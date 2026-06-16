// Copyright 2026 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {submit} from 'redux-form';
import configureMockStore from 'redux-mock-store';

import formDialog from '@app/form_dialog';

import {DELETE_FACTORY_DRIVE_FORM} from '../constants';

import DeleteFactoryDriveForm from './delete_factory_drive_form';

// Mock for the function returned by the getFormPayloadFactory
const mockPayload = {id: 123, name: 'test_drive'};

// Mock dependencies
jest.mock('@app/form_dialog', () => ({
  selectors: {
    isFormVisibleFactory: jest.fn(() => jest.fn(() => true)),
    getFormPayloadFactory: jest.fn(() => jest.fn(() => mockPayload)),
  },
  actions: {
    closeForm: jest.fn((formName) =>
      ({type: 'MOCK_CLOSE_FORM', payload: formName})),
  },
}));

jest.mock('../actions', () => ({
  deleteFactoryDrive: jest.fn((values) =>
    ({type: 'MOCK_DELETE_FACTORY_DRIVE', payload: values})),
}));

jest.mock('redux-form', () => ({
  ...jest.requireActual('redux-form'),
  submit: jest.fn((formName) => ({type: 'MOCK_SUBMIT', payload: formName})),
}));

const mockStore = configureMockStore([]);

/**
 * DeleteFactoryDriveForm component test.
 */
describe('DeleteFactoryDriveForm', () => {
  let store: any;

  beforeEach(() => {
    jest.clearAllMocks();

    store = mockStore({
      app: {
        display: {
          form: {
            [DELETE_FACTORY_DRIVE_FORM]: {
              values: {},
              syncErrors: {},
            },
          },
          project: {
            currentProject: 'test-project',
          },
        },
      },
    });
    store.dispatch = jest.fn(store.dispatch);
  });

  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <DeleteFactoryDriveForm />
      </Provider>,
    );
  };

  test('renders the dialog with title, text, and buttons', () => {
    renderComponent();

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Delete Factory Drive')).toBeInTheDocument();
    expect(screen.getByText('Delete all versions of this file'))
      .toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Delete'})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Cancel'})).toBeInTheDocument();
  });

  test('dispatches submit action when Delete button is clicked', () => {
    renderComponent();
    const deleteButton = screen.getByRole('button', {name: 'Delete'});

    fireEvent.click(deleteButton);

    expect(submit).toHaveBeenCalledWith(DELETE_FACTORY_DRIVE_FORM);
  });

  test('dispatches cancel action when Cancel button is clicked', () => {
    renderComponent();
    const cancelButton = screen.getByRole('button', {name: 'Cancel'});

    fireEvent.click(cancelButton);

    const storeActions = store.getActions();
    expect(storeActions)
      .toContainEqual(formDialog.actions.closeForm(DELETE_FACTORY_DRIVE_FORM));
    expect(formDialog.actions.closeForm)
      .toHaveBeenCalledWith(DELETE_FACTORY_DRIVE_FORM);
  });
});
