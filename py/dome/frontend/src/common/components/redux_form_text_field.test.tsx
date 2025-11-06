// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {InjectedFormProps, reducer as formReducer, reduxForm} from 'redux-form';

import ReduxFormTextField from '@common/components/redux_form_text_field';

/**
 * ReduxFormTextField component test.
 */
describe('ReduxFormTextField', () => {
  // Define the shape of the form values
  interface FormValues {
    value?: string;
  }

  // Props for the test form component
  interface FormProps {
    extraFieldProps?: Partial<React.ComponentProps<typeof ReduxFormTextField>>;
  }

  // Create a simple form component to host the ReduxFormRadiosField
  const TestForm: React.FC<
    InjectedFormProps<FormValues, FormProps> & any
  > = (props) => {
    const {extraFieldProps, handleSubmit} = props;
    return (
      <form onSubmit={handleSubmit}>
        <ReduxFormTextField
          {...extraFieldProps}
          name={props.extraFieldProps.label}
        />
        <button type="submit">Submit</button>
      </form>
    );
  };

  // Wrap the form component with reduxForm
  const DecoratedTestForm = reduxForm<FormValues, FormProps>({
    form: 'testForm',
  })(TestForm);

  // Helper function to render the component with Redux Provider
  const renderWithRedux = (ui: React.ReactElement) => {
    const rootReducer = combineReducers({form: formReducer});
    const store = createStore(rootReducer);
    return {
      ...render(<Provider store={store}>{ui}</Provider>),
      store,
    };
  };

  test('renders the label correctly', () => {
    renderWithRedux(
      <DecoratedTestForm
        extraFieldProps={{
          label: 'Custom Label',
        }}
      />,
    );
    expect(screen.getByLabelText('Custom Label')).toBeInTheDocument();
  });

  test('renders an input field', () => {
    renderWithRedux(
      <DecoratedTestForm
        extraFieldProps={{
          label: 'Test Label',
        }}
      />,
    );
    expect(
      screen.getByRole('textbox', {name: 'Test Label'}),
    ).toBeInTheDocument();
  });

  test('hides error when ignoreTouch is true but no error', () => {
    renderWithRedux(
      <DecoratedTestForm
        extraFieldProps={{
          label: 'Test Label',
        }}
      />,
    );
    const inputContainer = screen.getByLabelText('Test Label')
      .closest('.MuiFormControl-root');
    expect(inputContainer).not.toHaveClass('Mui-error');
  });

  test('passes other props like type, placeholder, and disabled', () => {
    renderWithRedux(
      <DecoratedTestForm
        extraFieldProps={{
          label: 'Test Label',
          type: 'password',
          placeholder: 'Enter password',
          disabled: true,
        }}
      />,
    );
    const input = screen.getByLabelText('Test Label');
    expect(input).toHaveAttribute('type', 'password');
    expect(input).toHaveAttribute('placeholder', 'Enter password');
    expect(input).toBeDisabled();
  });
});
