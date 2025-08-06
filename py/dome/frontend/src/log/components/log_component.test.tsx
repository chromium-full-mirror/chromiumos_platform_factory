// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';

import * as utils from '@common/utils';
import {createTheme, ThemeProvider} from '@mui/material/styles';

import LogComponent, {LogComponentOwnProps} from './log_component';

// Deeply mock the modules
jest.mock('@common/utils');

// Setup mock implementations
const mockAssertNotReachable = utils.assertNotReachable as unknown as jest.Mock;
mockAssertNotReachable.mockReturnValue('error');

const theme = createTheme();
const renderComponent = (props: any = {}) => {
  const basicProps: Omit<LogComponentOwnProps, 'retry' | 'remove'> = {
    message: 'Test message',
    componentType: 'item',
    componentState: 'SUCCEEDED',
    progress: undefined,
    expanded: false,
  };
  return render(
    <ThemeProvider theme={theme}>
      <LogComponent {...basicProps} {...props} />
    </ThemeProvider>,
  );
};

/**
 * LogComponent component test.
 */
describe('LogComponent', () => {
  test('renders with the correct message', () => {
    renderComponent();
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  test('renders a success icon when state is SUCCEEDED', () => {
    renderComponent({componentState: 'SUCCEEDED'});
    expect(screen.getByTestId(/CheckCircle/i)).toBeInTheDocument();
  });

  test('renders a circular progress when state is PROCESSING', () => {
    renderComponent({componentState: 'PROCESSING'});
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders an error icon and calls retry \
    when FAILED and retry is provided',
  () => {
    const retryMock = jest.fn();
    renderComponent({
      componentState: 'FAILED',
      retry: retryMock,
    });
    const retryButton = screen.getByTestId(/ErrorIcon/i);
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(retryMock).toHaveBeenCalled();
  });

  test('renders an error icon disabled \
    when FAILED and retry is not provided',
  () => {
    renderComponent({componentState: 'FAILED'});
    const retryButton = screen.getByTestId(/ErrorIcon/i);
    expect(retryButton).toBeInTheDocument();
    expect(retryButton).toBeDisabled();
  });

  test('renders a report icon when state is REPORT', () => {
    renderComponent({componentState: 'REPORT'});
    expect(screen.getByTestId(/ReportProblem/i)).toBeInTheDocument();
  });

  test('renders a running icon when state is WAITING', () => {
    renderComponent({componentState: 'WAITING'});
    expect(screen.getByTestId(/AutoRenew/i)).toBeInTheDocument();
  });

  test('calls remove when delete button is clicked', () => {
    const removeMock = jest.fn();
    renderComponent({remove: removeMock});
    const deleteButton = screen.getByTestId(/Delete/i);
    fireEvent.click(deleteButton);
    expect(removeMock).toHaveBeenCalled();
  });

  test('disables remove button when remove is not provided', () => {
    renderComponent();
    const deleteButton = screen.getByTestId(/Delete/i);
    expect(deleteButton).toBeDisabled();
  });

  test('renders a header with the correct styles', () => {
    renderComponent({
      componentType: 'header',
      message: 'header message',
    });
    expect(screen.getByText('header message')).toBeInTheDocument();
    expect(screen.getByText('header message'))
      .toHaveStyle(`font-size: ${theme.typography.pxToRem(18)}`);
  });

  test('renders an item with the correct styles', () => {
    renderComponent({
      componentType: 'item',
      message: 'item message',
    });
    renderComponent({componentType: 'item'});
    expect(screen.getByText('item message')).toBeInTheDocument();
  });

  test('renders a list-item with the correct styles', () => {
    renderComponent({
      componentType: 'list-item',
      message: 'list-item message',
    });
    renderComponent({componentType: 'list-item'});
    expect(screen.getByText('list-item message')).toBeInTheDocument();
  });

  test('disables the remove button when the component is WAITING', () => {
    renderComponent({
      componentState: 'WAITING',
      remove: () => undefined,
    });
    const deleteButton = screen.getByTestId(/Delete/i);
    expect(deleteButton).toBeDisabled();
  });

  test('disables the remove button when the component is PROCESSING', () => {
    renderComponent({
      componentState: 'PROCESSING',
      remove: () => undefined,
    });
    const deleteButton = screen.getByTestId(/Delete/i);
    expect(deleteButton).toBeDisabled();
  });

  test('non-exist componentState', () => {
    renderComponent({
      componentState: 'non_exist_state',
    });
    expect(mockAssertNotReachable).toHaveBeenCalledWith('non_exist_state');
    expect(mockAssertNotReachable).toReturnWith('error');
  });

  test('non-exist componentType', () => {
    renderComponent({
      componentType: 'non_exist_type',
    });
    expect(mockAssertNotReachable).toHaveBeenCalledWith('non_exist_type');
    expect(mockAssertNotReachable).toReturnWith('error');
  });
});
