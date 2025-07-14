// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {reducer as formReducer} from 'redux-form';

import LoginForm from '@app/auth/components/login_form';
import {createTheme, ThemeProvider} from '@mui/material/styles';

const renderWithProviders = (ui: any, {
  reduxState = {}, ...renderOptions
} = {}) => {
  const store = createStore(combineReducers({form: formReducer}), reduxState);
  const theme = createTheme();
  return render(
    <ThemeProvider theme={theme}>
      <Provider store={store}>
        {ui}
      </Provider>
    </ThemeProvider>,
    renderOptions,
  );
};

/**
 * LoginForm component test.
 */
describe('LoginForm', () => {
  test('should render the login form elements', () => {
    const handleSubmit = jest.fn();
    renderWithProviders(<LoginForm onSubmit={handleSubmit} />);

    expect(screen.getByText('Login to continue')).toBeInTheDocument();

    // Check for input fields using their labels
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();

    // Check for the submit button
    expect(screen.getByRole('button', {name: 'Login'})).toBeInTheDocument();
  });
});
