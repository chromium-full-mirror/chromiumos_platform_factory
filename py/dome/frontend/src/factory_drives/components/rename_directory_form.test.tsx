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

import {RENAME_DIRECTORY_FORM} from '@app/factory_drives/constants';
import formDialog from '@app/form_dialog';
import {RootState} from '@app/types';

import RenameDirectoryForm from './rename_directory_form';

// Mock the actions and constants
jest.mock('../actions', () => ({
  startRenameDirectory: jest.fn(),
}));
jest.mock('@app/form_dialog', () => ({
  actions: {
    closeForm: jest.fn((formName) => ({type: 'CLOSE_FORM', payload: formName})),
  },
  selectors: {
    isFormVisibleFactory: (formName: string) => (state: any) =>
      state.app.display.formDialog[formName]?.visible || false,
    getFormPayloadFactory: (formName: string) => (state: any) =>
      state.app.display.formDialog[formName]?.payload,
  },
}));
// Mock Redux Form's submit action creator
jest.mock('redux-form', () => ({
  ...jest.requireActual('redux-form'),
  submit: jest.fn((formName) => ({type: 'SUBMIT_FORM', payload: formName})),
}));

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

/**
 * RenameDirectoryForm component test.
 */
describe('RenameDirectoryForm', () => {
  const initialPayload = {id: 'dir123', name: 'old_name'};

  const renderComponent = (storeState: Partial<RootState>) => {
    const store = mockStore({
      app: {
        display: {
          formDialog: {
            [RENAME_DIRECTORY_FORM]: {
              visible: true,
              payload: initialPayload,
            },
          },
          project: {
            currentProject: 'test-proj',
          },
          form: {},
        },
      },
      ...storeState,
    } as RootState);

    // Spy on dispatch
    jest.spyOn(store, 'dispatch');

    return render(
      <Provider store={store}>
        <RenameDirectoryForm />
      </Provider>,
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders the dialog with initial values when open', () => {
    renderComponent({});

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Rename Directory')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Rename'})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Cancel'})).toBeInTheDocument();
  });

  test('does not render the dialog when not open', () => {
    renderComponent({
      app: {
        display: {
          formDialog: {
            [RENAME_DIRECTORY_FORM]: {
              visible: false,
              payload: initialPayload,
            },
          },
          project: {currentProject: 'test-proj'},
          form: {},
        },
      },
    } as unknown as RootState);

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  test('dispatches closeForm action when Cancel button is clicked', () => {
    renderComponent({
      app: {
        display: {
          formDialog: {
            [RENAME_DIRECTORY_FORM]: {
              visible: true,
              payload: initialPayload,
            },
          },
          project: {currentProject: 'test-proj'},
          form: {},
        },
      },
    } as unknown as RootState);

    fireEvent.click(screen.getByRole('button', {name: 'Cancel'}));

    expect(formDialog.actions.closeForm)
      .toHaveBeenCalledWith(RENAME_DIRECTORY_FORM);
  });

  test('dispatches submit action when Rename button is clicked', () => {
    renderComponent({
      app: {
        display: {
          formDialog: {
            [RENAME_DIRECTORY_FORM]: {
              visible: true,
              payload: initialPayload,
            },
          },
          project: {currentProject: 'test-proj'},
          form: {},
        },
      },
    } as unknown as RootState);

    fireEvent.click(screen.getByRole('button', {name: 'Rename'}));

    expect(submit).toHaveBeenCalledWith(RENAME_DIRECTORY_FORM);
  });
});
