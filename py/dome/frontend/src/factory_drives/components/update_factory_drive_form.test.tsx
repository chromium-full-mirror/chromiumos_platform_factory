// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {reducer as formReducer} from 'redux-form';

import UpdateFactoryDriveForm from './update_factory_drive_form';

/**
 * UpdateFactoryDriveForm component test.
 */
describe('UpdateFactoryDriveForm', () => {
  test('should render without crashing', () => {
    const rootReducer = combineReducers({
      form: formReducer,
    });
    const store = createStore(rootReducer);
    const {container} = render(
      <Provider store={store}>
        <UpdateFactoryDriveForm />
      </Provider>,
    );
    expect(container).toBeInTheDocument();
  });
});
