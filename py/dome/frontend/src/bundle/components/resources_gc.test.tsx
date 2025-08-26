// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {Store} from 'redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import * as actions from '@app/bundle/actions';
import * as selectors from '@app/bundle/selectors';
import {RootState} from '@app/types';

import ResourcesGarbageCollectionButton from './resources_gc';

// Mock Material UI Icons to avoid rendering issues and keep tests light.
jest.mock('@mui/icons-material/DeleteSweep', () =>
  () => <div data-testid="delete-sweep-icon">DeleteSweepIcon</div>,
);

// Mock the selectors and actions from their respective paths.
jest.mock('../selectors', () => ({
  getDeletedResources: jest.fn(),
}));
jest.mock('../actions', () => ({
  startResourcesGarbageCollection: jest.fn(() => ({type: 'MOCK_START_GC'})),
  closeGarbageCollectionSnackbar: jest.fn(() => ({
    type: 'MOCK_CLOSE_SNACKBAR',
  })),
}));

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

// Type cast the mocked functions
const getDeletedResourcesMock = selectors.getDeletedResources as jest.Mock;
const startResourcesGarbageCollectionMock =
  actions.startResourcesGarbageCollection as jest.Mock;

/**
 * ResourcesGarbageCollectionButton component test.
 */
describe('ResourcesGarbageCollectionButton', () => {
  let store: Store;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Helper function to render the component with a specific Redux state
  const renderComponent = (initialState: Partial<RootState> = {}) => {
    store = mockStore(initialState as RootState);
    jest.spyOn(store, 'dispatch');

    return render(
      <Provider store={store}>
        <ResourcesGarbageCollectionButton />
      </Provider>,
    );
  };

  test('should render the FAB button with the correct icon', () => {
    getDeletedResourcesMock.mockReturnValue(null);
    renderComponent();

    // Check if the button role is present
    expect(screen.getByRole('button')).toBeInTheDocument();
    // Check if the mock icon is rendered
    expect(screen.getByTestId('delete-sweep-icon')).toBeInTheDocument();
  });

  test('should not show Snackbar when no resources are deleted', () => {
    getDeletedResourcesMock.mockReturnValue(null);
    renderComponent();

    // Snackbar content should not be present
    expect(screen.queryByText(/Released space:/)).not.toBeInTheDocument();
  });

  describe('when resources are deleted', () => {
    const deletedResources = {
      size: 1500000, // 1.5 MB
      files: ['test-file1.tmp', 'test-file2.log'],
    };

    beforeEach(() => {
      getDeletedResourcesMock.mockReturnValue(deletedResources);
      renderComponent();
    });

    test('should show Snackbar with correct size and file list', () => {
      expect(screen.getByText('Released space: 1.50 MB')).toBeInTheDocument();
      expect(screen.getByText('test-file1.tmp')).toBeInTheDocument();
      expect(screen.getByText('test-file2.log')).toBeInTheDocument();
    });
  });

  test('should display byte sizes correctly in Snackbar', () => {
    // Test for KB
    getDeletedResourcesMock.mockReturnValue({size: 5000, files: []});
    renderComponent();
    expect(screen.getByText('Released space: 5.00 KB')).toBeInTheDocument();

    // Test for B
    const {unmount} = renderComponent();
    getDeletedResourcesMock.mockReturnValue({size: 100, files: []});
    unmount(); // Unmount before re-rendering
    renderComponent();
    expect(screen.getByText('Released space: 100.00 B')).toBeInTheDocument();

    // Test for GB
    unmount();
    getDeletedResourcesMock.mockReturnValue({size: 2500000000, files: []});
    renderComponent();
    expect(screen.getByText('Released space: 2.50 GB')).toBeInTheDocument();
  });

  test('should dispatch startResourcesGarbageCollection action when \
    FAB is clicked',
  () => {
    getDeletedResourcesMock.mockReturnValue(null);
    renderComponent();

    const fabButton = screen.getByRole('button');
    fireEvent.click(fabButton);

    // Check if the mock action creator was called
    expect(startResourcesGarbageCollectionMock).toHaveBeenCalledTimes(1);
    // Check if the store dispatched the action
    expect(store.dispatch)
      .toHaveBeenCalledWith(actions.startResourcesGarbageCollection());
  });
});
