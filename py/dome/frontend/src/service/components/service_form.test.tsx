// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore, Store} from 'redux';
import {reducer as formReducer} from 'redux-form';

import ServiceForm from '@app/service/components/service_form';
import {NAME as SERVICE_FORM_NAME} from '@app/service/constants';
import {Schema} from '@app/service/types';

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
 * ServiceForm component test.
 */
describe('ServiceForm', () => {
  let mockOnSubmit: jest.Mock;
  let store: Store;

  const mockSchema: Schema = {
    name: 'test-schema',
    description: 'A mock schema for testing',
    fields: [
      {
        name: 'serviceUrl',
        type: 'text',
        label: 'Service URL',
        required: true,
      },
      {
        name: 'apiKey',
        type: 'password',
        label: 'API Key',
        required: false,
      },
    ],
  } as Schema;
  const service = {};

  beforeEach(() => {
    mockOnSubmit = jest.fn();
    store = createStore(combineReducers({form: formReducer}));
  });

  test('should render correctly with the provided schema', () => {
    renderWithRedux(
      <ServiceForm
        onSubmit={mockOnSubmit}
        schema={mockSchema}
        form={SERVICE_FORM_NAME}
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
  });

  test('should call onSubmit when the Deploy button is clicked', async () => {
    renderWithRedux(
      <ServiceForm
        onSubmit={mockOnSubmit}
        schema={mockSchema}
        form={SERVICE_FORM_NAME}
        initialValues={service}
        enableReinitialize
      />,
      {store},
    );

    const deployButton = screen.getByRole('button', {name: 'Deploy'});
    fireEvent.click(deployButton);

    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
  });
});
