// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, within} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import * as actions from '@app/bundle/actions';
import ResourceTable from '@app/bundle/components/resources_table';
import {Bundle} from '@app/bundle/types';
import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Mock modules
jest.mock('@app/bundle/actions', () => ({
  resetDuplicateBundleResource: jest.fn(),
}));
jest.mock('dateformat', () => jest.fn(() => '20251027120000'));

// Mock child form component
jest.mock('./duplicate_resource_form', () => (props: any) => (
  <div data-testid={`duplicate-form-${props.resourceType}`}>
    <button
      onClick={() => props.onSubmit({selectedDuplicate: 'mocked_selection'})}
    >
      Submit Duplicate for {props.resourceType}
    </button>
  </div>
));

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

/**
 * ResourceTable component test.
 */
describe('ResourceTable', () => {
  const defaultBundle: Bundle = {
    name: 'test-bundle',
    resources: {
      firmware: {type: 'firmware', version: '1.0'},
      toolkit: {type: 'toolkit', version: '2.0', information: 'Some info'},
      test_image: {type: 'test_image', version: 'N/A'},
      hwid: {type: 'hwid', version: '3.0', warningMessage: '["Warning 1"]'},
      complete: {type: 'complete', version: '4.0'},
    },
    requireUserAction: {
      hwid: [{type: 'duplicate', link: 'some-link', versions: ['3.0', '2.9']}],
    },
  } as unknown as Bundle;

  const defaultProps = {
    projectName: 'test-project',
    bundle: defaultBundle,
  };

  const renderComponent = (props = defaultProps, initialState = {}) => {
    const theme = createTheme();
    const store = mockStore(initialState as unknown as RootState);
    store.dispatch = jest.fn();

    return {
      render: render(
        <ThemeProvider theme={theme}>
          <Provider store={store}>
            <ResourceTable {...props} />
          </Provider>
        </ThemeProvider>,
      ),
      dispatch: store.dispatch,
    };
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render resource types, file types, and versions', () => {
    renderComponent();
    expect(screen.getByText('1.0')).toBeInTheDocument();
    expect(screen.getByText('toolkit (*.run)')).toBeInTheDocument();
    expect(screen.getByText('2.0')).toBeInTheDocument();
    expect(screen.getByText('Some info')).toBeInTheDocument();
  });

  test('should display warning messages', () => {
    renderComponent();
    expect(screen.getByText('Warning 1')).toBeInTheDocument();
  });

  test('should NOT render download button if version is N/A', () => {
    renderComponent();
    expect(screen.queryByTestId('download-test_image')).not.toBeInTheDocument();
  });

  test('should render DuplicateResourceForm when duplicates exist', () => {
    renderComponent();
    expect(screen.getByTestId('duplicate-form-hwid')).toBeInTheDocument();
  });

  test('should call resetDuplicateBundleResource \
    on DuplicateResourceForm submit',
  () => {
    const {dispatch} = renderComponent();

    const duplicateForm = screen.getByTestId('duplicate-form-hwid');
    const submitButton = within(duplicateForm)
      .getByText('Submit Duplicate for hwid');
    fireEvent.click(submitButton);

    expect(dispatch).toHaveBeenCalledTimes(1);
    expect(actions.resetDuplicateBundleResource).toHaveBeenCalledWith(
      'test-project',
      'test-bundle',
      'test-bundle-20251027120000',
      'Updated "hwid" type resource',
      'hwid',
      'mocked_selection',
    );
  });

  test('should generate correct bundleName when original name is empty', () => {
    const emptyBundleProps = {
      ...defaultProps,
      bundle: {
        ...defaultBundle,
        name: 'empty',
      },
    };
    renderComponent(emptyBundleProps);

    const duplicateForm = screen.getByTestId('duplicate-form-hwid');
    const submitButton = within(duplicateForm)
      .getByText('Submit Duplicate for hwid');
    fireEvent.click(submitButton);

    expect(actions.resetDuplicateBundleResource).toHaveBeenCalledWith(
      'test-project',
      'empty',
      'test-project-20251027120000',
      'Updated "hwid" type resource',
      'hwid',
      'mocked_selection',
    );
  });

  test('should generate correct bundleName when \
    original name has a timestamp',
  () => {
    const timedBundleProps = {
      ...defaultProps,
      bundle: {
        ...defaultBundle,
        name: 'test-bundle-20240101000000',
      },
    };
    renderComponent(timedBundleProps);

    const duplicateForm = screen.getByTestId('duplicate-form-hwid');
    const submitButton = within(duplicateForm)
      .getByText('Submit Duplicate for hwid');
    fireEvent.click(submitButton);

    expect(actions.resetDuplicateBundleResource).toHaveBeenCalledWith(
      'test-project',
      'test-bundle-20240101000000',
      'test-bundle-20251027120000',
      'Updated "hwid" type resource',
      'hwid',
      'mocked_selection',
    );
  });
});
