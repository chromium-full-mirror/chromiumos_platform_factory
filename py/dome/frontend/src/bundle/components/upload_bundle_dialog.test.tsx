// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

const mockIsFormVisible = jest.fn();
const mockCloseForm = jest.fn((formName) => ({
  type: 'MOCK_FORM_DIALOG_CLOSE',
  payload: formName,
}));
const mockGetCurrentProject = jest.fn();
const mockGetBundleNames = jest.fn();
const mockReduxFormSubmit = jest.fn((formName) => ({
  type: 'MOCK_REDUX_FORM_SUBMIT',
  payload: formName,
}));

// Mock for the function returned by the startUploadBundle action creator
const mockThunkAction = jest.fn();
const mockStartUploadBundle = jest.fn(() => mockThunkAction);

// Mock dependencies
jest.mock('../actions', () => ({
  startUploadBundle: mockStartUploadBundle,
}));
jest.mock('@app/form_dialog', () => ({
  selectors: {
    isFormVisibleFactory: jest.fn(() => mockIsFormVisible),
  },
  actions: {
    closeForm: mockCloseForm,
  },
}));
jest.mock('@app/project', () => ({
  selectors: {
    getCurrentProject: mockGetCurrentProject,
  },
}));
jest.mock('../selectors', () => ({
  getBundleNames: mockGetBundleNames,
}));
jest.mock('redux-form', () => ({
  submit: mockReduxFormSubmit,
}));

// Mock Child Components
const mockFileUploadDialog = jest.fn((props: any) => (
  <div data-testid="file-upload-dialog">
    <h1>{props.title}</h1>
    {props.open && (
      <>
        <button onClick={props.onCancel}>Cancel</button>
        <button
          onClick={() => props.onSubmit({
            name: 'test-name',
            note: 'test-note',
            file: new File(['mock content'], 'test.zip', {
              type: 'application/zip',
            }),
          })}
        >
          SimulateFormSubmit
        </button>
        <button onClick={props.submitForm}>TriggerReduxFormSubmit</button>
        {props.children}
      </>
    )}
  </div>
));
jest.mock('@common/components/file_upload_dialog', () => mockFileUploadDialog);

jest.mock('./upload_bundle_form', () => (props: any) => (
  <div data-testid="upload-bundle-form">
    Mock UploadBundleForm (Bundle Names: {props.bundleNames.join(', ')})
  </div>
));

import UploadBundleDialog from '@app/bundle/components/upload_bundle_dialog';
import {UPLOAD_BUNDLE_FORM} from '@app/bundle/constants';
import {RootState} from '@app/types';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

/**
 * UploadBundleDialog component test.
 */
describe('UploadBundleDialog', () => {
  let store: any;
  const initialState: RootState = {} as unknown as RootState;

  beforeEach(() => {
    store = mockStore(initialState);

    jest.clearAllMocks();

    mockIsFormVisible.mockReturnValue(true);
    mockGetCurrentProject.mockReturnValue('test-project-id');
    mockGetBundleNames.mockReturnValue([
      'existing-bundle1',
      'existing-bundle2',
    ]);
  });

  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <UploadBundleDialog />
      </Provider>,
    );
  };

  test('should render FileUploadDialog with title when open is true', () => {
    renderComponent();
    expect(screen.getByTestId('file-upload-dialog')).toBeInTheDocument();
    expect(
      screen.getByRole('heading', {name: 'Upload Bundle'}),
    ).toBeInTheDocument();
    expect(mockFileUploadDialog).toHaveBeenCalledWith(
      expect.objectContaining({
        open: true,
        title: 'Upload Bundle',
      }),
      expect.anything(),
    );
  });

  test('should not display dialog content when open is false', () => {
    mockIsFormVisible.mockReturnValue(false);
    renderComponent();
    expect(screen.queryByText('Cancel')).not.toBeInTheDocument();
    expect(screen.queryByTestId('upload-bundle-form')).not.toBeInTheDocument();
    expect(mockFileUploadDialog).toHaveBeenCalledWith(
      expect.objectContaining({
        open: false,
      }),
      expect.anything(),
    );
  });

  test('should pass bundleNames to UploadBundleForm', () => {
    renderComponent();
    expect(screen.getByTestId('upload-bundle-form'))
      .toHaveTextContent('existing-bundle1, existing-bundle2');
  });

  test('should dispatch closeForm action when Cancel button is clicked', () => {
    renderComponent();
    fireEvent.click(screen.getByText('Cancel'));

    // Check that the action creator was called with the correct form name
    expect(mockCloseForm).toHaveBeenCalledWith(UPLOAD_BUNDLE_FORM);

    // Check that the store dispatched the object returned by the mockCloseForm
    const expectedAction = {
      type: 'MOCK_FORM_DIALOG_CLOSE',
      payload: UPLOAD_BUNDLE_FORM,
    };
    expect(store.getActions()).toContainEqual(expectedAction);
  });

  test('should dispatch redux-form submit action when \
    TriggerReduxFormSubmit button is clicked',
  () => {
    renderComponent();
    fireEvent.click(screen.getByText('TriggerReduxFormSubmit'));

    // Check that the action creator was called with the correct form name
    expect(mockReduxFormSubmit).toHaveBeenCalledWith(UPLOAD_BUNDLE_FORM);

    const expectedAction = {
      type: 'MOCK_REDUX_FORM_SUBMIT',
      payload: UPLOAD_BUNDLE_FORM,
    };
    expect(store.getActions()).toContainEqual(expectedAction);
  });

  test('should dispatch the thunk action on form submit', () => {
    renderComponent();
    fireEvent.click(screen.getByText('SimulateFormSubmit'));

    const expectedFile = new File(['mock content'], 'test.zip', {
      type: 'application/zip',
    });

    // Check if the action creator factory (startUploadBundle) was called
    // with the correct arguments.
    expect(mockStartUploadBundle).toHaveBeenCalledTimes(1);
    expect(mockStartUploadBundle).toHaveBeenCalledWith({
      project: 'test-project-id',
      name: 'test-name',
      note: 'test-note',
      bundleFile: expectedFile,
    });
  });
});
