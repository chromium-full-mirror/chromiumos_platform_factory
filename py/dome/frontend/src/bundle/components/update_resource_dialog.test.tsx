// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import dateFormat from 'dateformat';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore, Store} from 'redux';
import {reducer as formReducer} from 'redux-form';

// Mock external modules
jest.mock('dateformat');

// Mock React Components
jest.mock('./update_resource_form', () => ({
  __esModule: true,
  default: jest.fn(),
}));
jest.mock('@common/components/file_upload_dialog', () => ({
  __esModule: true,
  default: jest.fn(),
}));

// Mock actions and selectors
jest.mock('@app/bundle/actions');
jest.mock('@app/form_dialog/actions');

const mockIsFormVisibleSelector = jest.fn();
const mockGetFormPayloadSelector = jest.fn();
jest.mock('@app/form_dialog/selectors', () => ({
  isFormVisibleFactory: jest.fn(() => mockIsFormVisibleSelector),
  getFormPayloadFactory: jest.fn(() => mockGetFormPayloadSelector),
}));

jest.mock('@app/project/selectors');
jest.mock('../selectors');
jest.mock('redux-form', () => ({
  ...jest.requireActual('redux-form'),
  submit: jest.fn(),
  reducer: jest.requireActual('redux-form').reducer,
}));

// Import the component and dependencies AFTER mocks are set up
import {submit} from 'redux-form';

import UpdateResourceForm from '@app/bundle/components/update_resource_form';
import {UpdateResourceFormPayload} from '@app/bundle/types';
import * as projectSelectors from '@app/project/selectors';
import FileUploadDialog from '@common/components/file_upload_dialog';

import UpdateResourceDialog from './update_resource_dialog';

// Type safety for mocked functions
const mockedDateFormat = dateFormat as jest.MockedFunction<typeof dateFormat>;
const MockedFileUploadDialog = FileUploadDialog as unknown as jest.Mock;
const MockedUpdateResourceForm = UpdateResourceForm as jest.Mock;
const mockedSubmit = submit as jest.MockedFunction<typeof submit>;

const mockedGetCurrentProject = projectSelectors.getCurrentProject as jest.Mock;

// Default mock payload
const DEFAULT_PAYLOAD: UpdateResourceFormPayload = {
  bundleName: 'default-bundle',
  resourceType: 'default-type',
  resourceKey: 'default-key',
};

/**
 * UpdateResourceDialog component test.
 */
describe('UpdateResourceDialog', () => {
  const mockDateString = '20251106123000';
  let store: Store;

  beforeEach(() => {
    jest.clearAllMocks();

    mockedDateFormat.mockReturnValue(mockDateString);

    MockedUpdateResourceForm.mockImplementation((props: any) => (
      <div data-testid="update-resource-form">
        Mock Form - initialName: {props.initialValues?.name}
      </div>
    ));

    MockedFileUploadDialog.mockImplementation((props: any) => (
      <div data-testid="file-upload-dialog">
        <h1>{props.title}</h1>
        {props.children}
        <button onClick={props.onCancel}>Cancel</button>
        <button onClick={props.submitForm}>SubmitForm</button>
        <button
          onClick={() => props.onSubmit({
            name: 'simulated-new-name',
            note: 'simulated note',
            file: new File(['content'], 'test.bin', {
              type: 'application/octet-stream',
            }),
          })}
        >
          SimulateDialogSubmit
        </button>
      </div>
    ));

    // Default return values for the selectors
    mockIsFormVisibleSelector.mockReturnValue(false);
    mockGetFormPayloadSelector.mockReturnValue(DEFAULT_PAYLOAD);
    mockedGetCurrentProject.mockReturnValue('test-project');
    mockedSubmit.mockReturnValue({type: 'TEST_SUBMIT'});

    store = createStore(combineReducers({form: formReducer}));
    jest.spyOn(store, 'dispatch')
      .mockImplementation(() => ({type: 'MOCKED_DISPATCH'}));
  });

  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <UpdateResourceDialog />
      </Provider>,
    );
  };

  test('renders FileUploadDialog with correct base props when open', () => {
    mockIsFormVisibleSelector.mockReturnValue(true);
    renderComponent();
    expect(MockedFileUploadDialog).toHaveBeenCalledWith(
      expect.objectContaining({
        open: true,
        title: 'Update Resource',
      }),
      {},
    );
    expect(screen.getByText('Update Resource')).toBeInTheDocument();
  });

  describe('initialValues generation for UpdateResourceForm', () => {
    const basePayload = {
      resourceType: 'firmware',
      resourceKey: 'someResourceKey',
    };
    const expectedNote = 'Updated "firmware" type resource';

    beforeEach(() => {
      mockIsFormVisibleSelector.mockReturnValue(true);
    });

    test('generates correct initialValues with timestamp format', () => {
      mockGetFormPayloadSelector.mockReturnValue({
        ...basePayload,
        bundleName: 'test-bundle-20240101000000',
      });
      renderComponent();
      expect(MockedUpdateResourceForm)
        .toHaveBeenCalledWith(expect.objectContaining({
          initialValues: {
            name: `test-bundle-${mockDateString}`,
            note: expectedNote,
          },
        }), {});
    });

    test('generates correct initialValues for "empty" bundleName', () => {
      mockedGetCurrentProject.mockReturnValue('my-proj');
      mockGetFormPayloadSelector.mockReturnValue({
        ...basePayload,
        bundleName: 'empty',
      });
      renderComponent();
      const expectedName = `my-proj-${mockDateString}`;
      expect(MockedUpdateResourceForm).toHaveBeenCalledWith(
        expect.objectContaining({
          initialValues: {
            name: expectedName,
            note: expectedNote,
          },
        }),
        {},
      );
    });

    test('generates correct initialValues for other bundleName', () => {
      mockGetFormPayloadSelector.mockReturnValue({
        ...basePayload,
        bundleName: 'other-bundle',
      });
      renderComponent();
      const expectedName = `other-bundle-${mockDateString}`;
      expect(MockedUpdateResourceForm).toHaveBeenCalledWith(
        expect.objectContaining({
          initialValues: {
            name: expectedName,
            note: expectedNote,
          },
        }),
        {},
      );
    });
  });
});
