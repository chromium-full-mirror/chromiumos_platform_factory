// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom'; // Provides additional matchers
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

// Mock child components to isolate tests
jest.mock('@app/service/components/service_list', () => () => (
  <div>Mocked ServiceList</div>
));

// Mock for EnableUmpireForm to test props and callbacks
const MockEnableUmpireForm = jest.fn(() => <div>Mocked EnableUmpireForm</div>);
jest.mock('./enable_umpire_form', () => (props: any) => {
  MockEnableUmpireForm();
  return <div>Mocked EnableUmpireForm</div>;
});

// Mock actions and selectors
const mockFetchPorts = jest.fn();
const mockDisableUmpire = jest.fn();
const mockRemoveProjectPort = jest.fn();
jest.mock('../actions', () => ({
  fetchPorts: mockFetchPorts,
  disableUmpire: mockDisableUmpire,
  removeProjectPort: mockRemoveProjectPort,
}));

import DashboardApp from '@app/dashboard/components/dashboard_app';
import {RootState} from '@app/types';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

/**
 * DashboardApp component test.
 */
describe('DashboardApp', () => {
  beforeEach(() => {
    // Reset mocks
    MockEnableUmpireForm.mockClear();
  });

  const renderComponent = (projectProps: any = {}) => {
    if (Object.keys(projectProps).length === 0) {
      projectProps = {
        currentProject: 'test-project',
        projects: {
          'test-project': {
            name: 'test-project',
            hasExistingUmpire: true,
            umpireEnabled: true,
            umpirePort: 9250,
            netbootBundle: null,
            isAndroid: false,
            umpireReady: true,
          },
        },
      };
    }
    const initialState = {
      app: {
        display: {
          dashboard: {
            ports: [],
          },
          project: projectProps,
        },
      },
    } as unknown as RootState;
    const store = mockStore(initialState);
    store.dispatch = jest.fn();
    return render(
      <Provider store={store}>
        <DashboardApp />
      </Provider>,
    );
  };

  test('renders the dashboard title', () => {
    renderComponent();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  describe('when Umpire is disabled', () => {
    beforeEach(() => {
      renderComponent({
        currentProject: 'test-project',
        projects: {
          'test-project': {
            name: 'test-project',
            hasExistingUmpire: true,
            umpireEnabled: false,
            umpirePort: 9250,
            netbootBundle: null,
            isAndroid: false,
            umpireReady: true,
          },
        },
      });
    });

    test('shows the switch as unchecked', () => {
      expect(
        (screen.getByLabelText('Enable Umpire') as HTMLInputElement).checked,
      ).toBe(false);
    });

    test('does not show Umpire info or services', () => {
      expect(screen.queryByText('Info')).not.toBeInTheDocument();
      expect(screen.queryByText('Services')).not.toBeInTheDocument();
    });
  });

  describe('when Umpire is enabled and ready', () => {
    const umpireReadyProps: any = {
      currentProject: 'test-project',
      projects: {
        'test-project': {
          name: 'test-project',
          hasExistingUmpire: true,
          umpireEnabled: true,
          umpirePort: 12345,
          netbootBundle: null,
          isAndroid: false,
          umpireReady: true,
        },
      },
    };

    test('shows the switch as checked', () => {
      renderComponent(umpireReadyProps);
      expect(
        (screen.getByLabelText('Enable Umpire') as HTMLInputElement).checked,
      ).toBe(true);
    });

    test('shows Umpire info and services', () => {
      renderComponent(umpireReadyProps);
      expect(screen.getByText('Info')).toBeInTheDocument();
      expect(screen.getByText('port: 12345')).toBeInTheDocument();
      expect(screen.getByText('Services')).toBeInTheDocument();
      expect(screen.getByText('Mocked ServiceList')).toBeInTheDocument();
    });

    test('calls disableUmpire and removeProjectPort when \
      switch is toggled',
    () => {
      renderComponent(umpireReadyProps);
      const switchInput = screen.getByLabelText('Enable Umpire');
      fireEvent.click(switchInput);

      expect(mockDisableUmpire).toHaveBeenCalledWith('test-project');
      expect(mockRemoveProjectPort).toHaveBeenCalledWith([], 'test-project');
    });
  });
});
