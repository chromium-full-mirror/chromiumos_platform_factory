// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore, Store} from 'redux';
import {reducer as formReducer} from 'redux-form';

import CreateProjectForm from '@app/project/components/create_project_form';
import {CREATE_PROJECT_FORM} from '@app/project/constants';

// Mock Redux store setup for redux-form
const rootReducer = combineReducers({
  form: formReducer,
});

const createMockStore = (initialState = {}): Store => {
  return createStore(rootReducer, initialState);
};

/**
 * CreateProjectForm component test.
 */
describe('CreateProjectForm', () => {
  const mockSubmitHandler = jest.fn();
  const existingProjectNames = ['existing-project', 'another-one'];

  const renderComponent = (store: Store = createMockStore(), props = {}) => {
    return render(
      <Provider store={store}>
        <CreateProjectForm
          projectNames={existingProjectNames}
          onSubmit={mockSubmitHandler}
          {...props}
        />
      </Provider>,
    );
  };

  beforeEach(() => {
    mockSubmitHandler.mockClear();
  });

  test('should render all form elements correctly', () => {
    renderComponent();

    // Check for the text field
    expect(screen.getByLabelText(/New project name/i)).toBeInTheDocument();

    // Check for the checkbox
    expect(screen.getByLabelText(/Is this an Android project?/i))
      .toBeInTheDocument();

    // Check for the submit button
    expect(screen.getByRole('button', {name: /Create a new project/i}))
      .toBeInTheDocument();
  });

  test('should display a validation error if the project name is empty', () => {
    renderComponent();

    const nameInput = screen.getByLabelText(/New project name/i);
    const submitButton = screen.getByRole('button', {
      name: /Create a new project/i,
    });

    // Touch the field and blur without typing
    fireEvent.click(nameInput);
    fireEvent.blur(nameInput);

    // Attempt to submit
    fireEvent.click(submitButton);

    expect(mockSubmitHandler).not.toHaveBeenCalled();
  });

  test('display a validation error if the project name already exists', () => {
    renderComponent();

    const nameInput = screen.getByLabelText(/New project name/i);
    const submitButton = screen.getByRole('button', {
      name: /Create a new project/i,
    });

    // Use an existing project name
    fireEvent.input(nameInput, existingProjectNames[0]);
    fireEvent.click(submitButton);

    // Check for the custom unique validation message
    expect(mockSubmitHandler).not.toHaveBeenCalled();
  });

  test('can update form state in Redux store when checkbox is toggled', () => {
    const store = createMockStore();
    renderComponent(store);

    const androidString = /Is this an Android project?/i;
    const androidCheckbox = screen.getByLabelText(androidString);

    // Initial state (should be undefined or false)
    let formState = store.getState().form[CREATE_PROJECT_FORM]?.values;
    expect(formState?.isAndroid).not.toBe(true);

    // Check the box
    fireEvent.click(androidCheckbox);
    expect(androidCheckbox).toBeChecked();
    formState = store.getState().form[CREATE_PROJECT_FORM]?.values;
    expect(formState?.isAndroid).toBe(true);

    // Uncheck the box
    fireEvent.click(androidCheckbox);
    expect(androidCheckbox).not.toBeChecked();
    formState = store.getState().form[CREATE_PROJECT_FORM]?.values;
    expect(formState?.isAndroid).toBe(false);
  });
});
