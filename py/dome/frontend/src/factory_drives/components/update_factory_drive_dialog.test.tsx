// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {submit} from 'redux-form';
import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';

jest.mock('@common/components/file_upload_dialog', () => (props: any) => (
  <div data-testid="file-upload-dialog">
    {props.open && (
      <>
        <h1>{props.title}</h1>
        <button onClick={props.onCancel}>Cancel</button>
        <button onClick={props.submitForm}>Submit Form Prop</button>
        {props.multiple ? (
          <button
            data-testid="simulate-multiple-submit"
            onClick={() =>
              props.onSubmit({
                files: {
                  length: 2,
                  item: (index: number) =>
                    new File(['content'], `test${index + 1}.bin`),
                  * [Symbol.iterator]() {
                    yield new File(['content'], 'test1.bin');
                    yield new File(['content'], 'test2.bin');
                  },
                },
              })
            }
          >
            Simulate Multiple Submit
          </button>
        ) : (
          <button
            data-testid="simulate-single-submit"
            onClick={() =>
              props.onSubmit({file: new File(['content'], 'test.bin')})
            }
          >
            Simulate Single Submit
          </button>
        )}
        {props.children}
      </>
    )}
  </div>
));
jest.mock('./update_factory_drive_form', () => () => (
  <div data-testid="update-factory-drive-form">Form Content</div>
));

import {startUpdateFactoryDrive} from '@app/factory_drives/actions';
import {UPDATE_FACTORY_DRIVE_FORM} from '@app/factory_drives/constants';
import formDialog from '@app/form_dialog';
import project from '@app/project';

jest.mock('../actions', () => ({
  startUpdateFactoryDrive: jest.fn(),
}));
jest.mock('redux-form', () => ({
  submit: jest.fn(),
}));
jest.mock('@app/project', () => ({
  selectors: {
    getCurrentProject: jest.fn(() => 'test-project'),
  },
}));

const mockIsFormVisible = jest.fn();
const mockGetFormPayload = jest.fn();

jest.mock('@app/form_dialog', () => ({
  selectors: {
    isFormVisibleFactory: jest.fn(() => mockIsFormVisible),
    getFormPayloadFactory: jest.fn(() => mockGetFormPayload),
  },
  actions: {
    closeForm: jest.fn(() => ({type: 'MOCK_CLOSE_FORM'})),
  },
}));

import UpdateFactoryDriveDialog from './update_factory_drive_dialog';

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

/**
 * UpdateFactoryDriveDialog component test.
 */
describe('UpdateFactoryDriveDialog', () => {
  let store: any;
  const mockStartUpdate = startUpdateFactoryDrive as jest.Mock;
  const mockSubmit = submit as jest.Mock;
  const mockCloseForm = formDialog.actions.closeForm as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();

    mockIsFormVisible.mockReturnValue(true);
    mockGetFormPayload.mockReturnValue({
      multiple: false,
      id: null,
      dirId: 'dir123',
      name: '',
    });
    (project.selectors.getCurrentProject as jest.Mock)
      .mockReturnValue('test-project');

    store = mockStore({});
    store.dispatch = jest.fn();
  });

  const renderComponent = () =>
    render(
      <Provider store={store}>
        <UpdateFactoryDriveDialog />
      </Provider>,
    );

  test('renders FileUploadDialog with correct props when open', () => {
    renderComponent();
    expect(screen.getByTestId('file-upload-dialog')).toBeInTheDocument();
    expect(screen.getByText('Update Factory Drive')).toBeInTheDocument();
    expect(screen.getByTestId('update-factory-drive-form')).toBeInTheDocument();
  });

  test('does not render dialog content when not open', () => {
    mockIsFormVisible.mockReturnValue(false);
    renderComponent();
    expect(screen.queryByText('Update Factory Drive')).not.toBeInTheDocument();
  });

  test('calls cancelUpdate (closeForm) when cancel button is clicked', () => {
    renderComponent();
    fireEvent.click(screen.getByText('Cancel'));
    expect(mockCloseForm).toHaveBeenCalledWith(UPDATE_FACTORY_DRIVE_FORM);
    expect(store.dispatch).toHaveBeenCalledWith({type: 'MOCK_CLOSE_FORM'});
  });

  test('calls submitForm when submit button prop is called', () => {
    renderComponent();
    fireEvent.click(screen.getByText('Submit Form Prop'));
    expect(mockSubmit).toHaveBeenCalledWith(UPDATE_FACTORY_DRIVE_FORM);
  });

  describe('Single File Upload', () => {
    test('handles submit with new file (no id)', () => {
      renderComponent();
      fireEvent.click(screen.getByTestId('simulate-single-submit'));

      expect(mockStartUpdate).toHaveBeenCalledTimes(1);
      expect(mockStartUpdate).toHaveBeenCalledWith({
        project: 'test-project',
        id: null,
        dirId: 'dir123',
        name: 'test.bin',
        file: expect.any(File),
      });
      const fileArg = mockStartUpdate.mock.calls[0][0].file;
      expect(fileArg.name).toBe('test.bin');
    });

    test('handles submit with existing file (with id)', () => {
      mockGetFormPayload.mockReturnValue({
        multiple: false,
        id: 'file123',
        dirId: 'dirAABB',
        name: 'existing.bin',
      });
      renderComponent();
      fireEvent.click(screen.getByTestId('simulate-single-submit'));

      expect(mockStartUpdate).toHaveBeenCalledTimes(1);
      expect(mockStartUpdate).toHaveBeenCalledWith({
        project: 'test-project',
        id: 'file123',
        dirId: 'dirAABB',
        name: 'existing.bin',
        file: expect.any(File),
      });
    });
  });

  describe('Multiple File Upload', () => {
    beforeEach(() => {
      mockGetFormPayload.mockReturnValue({
        multiple: true,
        id: null,
        dirId: 'dir456',
      });
    });

    test('handles submit with multiple files', () => {
      renderComponent();
      fireEvent.click(screen.getByTestId('simulate-multiple-submit'));

      expect(mockStartUpdate).toHaveBeenCalledTimes(2);
      expect(mockStartUpdate).toHaveBeenCalledWith({
        project: 'test-project',
        id: null,
        dirId: 'dir456',
        name: 'test1.bin',
        file: expect.any(File),
      });
      expect(mockStartUpdate).toHaveBeenCalledWith({
        project: 'test-project',
        id: null,
        dirId: 'dir456',
        name: 'test2.bin',
        file: expect.any(File),
      });

      const fileArg1 = mockStartUpdate.mock.calls[0][0].file;
      expect(fileArg1.name).toBe('test1.bin');
      const fileArg2 = mockStartUpdate.mock.calls[1][0].file;
      expect(fileArg2.name).toBe('test2.bin');
    });
  });
});
