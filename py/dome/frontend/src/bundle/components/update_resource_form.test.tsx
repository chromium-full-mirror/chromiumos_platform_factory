// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {reducer as formReducer} from 'redux-form';

import UpdateResourceForm from '@app/bundle/components/update_resource_form';

interface RenderComponentOptions {
  bundleNames?: string[];
  handleSubmit?: jest.Mock;
}

const renderComponent = (options: RenderComponentOptions = {}) => {
  const rootReducer = combineReducers({form: formReducer});
  const store = createStore(rootReducer);

  const defaultProps = {
    bundleNames: [],
    handleSubmit: jest.fn(),
  };

  const props = {...defaultProps, ...options};

  return render(
    <Provider store={store}>
      <UpdateResourceForm {...props} />
    </Provider>,
  );
};

/**
 * UpdateResourceForm component test.
 */
describe('UpdateResourceForm', () => {
  test('should render form fields correctly', () => {
    renderComponent();

    expect(screen.getByLabelText('New Bundle Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Note')).toBeInTheDocument();
  });

  test('should NOT show unique error when name is new', async () => {
    renderComponent({bundleNames: ['other-bundle']});

    const nameInput = screen.getByLabelText('New Bundle Name');
    fireEvent.change(nameInput, {target: {value: 'new-bundle'}});
    fireEvent.blur(nameInput);

    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  test('should call handleSubmit prop on form submission', async () => {
    const mockHandleSubmit = jest.fn();
    renderComponent({handleSubmit: mockHandleSubmit});

    const nameInput = screen.getByLabelText('New Bundle Name');
    fireEvent.change(nameInput, {target: {value: 'submit-test'}});

    const form = screen.getByLabelText('New Bundle Name').closest('form');
    if (form) {
      fireEvent.submit(form);
    } else {
      throw new Error('Form element not found');
    }

    await waitFor(() => {
      expect(mockHandleSubmit).toHaveBeenCalled();
    });
  });
});
