// Copyright 2026 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Field} from 'redux-form';

import ReduxFormTabsField from './redux_form_tabs_field';

// Mock the Field component to just pass props through to the component
jest.mock('redux-form', () => ({
  Field: jest.fn(({component, ...props}) => component(props)),
}));

/**
 * ReduxFormTabsField component test.
 */
describe('ReduxFormTabsField', () => {
  const mockTabTypes = [
    {name: 'Tab 1', value: 'tab1'},
    {name: 'Tab 2', value: 'tab2'},
    {name: 'Tab 3', value: 'tab3'},
  ];

  const mockOnChange = jest.fn();
  const mockInputProps = {
    value: 'tab1',
    onChange: mockOnChange,
    name: 'testTabs',
  };

  const defaultProps = {
    input: mockInputProps,
    meta: {},
    tab_types: mockTabTypes,
    name: 'testTabsField',
  };

  beforeEach(() => {
    // Clear mock calls before each test
    mockOnChange.mockClear();
    (Field as jest.Mock).mockClear();
  });

  test('should render the correct number of tabs', () => {
    render(<ReduxFormTabsField {...defaultProps} />);

    const tabs = screen.getAllByRole('tab');
    expect(tabs).toHaveLength(mockTabTypes.length);
  });

  test('should render tab labels correctly', () => {
    render(<ReduxFormTabsField {...defaultProps} />);

    mockTabTypes.forEach((tabType) => {
      expect(screen.getByRole('tab', {name: tabType.name})).toBeInTheDocument();
    });
  });

  test('should have the initial tab selected based on input.value', () => {
    render(<ReduxFormTabsField {...defaultProps} />);

    const initialTab = screen.getByRole('tab', {name: 'Tab 1'});
    expect(initialTab).toHaveAttribute('aria-selected', 'true');
  });

  test('should call onChange with the new value when a tab is clicked', () => {
    render(<ReduxFormTabsField {...defaultProps} />);

    const tabToClick = screen.getByRole('tab', {name: 'Tab 2'});
    fireEvent.click(tabToClick);

    // The onChange handler in the component receives the event and the new
    // value. Material UI Tabs onChange provides the new value as the second
    // argument.
    expect(mockOnChange).toHaveBeenCalledTimes(1);
    expect(mockOnChange).toHaveBeenCalledWith('tab2');
  });
});
