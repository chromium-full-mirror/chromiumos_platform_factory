// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore, Store} from 'redux';
import {reducer as formReducer} from 'redux-form';

import {RequireUserAction, Resource} from '@app/bundle/types';

import DuplicateResourceForm from './duplicate_resource_form';

// Mock '@mui/styles' to provide mock classes
jest.mock('@mui/styles', () => ({
  ...jest.requireActual('@mui/styles'),
  createStyles: (styles: any) => styles,
  withStyles: (styles: any) =>
    (Component: React.ComponentType<any>) => (props: any) => {
      const theme = {spacing: (val: number) => val * 8};
      const styleDef = typeof styles === 'function' ? styles(theme) : styles;
      const mockClasses = Object.keys(styleDef).reduce((acc, key) => {
        acc[key] = key;
        return acc;
      }, {} as { [key: string]: string });
      return <Component {...props} classes={mockClasses} />;
    },
}));

// Helper function to render with Redux Provider
const renderWithProviders = (
  ui: React.ReactElement,
  {store}: {store?: Store} = {},
) => {
  const rootReducer = combineReducers({
    form: formReducer,
  });
  const finalStore = store || createStore(rootReducer);
  return {
    ...render(<Provider store={finalStore}>{ui}</Provider>),
    store: finalStore,
  };
};

/**
 * DuplicateResourceForm component test.
 */
describe('DuplicateResourceForm', () => {
  const mockResource: Resource = {
    type: 'Test Resource', name: 'test',
  } as unknown as Resource;
  const mockResourceType = 'testResourceType';
  const mockDuplicate: RequireUserAction = {
    fileList: [
      {version: 'v1.0', file: 'file1.txt'},
      {version: 'v2.0', file: 'file2.txt'},
    ],
    type: '',
  };
  const mockSubmit = jest.fn();

  const defaultProps = {
    form: `duplicateForm_${mockResourceType}`,
    resource: mockResource,
    resourceType: mockResourceType,
    duplicate: mockDuplicate,
    onSubmit: mockSubmit,
  };

  beforeEach(() => {
    mockSubmit.mockClear();
  });

  test('renders the component with the correct title and radio options', () => {
    renderWithProviders(<DuplicateResourceForm {...defaultProps} />);

    expect(screen.getByText(/Multiple "Test Resource" found/))
      .toBeInTheDocument();
    expect(screen.getByText(/please choose only one:/)).toBeInTheDocument();

    // Check for radio buttons
    const radioV1 = screen.getByLabelText('v1.0');
    expect(radioV1).toBeInTheDocument();

    const radioV2 = screen.getByLabelText('v2.0');
    expect(radioV2).toBeInTheDocument();

    expect(screen.getByRole('button', {name: 'Confirm'})).toBeInTheDocument();
  });

  test('calls onSubmit with the selected value when \
    Confirm is clicked',
  () => {
    renderWithProviders(<DuplicateResourceForm {...defaultProps} />);

    // Select an option
    const radioV2 = screen.getByLabelText('v2.0');
    fireEvent.click(radioV2);
    expect(radioV2).toBeChecked();

    // Submit the form
    const confirmButton = screen.getByRole('button', {name: 'Confirm'});
    fireEvent.click(confirmButton);

    expect(mockSubmit).toHaveBeenCalledTimes(1);
  });

  test('does not call onSubmit if no option is selected \
    due to validation',
  () => {
    renderWithProviders(<DuplicateResourceForm {...defaultProps} />);

    const confirmButton = screen.getByRole('button', {name: 'Confirm'});
    fireEvent.click(confirmButton);

    expect(mockSubmit).not.toHaveBeenCalled();
  });
});
