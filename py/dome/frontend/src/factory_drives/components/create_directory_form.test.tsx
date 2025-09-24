// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {submit} from 'redux-form';
import configureMockStore from 'redux-mock-store';

import {CREATE_DIRECTORY_FORM} from '@app/factory_drives/constants';
import formDialog from '@app/form_dialog';

import CreateDirectoryForm from './create_directory_form';

// Mock the dependencies
jest.mock('@app/form_dialog', () => ({
  selectors: {
    isFormVisibleFactory: jest.fn(() => jest.fn(() => true)),
  },
  actions: {
    closeForm: jest.fn((formName) =>
      ({type: 'MOCK_CLOSE_FORM', payload: formName})),
  },
}));

jest.mock('../actions', () => ({
  startCreateDirectory: jest.fn((values) =>
    ({type: 'MOCK_START_CREATE_DIRECTORY', payload: values})),
}));

jest.mock('redux-form', () => ({
  ...jest.requireActual('redux-form'),
  submit: jest.fn((formName) => ({type: 'MOCK_SUBMIT', payload: formName})),
}));

const mockStore = configureMockStore([]);

/**
 * CreateDirectoryForm component test.
 */
describe('CreateDirectoryForm', () => {
  let store: any;
  const dirId = 123;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup mock store
    store = mockStore({
      app: {
        display: {
          form: {
            [CREATE_DIRECTORY_FORM]: {
              values: {},
              syncErrors: {},
            },
          },
          project: {},
        },
      },
    });
    store.dispatch = jest.fn(store.dispatch);
  });

  const renderComponent = (props = {dirId}) => {
    return render(
      <Provider store={store}>
        <CreateDirectoryForm {...props} />
      </Provider>,
    );
  };

  test('renders the dialog with title and buttons', () => {
    renderComponent();

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Create Directory')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Create'})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Cancel'})).toBeInTheDocument();
    expect(screen.getByLabelText('name')).toBeInTheDocument();
  });

  test('shows validation error for invalid directory name', async () => {
    renderComponent();
    const nameInput = screen.getByLabelText('name');
    const createButton = screen.getByRole('button', {name: 'Create'});

    fireEvent.change(nameInput, {target: {value: 'Invalid Folder Name'}});
    fireEvent.click(createButton);

    expect(submit).toHaveBeenCalledWith(CREATE_DIRECTORY_FORM);
  });

  test('dispatches submit action when Create button is clicked', () => {
    renderComponent();
    const createButton = screen.getByRole('button', {name: 'Create'});

    fireEvent.click(createButton);

    expect(submit).toHaveBeenCalledWith(CREATE_DIRECTORY_FORM);
  });

  test('dispatches cancel action when Cancel button is clicked', () => {
    renderComponent();
    const cancelButton = screen.getByRole('button', {name: 'Cancel'});

    fireEvent.click(cancelButton);

    const actions = store.getActions();
    expect(actions)
      .toContainEqual(formDialog.actions.closeForm(CREATE_DIRECTORY_FORM));
    expect(formDialog.actions.closeForm)
      .toHaveBeenCalledWith(CREATE_DIRECTORY_FORM);
  });
});
