// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import FactoryDriveApp from '@app/factory_drives/components/factory_drive_app';
import {
  CREATE_DIRECTORY_FORM,
  UPDATE_FACTORY_DRIVE_FORM,
} from '@app/factory_drives/constants';
import formDialog from '@app/form_dialog';

// Mock dependencies
jest.mock('@app/form_dialog', () => ({
  actions: {
    openForm: jest.fn(() => ({type: 'OPEN_FORM_MOCK'})),
  },
}));

// Mock child components
jest.mock('./update_factory_drive_dialog', () => () => (
  <div>UpdateFactoryDriveDialogMock</div>
));
jest.mock('./create_directory_form', () => ({dirId}: any) => (
  <div data-testid="create-directory-form">
    CreateDirectoryFormMock - dirId: {String(dirId)}
  </div>
));

// Mock FactoryDriveList and provide a way to trigger dirClicked
const mockDirClicked = jest.fn();
jest.mock('./factory_drive_list', () => ({currentDirId, dirClicked}: any) => {
  mockDirClicked.mockImplementation(dirClicked);
  return (
    <div data-testid="factory-drive-list" onClick={() => dirClicked(123)}>
      FactoryDriveListMock - currentDirId: {String(currentDirId)}
      <button onClick={() => dirClicked(456)}>Simulate Dir Click 456</button>
    </div>
  );
});

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore(middlewares);

/**
 * FactoryDriveApp component test.
 */
describe('FactoryDriveApp', () => {
  const renderComponent = () => {
    const store = mockStore({});
    return render(
      <Provider store={store}>
        <FactoryDriveApp />
      </Provider>,
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing and displays the title', () => {
    renderComponent();
    expect(screen.getByText('Factory Drive')).toBeInTheDocument();
    expect(
      screen.getByText('UpdateFactoryDriveDialogMock'),
    ).toBeInTheDocument();
  });

  test('initially renders child components with null currentDirId', () => {
    renderComponent();
    expect(
      screen.getByTestId('create-directory-form'),
    ).toHaveTextContent('dirId: null');
    expect(
      screen.getByTestId('factory-drive-list'),
    ).toHaveTextContent('currentDirId: null');
  });

  describe('Header Button Interactions', () => {
    test('dispatches openForm when "Create Files" button is clicked', () => {
      renderComponent();
      const createFilesButton = screen.getByRole('button', {
        name: /Create Files/i,
      });
      fireEvent.click(createFilesButton);

      expect(formDialog.actions.openForm).toHaveBeenCalledTimes(1);
      expect(formDialog.actions.openForm).toHaveBeenCalledWith(
        UPDATE_FACTORY_DRIVE_FORM,
        {id: null, dirId: null, name: 'unused_name', multiple: true},
      );
    });

    test('dispatches openForm when "Add directory" button is clicked', () => {
      renderComponent();
      const addDirectoryButton = screen.getByRole('button', {
        name: /Add directory/i,
      });
      fireEvent.click(addDirectoryButton);

      expect(formDialog.actions.openForm).toHaveBeenCalledTimes(1);
      expect(formDialog.actions.openForm)
        .toHaveBeenCalledWith(CREATE_DIRECTORY_FORM);
    });
  });

  test('uses the updated currentDirId in button actions after clicked', () => {
    renderComponent();

    // Simulate a directory click in the list
    const listMock = screen.getByTestId('factory-drive-list');
    fireEvent.click(listMock); // Sets currentDirId to 123

    // Now click the "Create Files" button
    const createFilesButton = screen.getByRole('button', {
      name: /Create Files/i,
    });
    fireEvent.click(createFilesButton);

    // Expect the action to be called with the new dirId
    expect(formDialog.actions.openForm).toHaveBeenCalledWith(
      UPDATE_FACTORY_DRIVE_FORM,
      {id: null, dirId: 123, name: 'unused_name', multiple: true},
    );
  });
});
