// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Mock Child Components
jest.mock('@app/auth/components/login_app', () => () => (
  <div data-testid="login-app">LoginApp</div>
));
jest.mock('@app/project/components/projects_app', () => () => (
  <div data-testid="projects-app">ProjectsApp</div>
));
jest.mock('@app/config/components/config_app', () => () => (
  <div data-testid="config-app">ConfigApp</div>
));
jest.mock('@app/dashboard/components/dashboard_app', () => () => (
  <div data-testid="dashboard-app">DashboardApp</div>
));
jest.mock('@app/bundle/components/bundles_app', () => () => (
  <div data-testid="bundles-app">BundlesApp</div>
));
jest.mock('@app/factory_drives/components/factory_drive_app', () => () => (
  <div data-testid="factory-drive-app">FactoryDriveApp</div>
));
jest.mock('@app/log/components/log_app', () => () => (
  <div data-testid="log-app">LogApp</div>
));
jest.mock('@app/sync_status/components/sync_status_app', () => () => (
  <div data-testid="sync-status-app">SyncStatusApp</div>
));

// Mock other components rendered directly by DomeApp
jest.mock('./dome_app_bar', () => (
  {toggleAppMenu}: {toggleAppMenu: () => void},
) => (
  <button aria-label="Toggle Menu" onClick={toggleAppMenu}>Toggle</button>
));
const MockDomeAppMenu = ({open}: {open: boolean}) => (
  <div data-testid="dome-app-menu" data-open={open}>Menu</div>
);
jest.mock('./dome_app_menu', () => MockDomeAppMenu);
jest.mock('@app/error/components/error_dialog', () => () => (
  <div>ErrorDialog</div>
));
jest.mock('@app/task/components/task_list', () => () => <div>TaskList</div>);
jest.mock('./dome_app_version_alert', () => () => <div>VersionAlert</div>);

// Mock the fetchDomeInfo action
const mockFetchDomeInfo = jest.fn();
jest.mock('@app/dome_app/actions', () => ({
  __esModule: true,
  fetchDomeInfo: mockFetchDomeInfo,
}));

import DomeApp from '@app/dome_app/components/dome_app';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

/**
 * DomeApp component test.
 */
describe('DomeApp', () => {
  beforeEach(() => {
    window.alert = jest.fn();
    mockFetchDomeInfo.mockClear();
    mockFetchDomeInfo.mockReturnValue(() => Promise.resolve());
  });

  const renderComponent = (authProps: any = {}, domeAppProps: any = {}) => {
    if (Object.keys(authProps).length === 0) {
      authProps = {
        isLoggedIn: true,
      };
    }
    if (Object.keys(domeAppProps).length === 0) {
      domeAppProps = {
        currentApp: 'PROJECTS_APP',
        domeInfo: {
          dockerImageGithash: '*ba23356901533c6c904bdbeb516dfc3dbcf32dd9',
          dockerImageIslocal: true,
          dockerImageTimestamp: '20251105171457',
          dockerImageLatestVersion: '',
          isDevServer: false,
        },
      };
    }
    const theme = createTheme();
    const store = mockStore({
      app: {
        display: {
          auth: authProps,
          domeApp: domeAppProps,
        },
      },
    } as unknown as RootState);
    return render(
      <ThemeProvider theme={theme}>
        <Provider store={store}>
          <DomeApp />
        </Provider>
      </ThemeProvider>,
    );
  };

  test('should call fetchDomeInfo on mount', () => {
    renderComponent();
    expect(mockFetchDomeInfo).toHaveBeenCalledTimes(1);
  });

  test('should show alert if not Chrome', () => {
    const originalUserAgent = navigator.userAgent;
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Firefox',
      configurable: true,
    });

    renderComponent();
    expect(window.alert).toHaveBeenCalledWith(expect.stringContaining(
      'To visit Dome, please use Chrome/Chromium to avoid unnecessary issues.',
    ));

    Object.defineProperty(navigator, 'userAgent', {
      value: originalUserAgent,
      configurable: true,
    });
  });

  test('renders LoginApp when not logged in', () => {
    renderComponent({isLoggedIn: false});
    expect(screen.getByTestId('login-app')).toBeInTheDocument();
  });

  test('renders ProjectsApp when logged in and appName is PROJECTS_APP', () => {
    renderComponent({isLoggedIn: true}, {currentApp: 'PROJECTS_APP'});
    expect(screen.getByTestId('projects-app')).toBeInTheDocument();
  });

  test('renders ConfigApp when logged in and appName is CONFIG_APP', () => {
    renderComponent({isLoggedIn: true}, {currentApp: 'CONFIG_APP'});
    expect(screen.getByTestId('config-app')).toBeInTheDocument();
  });

  test('renders DashboardApp when logged in and appName \
    is DASHBOARD_APP',
  () => {
    renderComponent({isLoggedIn: true}, {currentApp: 'DASHBOARD_APP'});
    expect(screen.getByTestId('dashboard-app')).toBeInTheDocument();
  });

  test('renders BundlesApp when logged in and appName is BUNDLES_APP', () => {
    renderComponent({isLoggedIn: true}, {currentApp: 'BUNDLES_APP'});
    expect(screen.getByTestId('bundles-app')).toBeInTheDocument();
  });

  test('renders FactoryDriveApp when logged in and appName \
    is FACTORY_DRIVE_APP',
  () => {
    renderComponent({isLoggedIn: true}, {currentApp: 'FACTORY_DRIVE_APP'});
    expect(screen.getByTestId('factory-drive-app')).toBeInTheDocument();
  });

  test('renders LogApp when logged in and appName is LOG_APP', () => {
    renderComponent({isLoggedIn: true}, {currentApp: 'LOG_APP'});
    expect(screen.getByTestId('log-app')).toBeInTheDocument();
  });

  test('renders SyncStatusApp when logged in and appName \
    is SYNC_STATUS_APP',
  () => {
    renderComponent({isLoggedIn: true}, {currentApp: 'SYNC_STATUS_APP'});
    expect(screen.getByTestId('sync-status-app')).toBeInTheDocument();
  });
});
