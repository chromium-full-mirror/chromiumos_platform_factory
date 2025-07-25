// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {
  activateBundle,
  collapseBundle,
  deleteBundle,
  expandBundle,
  setBundleAsNetboot,
} from '@app/bundle/actions';
import {Bundle} from '@app/bundle/types';
import {RootState} from '@app/types';
import {ThemeProvider} from '@mui/material/styles';
import {createTheme} from '@mui/material/styles';

import BundleComponent, {BundleComponentOwnProps} from './bundle_component';

jest.mock('@app/bundle/actions');

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

const theme = createTheme();
const netbootName = /use this bundle's netboot resource/i;
const warningMessage = '[\"This is warning message for project A.\"]';

const sampleBundle: BundleComponentOwnProps['bundle'] = {
  name: 'test-bundle',
  note: 'This is a test bundle',
  active: true,
  requireUserAction: {},
  warningMessage,
  resources: {
    cmdline: {
      type: 'string',
      version: 'string',
      hash: 'string',
      information: 'string',
      warningMessage,
    },
  },
};

const sampleBundles: BundleComponentOwnProps['bundles'] = [
  sampleBundle,
  {
    name: 'test-bundle-2',
    note: 'This is another test bundle',
    active: false,
    requireUserAction: {},
    warningMessage,
    resources: {
      cmdline: {
        type: 'string',
        version: 'string',
        hash: 'string',
        information: 'string',
        warningMessage,
      },
    },
  },
];

/**
 * BundleComponent component test.
 */
describe('BundleComponent', () => {
  let initialState: RootState;

  beforeEach(() => {
    // Define a default initial state for the Redux store
    initialState = {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle': false},
            entries: [sampleBundle],
          },
        },
      },
    } as unknown as RootState;
  });

  const renderComponent = (
    props = {}, customStoreState = {}, bundle: Bundle, bundles: Bundle[],
  ) => {
    const store = mockStore({...initialState, ...customStoreState});
    store.dispatch = jest.fn();
    return {
      customeRender: render(
        <Provider store={store}>
          <ThemeProvider theme={theme}>
            <BundleComponent
                bundle={bundle}
                bundles={bundles}
                {...props}
            />
          </ThemeProvider>
        </Provider>,
      ),
      dispatch: store.dispatch,
    };
  };

  test('renders correctly with active bundle', () => {
    renderComponent({}, {}, sampleBundle, sampleBundles);

    expect(screen.getByText('test-bundle')).toBeInTheDocument();
    expect(screen.getByText('This is a test bundle')).toBeInTheDocument();
    expect(screen.getByText('ACTIVE')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: netbootName})).toBeInTheDocument();
  });

  test('renders correctly with inactive bundle', () => {
    renderComponent({}, {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle-2',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle-2': false},
            entries: [sampleBundle],
          },
        },
      },
    }, sampleBundles[1], sampleBundles);

    expect(screen.getByText('test-bundle-2')).toBeInTheDocument();
    expect(screen.getByText('This is another test bundle')).toBeInTheDocument();
    expect(screen.getByText('INACTIVE')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: netbootName})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'delete this bundle'}))
      .toBeInTheDocument();
  });

  test('calls activateBundle when switch is toggled', () => {
    const {dispatch} = renderComponent({}, {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle': true},
            entries: [sampleBundle],
          },
        },
      },
    }, sampleBundle, sampleBundles);

    fireEvent.click(screen.getByRole('checkbox'));
    expect(dispatch).toHaveBeenCalledTimes(1);
    expect(dispatch).toHaveBeenCalledWith(activateBundle('test-bundle', false));
  });

  test('calls expandBundle when content is clicked', () => {
    const {dispatch} = renderComponent({}, {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle': false},
            entries: [sampleBundle],
          },
        },
      },
    }, sampleBundle, sampleBundles);

    fireEvent.click(screen.getByTestId('bundle-content-test-bundle'));
    expect(dispatch).toHaveBeenCalledTimes(1);
    expect(dispatch).toHaveBeenCalledWith(expandBundle('test-bundle'));
  });

  test('calls collapseBundle when content is clicked and expanded', () => {
    const {dispatch} = renderComponent({}, {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle': true},
            entries: [sampleBundle],
          },
        },
      },
    }, sampleBundle, sampleBundles);

    fireEvent.click(screen.getByTestId('bundle-content-test-bundle'));
    expect(dispatch).toHaveBeenCalledTimes(1);
    expect(dispatch).toHaveBeenCalledWith(collapseBundle('test-bundle'));
  });

  test('calls deleteBundle when delete button is clicked', () => {
    const {dispatch} = renderComponent({}, {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle-2',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle-2': false},
            entries: [sampleBundle],
          },
        },
      },
    }, sampleBundles[1], sampleBundles);

    fireEvent.click(screen.getByRole('button', {name: 'delete this bundle'}));
    expect(dispatch).toHaveBeenCalledTimes(1);
    expect(dispatch).toHaveBeenCalledWith(deleteBundle('test-bundle-2'));
  });

  test('calls setBundleAsNetboot when netboot button is clicked', () => {
    const {dispatch} = renderComponent({}, {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle-2',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle-2': false},
            entries: [sampleBundle],
          },
        },
      },
    }, sampleBundles[1], sampleBundles);

    fireEvent.click(screen.getByRole('button', {name: netbootName}));
    expect(dispatch).toHaveBeenCalledTimes(1);
    expect(dispatch).toHaveBeenCalledWith(
      setBundleAsNetboot('test-bundle-2', 'test-project'),
    );
  });

  test('should display error icon when requireUserAction is not empty', () => {
    const bundleWithError = {
      name: 'test-bundle-2',
      note: 'This is another test bundle',
      active: false,
      requireUserAction: {
        type: 'string',
        fileList: [{
          file: 'string',
          version: 'string',
        }],
      },
      resources: {
        cmdline: {
          type: 'string',
          version: 'string',
          hash: 'string',
          information: 'string',
          warningMessage,
        },
      },
    } as unknown as Bundle;

    renderComponent({}, {
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle',
              },
            },
          },
          bundle: {
            expanded: {'test-bundle': false},
            entries: [bundleWithError],
          },
        },
      },
    }, bundleWithError, [bundleWithError]);

    expect(screen.getByTestId('ErrorIcon')).toBeInTheDocument();
  });

  // Reset mocks after each test
  afterEach(() => {
    cleanup();
    jest.clearAllMocks();
  });
});
