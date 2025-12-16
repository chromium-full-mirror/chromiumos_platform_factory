// Copyright 2026 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render} from '@testing-library/react';
import React from 'react';

import ReduxFormDateField from '@app/log/components/redux_form_date_field';
import {
  ReduxFormTextFieldProps,
} from '@common/components/redux_form_text_field';

jest.mock('@common/components/redux_form_text_field', () => {
  const MockReduxFormTextField = (props: ReduxFormTextFieldProps) => (
    <input data-testid="mock-text-field" {...props} />
  );
  return MockReduxFormTextField;
});

/**
 * ReduxFormDateField component test.
 */
describe('ReduxFormDateField', () => {
  test('should render the ReduxFormTextField correctly', () => {
    const {getByTestId} = render(
      <ReduxFormDateField name="testDate" label={''} />,
    );
    const input = getByTestId('mock-text-field');
    expect(input).toHaveAttribute('type', 'date');
  });
});
