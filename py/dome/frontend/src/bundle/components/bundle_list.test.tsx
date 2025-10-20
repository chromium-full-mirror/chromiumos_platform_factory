// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

// Mock actions and selectors
const mockFetchBundles = jest.fn(() => ({type: 'FETCH_BUNDLES_MOCK'}));
const mockReorderBundles = jest.fn((oldIndex, newIndex) => ({
  type: 'REORDER_BUNDLES_MOCK',
  payload: {oldIndex, newIndex},
}));
jest.mock('../actions', () => ({
  fetchBundles: mockFetchBundles,
  reorderBundles: mockReorderBundles,
}));

const mockGetBundles = jest.fn();
jest.mock('../selectors', () => ({
  getBundles: mockGetBundles,
}));

// Minimal Bundle type for the test
interface Bundle {
  name: string;
}

// Mock BundleComponent to avoid rendering its internals
jest.mock('./bundle_component', () => ({bundle}: {bundle: Bundle}) => (
  <div data-testid={`bundle-${bundle.name}`}>{bundle.name}</div>
));

// Mock react-sortable-hoc to capture props and simplify rendering
interface OnSortEndParams {
  oldIndex: number;
  newIndex: number;
}
type OnSortEndFunc = (params: OnSortEndParams) => void;
let capturedOnSortEnd: OnSortEndFunc | undefined;
jest.mock('react-sortable-hoc', () => ({
  SortableContainer:
    (WrappedComponent: React.ComponentType<any>) => (props: any) => {
      capturedOnSortEnd = props.onSortEnd;
      return (
        <div data-testid="mock-sortable-list">
          <WrappedComponent {...props} />
        </div>
      );
    },
  SortableElement:
    (WrappedComponent: React.ComponentType<any>) => (props: any) => (
      <div data-testid={`mock-sortable-item-${props.index}`}>
        <WrappedComponent {...props} />
      </div>
    ),
}));

import BundleList from '@app/bundle/components/bundle_list';
import {RootState} from '@app/types';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<Partial<RootState>>(middlewares);

/**
 * BundleList component test.
 */
describe('BundleList', () => {
  let store: any;
  const mockBundles: Bundle[] = [
    {name: 'BundleA'},
    {name: 'BundleB'},
    {name: 'BundleC'},
  ];

  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    mockGetBundles.mockReturnValue(mockBundles);

    // Create a new mock store instance
    store = mockStore({});
    // Spy on the store's dispatch function
    store.dispatch = jest.fn(store.dispatch);

    capturedOnSortEnd = undefined;
  });

  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <BundleList />
      </Provider>,
    );
  };

  test('should dispatch fetchBundles action on mount', () => {
    renderComponent();
    expect(mockFetchBundles).toHaveBeenCalledTimes(1);
    expect(store.dispatch).toHaveBeenCalledWith(mockFetchBundles());
  });

  test('should render the list of bundles from the store', () => {
    renderComponent();

    // Check that the mock container is rendered
    expect(screen.getByTestId('mock-sortable-list')).toBeInTheDocument();

    // Check that each bundle is rendered by the mock BundleComponent
    expect(screen.getByTestId('bundle-BundleA')).toHaveTextContent('BundleA');
    expect(screen.getByTestId('bundle-BundleB')).toHaveTextContent('BundleB');
    expect(screen.getByTestId('bundle-BundleC')).toHaveTextContent('BundleC');

    // Check that SortableElement mock wrapper is rendered for each item
    expect(screen.getByTestId('mock-sortable-item-0')).toBeInTheDocument();
    expect(screen.getByTestId('mock-sortable-item-1')).toBeInTheDocument();
    expect(screen.getByTestId('mock-sortable-item-2')).toBeInTheDocument();
  });

  describe('handleReorder (onSortEnd simulation)', () => {
    test('should dispatch reorderBundles action when \
      onSortEnd is called with different indices',
    () => {
      renderComponent();
      // Ensure the onSortEnd prop was captured by the mock SortableContainer
      expect(capturedOnSortEnd).toBeDefined();

      // Simulate the sort end event
      if (capturedOnSortEnd) {
        capturedOnSortEnd({oldIndex: 0, newIndex: 2});
      }

      // Verify the correct action was dispatched
      expect(mockReorderBundles).toHaveBeenCalledTimes(1);
      expect(mockReorderBundles).toHaveBeenCalledWith(0, 2);
      expect(store.dispatch).toHaveBeenCalledWith(mockReorderBundles(0, 2));
    });

    test('should NOT dispatch reorderBundles action when \
      onSortEnd is called with the same indices',
    () => {
      renderComponent();
      expect(capturedOnSortEnd).toBeDefined();

      // Simulate the sort end event with no change in index
      if (capturedOnSortEnd) {
        capturedOnSortEnd({oldIndex: 1, newIndex: 1});
      }

      // Verify the action was not dispatched
      expect(mockReorderBundles).not.toHaveBeenCalled();
      expect(store.dispatch).not.toHaveBeenCalledWith(expect.objectContaining({
        type: 'REORDER_BUNDLES_MOCK',
      }));
    });
  });
});
