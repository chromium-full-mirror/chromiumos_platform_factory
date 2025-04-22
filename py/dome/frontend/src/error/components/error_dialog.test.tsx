// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import '@testing-library/jest-dom/extend-expect';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {hideErrorDialog, showMoreErrorMessage} from '@app/error/actions';
import ErrorDialog from '@app/error/components/error_dialog';
import {RootState} from '@app/types';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

/**
 * ErrorDialog component test.
 */
describe('ErrorDialog', () => {
  let initialState: RootState;

  beforeEach(() => {
    // Define a default initial state for the Redux store
    initialState = {
      app: {
        display: {
          error: {
            show: true,
            showMore: false,
            message: {
              errorMessage: 'Redux error message',
            },
          },
        },
      },
    } as unknown as RootState;
  });

  const renderComponent = (props = {}, customStoreState = {}) => {
    const store = mockStore({...initialState, ...customStoreState});
    return render(
      <Provider store={store}>
        <ErrorDialog {...props} />
      </Provider>,
    );
  };

  test('renders with default messages from Redux store', () => {
    renderComponent();

    const textareas = screen.getAllByRole('textbox');
    expect(textareas[0]).toHaveValue('Redux error message');
    expect(screen.getByTestId('error-dialog')).toBeVisible();
  });

  test('renders with both custom ErrorMessage and MoreErrorMessage', () => {
    const customMessage = 'Custom main error';
    const customMoreMessage = 'Custom detailed error information';
    renderComponent({}, {
      app: {
        display: {
          error: {
            show: true,
            showMore: true,
            message: {
              errorMessage: customMessage,
              moreErrorMessage: customMoreMessage,
            },
          },
        },
      },
    });

    const textareas = screen.getAllByRole('textbox');
    expect(textareas[0]).toHaveValue(customMessage);
    expect(textareas[1]).toHaveValue(customMoreMessage);
  });

  test('calls showMoreErrorMessage when showMore button is clicked', () => {
    const store = mockStore(initialState);
    store.dispatch = jest.fn();

    render(
      <Provider store={store}>
        <ErrorDialog />
      </Provider>,
    );

    const showMoreButton = screen.getByRole('button', {name: /Show more/i});
    fireEvent.click(showMoreButton);

    expect(store.dispatch).toHaveBeenCalledTimes(1);
    expect(store.dispatch).toHaveBeenCalledWith(showMoreErrorMessage());
  });

  test('calls hideErrorDialog action when close button is clicked', () => {
    const store = mockStore(initialState);
    store.dispatch = jest.fn();

    render(
      <Provider store={store}>
        <ErrorDialog />
      </Provider>,
    );

    const closeButton = screen.getByRole('button', {name: /close/i});
    fireEvent.click(closeButton);

    expect(store.dispatch).toHaveBeenCalledTimes(1);
    expect(store.dispatch).toHaveBeenCalledWith(hideErrorDialog());
  });
});
