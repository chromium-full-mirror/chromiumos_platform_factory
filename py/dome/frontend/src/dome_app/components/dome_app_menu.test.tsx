// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';

import auth from '@app/auth';
import DomeAppMenu from '@app/dome_app/components/dome_app_menu';
import project from '@app/project';
import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Mock dependencies
// Mock selectors
jest.mock('@app/auth', () => ({
  selectors: {
    isLoggedIn: jest.fn(),
  },
}));
jest.mock('@app/project', () => ({
  selectors: {
    getCurrentProjectObject: jest.fn(),
  },
}));

// Mock child component to inspect props
jest.mock('./dome_app_menu_item', () => (props: any) => (
  <li
    data-testid={`menuitem-${props.app}`}
    aria-disabled={props.disabled || false}
    className={props.className}
    onClick={props.onClick}
  >
    {props.children}
  </li>
));

const mockStore = configureStore<Partial<RootState>>([]);
const theme = createTheme();

// Helper function to render the component with a mock store and theme
const renderComponent = (
  initialState: Partial<RootState> = {}, props: any = {open: true, width: 240},
) => {
  const store = mockStore(initialState);
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <DomeAppMenu {...props} />
      </ThemeProvider>
    </Provider>,
  );
};

/**
 * DomeAppMenu component test.
 */
describe('DomeAppMenu', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    // Default to not logged in
    (auth.selectors.isLoggedIn as jest.Mock).mockReturnValue(false);
    (project.selectors.getCurrentProjectObject as unknown as jest.Mock)
      .mockReturnValue(null);
  });

  test('does not render any menu items when not logged in', () => {
    renderComponent();
    // Check that none of the key menu items are present
    expect(screen.queryByText('Select project')).not.toBeInTheDocument();
    expect(screen.queryByText('Config')).not.toBeInTheDocument();
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
  });

  test('renders only base menu items when \
    logged in but no project selected',
  () => {
    (auth.selectors.isLoggedIn as jest.Mock).mockReturnValue(true);
    renderComponent();

    expect(screen.getByText('Select project')).toBeInTheDocument();
    expect(screen.getByText('Config')).toBeInTheDocument();
  });

  describe('when logged in and a project is selected', () => {
    const baseProject = {
      name: 'Test Project Alpha',
      umpireEnabled: false,
      umpireReady: false,
    };

    test('renders project name and all menu items', () => {
      (auth.selectors.isLoggedIn as jest.Mock).mockReturnValue(true);
      (project.selectors.getCurrentProjectObject as unknown as jest.Mock)
        .mockReturnValue(baseProject);
      renderComponent();

      expect(screen.getByText('Test Project Alpha')).toBeInTheDocument();
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText(/Bundles/)).toBeInTheDocument();
      expect(screen.getByText(/Factory Drive/)).toBeInTheDocument();
      expect(screen.getByText(/Logs/)).toBeInTheDocument();
      expect(screen.getByText(/Sync Status/)).toBeInTheDocument();
      expect(screen.getByText('Select project')).toBeInTheDocument();
      expect(screen.getByText('Config')).toBeInTheDocument();
    });

    test('disables specific items when umpireReady is false', () => {
      (auth.selectors.isLoggedIn as jest.Mock).mockReturnValue(true);
      (project.selectors.getCurrentProjectObject as unknown as jest.Mock)
        .mockReturnValue(baseProject);
      renderComponent();

      expect(
        screen.getByTestId('menuitem-DASHBOARD_APP'),
      ).not.toHaveAttribute('aria-disabled', 'true');
      expect(
        screen.getByTestId('menuitem-BUNDLES_APP'),
      ).toHaveAttribute('aria-disabled', 'true');
      expect(
        screen.getByTestId('menuitem-FACTORY_DRIVE_APP'),
      ).toHaveAttribute('aria-disabled', 'true');
      expect(
        screen.getByTestId('menuitem-LOG_APP'),
      ).toHaveAttribute('aria-disabled', 'true');
      expect(
        screen.getByTestId('menuitem-SYNC_STATUS_APP'),
      ).toHaveAttribute('aria-disabled', 'true');
    });

    test('shows "(activating...)" when umpireEnabled is true \
      but not ready',
    () => {
      (auth.selectors.isLoggedIn as jest.Mock).mockReturnValue(true);
      (project.selectors.getCurrentProjectObject as unknown as jest.Mock)
        .mockReturnValue({
          ...baseProject,
          umpireEnabled: true,
          umpireReady: false,
        });
      renderComponent();

      expect(screen.getByText('Bundles (activating...)')).toBeInTheDocument();
      expect(
        screen.getByText('Factory Drive (activating...)'),
      ).toBeInTheDocument();
      expect(screen.getByText('Logs (activating...)')).toBeInTheDocument();
      expect(
        screen.getByText('Sync Status (activating...)'),
      ).toBeInTheDocument();
    });

    test('does NOT show "(activating...)" and items enabled when \
      umpireReady is true',
    () => {
      (auth.selectors.isLoggedIn as jest.Mock).mockReturnValue(true);
      (project.selectors.getCurrentProjectObject as unknown as jest.Mock)
        .mockReturnValue({
          ...baseProject,
          umpireEnabled: true,
          umpireReady: true,
        });
      renderComponent();

      expect(screen.getByText('Bundles')).toBeInTheDocument();
      expect(screen.queryByText('(activating...)')).not.toBeInTheDocument();

      expect(
        screen.getByTestId('menuitem-BUNDLES_APP'),
      ).not.toHaveAttribute('aria-disabled', 'true');
      expect(
        screen.getByTestId('menuitem-FACTORY_DRIVE_APP'),
      ).not.toHaveAttribute('aria-disabled', 'true');
      expect(
        screen.getByTestId('menuitem-LOG_APP'),
      ).not.toHaveAttribute('aria-disabled', 'true');
      expect(
        screen.getByTestId('menuitem-SYNC_STATUS_APP'),
      ).not.toHaveAttribute('aria-disabled', 'true');
    });
  });

  test('controls visibility with the open prop', () => {
    (auth.selectors.isLoggedIn as jest.Mock).mockReturnValue(true);
    const {container, rerender} = renderComponent(
      {},
      {open: false, width: 240},
    );

    // With persistent variant, the content is in the DOM, but not visible.
    // We can check the visibility style of the Drawer's paper element.
    const drawerPaper = container.querySelector('.MuiDrawer-paper');
    expect(drawerPaper).not.toBeVisible();

    // Re-render with open: true
    rerender(
      <Provider store={mockStore({})}>
        <ThemeProvider theme={theme}>
          <DomeAppMenu width={240} open />
        </ThemeProvider>
      </Provider>,
    );
    expect(drawerPaper).toBeVisible();
  });
});
