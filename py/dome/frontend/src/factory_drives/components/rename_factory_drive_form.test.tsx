// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import * as reduxForm from 'redux-form';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
  CREATE_DIRECTORY_FORM,
  RENAME_FACTORY_DRIVE_FORM,
  UPDATE_FACTORY_DRIVE_FORM,
} from '@app/factory_drives/constants';
import {RenameRequest} from '@app/factory_drives/types';
import * as formDialogActions from '@app/form_dialog/actions';
import * as formDialogSelectors from '@app/form_dialog/selectors';
import * as projectSelectors from '@app/project/selectors';
import {RootState} from '@app/root_reducer';

import RenameFactoryDriveForm from './rename_factory_drive_form';

interface MockState {
  open: boolean;
  payload: RenameRequest | null;
}

const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

/**
 * RenameFactoryDriveForm component test.
 */
describe('RenameFactoryDriveForm', () => {
  let store: any;
  const initialPayload: RenameRequest = {id: 1, name: 'Old Factory Name'};

  const renderHelper = (state: MockState) => {
    // Mock selector return values
    const mockIsFormVisible = jest.fn(() => state.open);
    const mockGetFormPayload = jest.fn(() => state.payload!);
    const mockGetCurrentProject = jest.fn(() => ('My Project'));

    // Mock factories to return the mock functions
    jest.spyOn(formDialogSelectors, 'isFormVisibleFactory')
      .mockReturnValue(mockIsFormVisible);
    jest.spyOn(formDialogSelectors, 'getFormPayloadFactory')
      .mockReturnValue(mockGetFormPayload);
    jest.spyOn(projectSelectors, 'getCurrentProject')
      .mockImplementation(mockGetCurrentProject);

    const initialState = {
      app: {
        display: {
          formDialog: {
            visibility: {
              [CREATE_DIRECTORY_FORM]: false,
              [RENAME_FACTORY_DRIVE_FORM]: true,
            },
            payload: {
              [RENAME_FACTORY_DRIVE_FORM]: initialPayload,
              [UPDATE_FACTORY_DRIVE_FORM]: {
                id: null,
                dirId: null,
                name: 'unused_name',
                multiple: true,
              },
            },
          },
        },
      },
    } as unknown as RootState;
    store = mockStore(initialState);
    jest.spyOn(store, 'dispatch').mockImplementation();

    return render(
      <Provider store={store}>
        <RenameFactoryDriveForm />
      </Provider>,
    );
  };

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('when dialog is open', () => {
    beforeEach(() => {
      renderHelper({open: true, payload: initialPayload});
    });

    test('should render dialog with title and initial from payload', () => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Rename Factory Drive')).toBeInTheDocument();

      const nameInput = screen.getByLabelText('name');
      expect(nameInput).toBeInTheDocument();
    });

    test('should dispatch closeForm action when Cancel is clicked', () => {
      const expectedAction = {type: 'MOCK_CLOSE_FORM_ACTION'} as any;
      jest.spyOn(formDialogActions, 'closeForm')
        .mockReturnValue(expectedAction);

      const cancelButton = screen.getByRole('button', {name: 'Cancel'});
      fireEvent.click(cancelButton);

      // Check that the action creator was called correctly
      expect(formDialogActions.closeForm)
        .toHaveBeenCalledWith(RENAME_FACTORY_DRIVE_FORM);
      // Check that the result of the action creator was dispatched
      expect(store.dispatch).toHaveBeenCalledWith(expectedAction);
    });

    test('should dispatch reduxForm.submit action \
      when Rename button is clicked',
    () => {
      const expectedAction = {type: 'MOCK_SUBMIT_FORM_ACTION'};
      jest.spyOn(reduxForm, 'submit').mockReturnValue(expectedAction);

      const renameButton = screen.getByRole('button', {name: 'Rename'});
      fireEvent.click(renameButton);

      // Check that the action creator was called correctly
      expect(reduxForm.submit).toHaveBeenCalledWith(RENAME_FACTORY_DRIVE_FORM);
      // Check that the result of the action creator was dispatched
      expect(store.dispatch).toHaveBeenCalledWith(expectedAction);
    });
  });
});
