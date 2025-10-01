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

import DomeAppVersionAlert from './dome_app_version_alert';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

// Helper function to render the component with the mock store
const renderWithStore = (
  ui: React.ReactNode,
  initialState: Partial<RootState> = {},
) => {
  const theme = createTheme();
  const store = mockStore(initialState as unknown as RootState);
  return render(
    <ThemeProvider theme={theme}>
      <Provider store={store}>{ui}</Provider>
    </ThemeProvider>,
  );
};

/**
 * DomeAppVersionAlert component test.
 */
describe('DomeAppVersionAlert', () => {
  test('should not display alert when version check is disabled', () => {
    const initialState: RootState = {
      app: {
        display: {
          config: {
            config: {
              versionCheckEnabled: false,
            },
          },
          domeApp: {
            domeInfo: {
              dockerImageLatestVersion: '2',
              dockerImageTimestamp: '1',
            },
          },
        },
      },
    } as unknown as RootState;
    renderWithStore(<DomeAppVersionAlert />, initialState);

    expect(
      screen.queryByText(/Get the latest DOME updates/),
    ).not.toBeInTheDocument();
  });

  test(
    'should not display alert when latest version is not greater than ' +
      'current version',
    () => {
      const initialState: RootState = {
        app: {
          display: {
            config: {
              config: {
                versionCheckEnabled: true,
              },
            },
            domeApp: {
              domeInfo: {
                dockerImageLatestVersion: '1',
                dockerImageTimestamp: '1',
              },
            },
          },
        },
      } as unknown as RootState;
      renderWithStore(<DomeAppVersionAlert />, initialState);

      expect(
        screen.queryByText(/Get the latest DOME updates/),
      ).not.toBeInTheDocument();
    },
  );

  test(
    'should display alert when version check is enabled ' +
      'and latest version is greater than current version',
    () => {
      const initialState: RootState = {
        app: {
          display: {
            config: {
              config: {
                versionCheckEnabled: true,
              },
            },
            domeApp: {
              domeInfo: {
                dockerImageLatestVersion: '2',
                dockerImageTimestamp: '1',
              },
            },
          },
        },
      } as unknown as RootState;
      renderWithStore(<DomeAppVersionAlert />, initialState);

      expect(
        screen.getByText(/Get the latest DOME updates/),
      ).toBeInTheDocument();
      const commandPattern =
        './cros_docker.sh update && ' +
        './cros_docker.sh pull && ' +
        './cros_docker.sh install && ' +
        './cros_docker.sh run';
      const expectedTextRegExpOriginal = new RegExp(commandPattern);
      expect(screen.getByText(expectedTextRegExpOriginal)).toBeInTheDocument();
    },
  );
});
