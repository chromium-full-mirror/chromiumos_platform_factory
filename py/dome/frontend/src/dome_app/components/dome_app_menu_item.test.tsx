// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {switchApp} from '@app/dome_app/actions';
import DomeAppMenuItem from '@app/dome_app/components/dome_app_menu_item';
import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

const theme = createTheme();

/**
 * DomeAppMenuItem component test.
 */
describe('DomeAppMenuItem', () => {
  const currentTestApp = 'DASHBOARD_APP';
  const childrenContent = 'My Test App';

  test('renders correctly', () => {
    const initialState = {
      app: {
        display: {
          domeApp: {
            currentApp: currentTestApp,
          },
        },
      },
    } as unknown as RootState;
    const store = mockStore(initialState);

    render(
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <DomeAppMenuItem app={currentTestApp}>
            {childrenContent}
          </DomeAppMenuItem>
        </ThemeProvider>
      </Provider>,
    );

    const menuItem = screen.getByRole('menuitem', {name: childrenContent});
    expect(menuItem).toBeInTheDocument();
  });

  test('dispatches switchApp with the correct app name when clicked', () => {
    const initialState = {
      app: {
        display: {
          domeApp: {
            currentApp: currentTestApp,
          },
        },
      },
    } as unknown as RootState;
    const store = mockStore(initialState);
    store.dispatch = jest.fn();

    render(
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <DomeAppMenuItem app={currentTestApp}>
            {childrenContent}
          </DomeAppMenuItem>
        </ThemeProvider>
      </Provider>,
    );

    const menuItem = screen.getByRole('menuitem', {name: childrenContent});
    fireEvent.click(menuItem);

    // Check if the correct action was dispatched
    const expectedAction = switchApp(currentTestApp);
    expect(store.dispatch).toHaveBeenCalledTimes(1);
    expect(store.dispatch).toHaveBeenCalledWith(expectedAction);
  });
});
