// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {InjectedFormProps, reducer as formReducer, reduxForm} from 'redux-form';

import ReduxFormRadiosField from './redux_form_radios_field';

// Define the shape of the form values
interface FormValues {
  radioGroup?: string;
}

// Props for the test form component
interface FormProps {
  extraFieldProps?: Partial<React.ComponentProps<typeof ReduxFormRadiosField>>;
}

// Example radio options for testing
const testRadioOptions = [
  {label: 'Option Alpha', value: 'alpha'},
  {label: 'Option Beta', value: 'beta'},
];

// Simple validation function for Redux Form
const validate = (values: FormValues) => {
  const errors: any = {};
  if (!values.radioGroup) {
    errors.radioGroup = 'A selection is required';
  }
  return errors;
};

// Create a simple form component to host the ReduxFormRadiosField
const TestForm: React.FC<
  InjectedFormProps<FormValues, FormProps> & FormProps
> = (props) => {
  const {extraFieldProps, handleSubmit} = props;
  return (
    <form onSubmit={handleSubmit}>
      <ReduxFormRadiosField
        name="radioGroup"
        radioColor="error"
        radioTypes={testRadioOptions}
        errorState
        {...extraFieldProps}
      />
      <button type="submit">Submit</button>
    </form>
  );
};

// Wrap the form component with reduxForm
const DecoratedTestForm = reduxForm<FormValues, FormProps>({
  form: 'testForm',
  validate,
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

/**
 * ReduxFormRadiosField component test.
 */
describe('ReduxFormRadiosField', () => {
  test('renders radio buttons with correct labels and values', () => {
    renderWithRedux(<DecoratedTestForm />);

    testRadioOptions.forEach((option) => {
      const radioElement = screen.getByLabelText(option.label);
      expect(radioElement).toBeInTheDocument();
    });
  });

  test('updates form state when a radio button is selected', () => {
    const {store} = renderWithRedux(<DecoratedTestForm />);

    const optionBeta = screen.getByLabelText('Option Beta');
    fireEvent.click(optionBeta);

    let formState = store.getState().form.testForm;
    expect(formState.values?.radioGroup).toBe('beta');

    const optionAlpha = screen.getByLabelText('Option Alpha');
    fireEvent.click(optionAlpha);

    formState = store.getState().form.testForm;
    expect(formState.values?.radioGroup).toBe('alpha');
  });

  test('applies custom classRadio and classLabel props', () => {
    renderWithRedux(
      <DecoratedTestForm
        extraFieldProps={{
          classRadio: 'custom-radio',
          classLabel: 'custom-label',
        }}
      />,
    );

    // Check class on the Radio component
    const radioControl = screen.getByLabelText('Option Alpha')
      .closest('div')?.querySelector('.MuiRadio-root');
    expect(radioControl).toHaveClass('custom-radio');

    // Check class on the label Typography
    const labelText = screen.getByText('Option Alpha');
    expect(labelText).toHaveClass('custom-label');
  });

  test('applies radioColor prop', () => {
    renderWithRedux(
      <DecoratedTestForm
        extraFieldProps={{
          radioColor: 'secondary',
        }}
      />,
    );

    const radioControl = screen.getByLabelText('Option Alpha')
      .closest('div')?.querySelector('.MuiRadio-root');
    expect(radioControl).toHaveClass('MuiRadio-colorSecondary');
    expect(radioControl).toHaveClass('MuiRadio-colorSecondary');
  });
});
