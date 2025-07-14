// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore, Store} from 'redux';
import {reducer as formReducer} from 'redux-form';

import {NAME as SHOPFLOOR_SERVICE_FORM_NAME} from '@app/service/constants';
import {Schema} from '@app/service/types';

import ShopfloorServiceForm from './shopfloor_service_form';

// Mock the RenderFields component
jest.mock('./render_fields', () => ({schema}: {schema: Schema}) => (
  <div data-testid="render-fields">Mocked RenderFields: {schema.$id}</div>
));

// Helper function to render with Redux Provider
const renderWithRedux = (
  ui: React.ReactElement,
  {store = createStore(combineReducers({form: formReducer}))} = {},
) => {
  return {
    ...render(<Provider store={store}>{ui}</Provider>),
    store,
  };
};

/**
 * ShopfloorServiceForm component test.
 */
describe('ShopfloorServiceForm', () => {
  let mockOnSubmit: jest.Mock;
  let mockHandleTestConnection: jest.Mock;
  let store: Store;

  const mockSchema: Schema = {
    description: 'Common service config schema',
    type: 'object',
    properties: {
      active: {
        description: 'Default service state on start',
        type: 'boolean',
      },
      serviceUrl: {
        description: 'URL to Shop Floor Service.',
        type: 'string',
      },
    },
  } as Schema;
  const service = {};

  beforeEach(() => {
    mockOnSubmit = jest.fn();
    mockHandleTestConnection = jest.fn();
    store = createStore(combineReducers({form: formReducer}));
  });

  test('should render correctly with the provided schema', () => {
    renderWithRedux(
      <ShopfloorServiceForm
        onSubmit={mockOnSubmit}
        schema={mockSchema}
        handleTestConnection={mockHandleTestConnection}
        form={SHOPFLOOR_SERVICE_FORM_NAME}
        initialValues={service}
        enableReinitialize
      />,
      {store},
    );

    // Check for the mocked RenderFields
    expect(screen.getByTestId('render-fields')).toBeInTheDocument();

    // Check for buttons
    expect(screen.getByRole('button', {name: 'Discard Changes'}))
      .toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Deploy'})).toBeInTheDocument();
    expect(screen.getByTestId('deploy-test-btn'))
      .toHaveTextContent('Deploy & Test');
  });

  test('should call onSubmit when the "Deploy" button is clicked', () => {
    renderWithRedux(
      <ShopfloorServiceForm
        onSubmit={mockOnSubmit}
        schema={mockSchema}
        handleTestConnection={mockHandleTestConnection}
        form={SHOPFLOOR_SERVICE_FORM_NAME}
        initialValues={service}
        enableReinitialize
      />,
      {store},
    );

    const deployButton = screen.getByRole('button', {name: 'Deploy'});
    fireEvent.click(deployButton);

    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
  });

  test('should call handleTestConnection and onSubmit \
    when "Deploy & Test" button is clicked',
  () => {
    renderWithRedux(
      <ShopfloorServiceForm
        onSubmit={mockOnSubmit}
        schema={mockSchema}
        handleTestConnection={mockHandleTestConnection}
        form={SHOPFLOOR_SERVICE_FORM_NAME}
        initialValues={service}
        enableReinitialize
      />,
      {store},
    );

    const deployTestButton = screen.getByTestId('deploy-test-btn');
    fireEvent.click(deployTestButton);

    expect(mockHandleTestConnection).toHaveBeenCalledTimes(1);
    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
  });
});
