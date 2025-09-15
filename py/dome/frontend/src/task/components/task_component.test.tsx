// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import React from 'react';

import TaskComponent from '@app/task/components/task_component';
import {TaskState} from '@app/task/types';

import {createTheme, ThemeProvider} from '@mui/material/styles';

// Mock the icons to avoid rendering actual SVG content
jest.mock('@mui/icons-material/Autorenew',
  () => () => <div>AutorenewIcon</div>);
jest.mock('@mui/icons-material/CheckCircle',
  () => () => <div>CheckCircleIcon</div>,
);
jest.mock('@mui/icons-material/Delete', () => () => <div>DeleteIcon</div>);
jest.mock('@mui/icons-material/Error', () => () => <div>ErrorIcon</div>);
jest.mock('@mui/icons-material/Warning', () => () => <div>WarningIcon</div>);

const theme = createTheme();

const defaultProps = {
  state: 'WAITING' as TaskState,
  progress: {uploadedFiles: 0, totalFiles: 1, uploadedSize: 0, totalSize: 0},
  description: 'My test task description',
  warningMessage: null,
  dismiss: jest.fn(),
  retry: jest.fn(),
  cancel: jest.fn(),
};

// Helper function to render the component with ThemeProvider and default props
const renderComponent = (props = {}) => {
  const combinedProps = {...defaultProps, ...props};
  return render(
    <ThemeProvider theme={theme}>
      <TaskComponent {...combinedProps} />
    </ThemeProvider>,
  );
};

/**
 * TaskComponent component test.
 */
describe('TaskComponent', () => {
  test('renders the description', () => {
    renderComponent();
    expect(screen.getByText(defaultProps.description)).toBeInTheDocument();
  });

  describe('Warning Messages', () => {
    test('does not show warning icon when warningMessage is null', () => {
      renderComponent({warningMessage: null});
      expect(screen.queryByText('WarningIcon')).not.toBeInTheDocument();
    });

    test('does not show warning icon when warningMessage is empty', () => {
      renderComponent({warningMessage: ''});
      expect(screen.queryByText('WarningIcon')).not.toBeInTheDocument();
    });

    test('does not show warning icon when warningMessage is "[]"', () => {
      renderComponent({warningMessage: '[]'});
      expect(screen.queryByText('WarningIcon')).not.toBeInTheDocument();
    });

    test('shows warning messages when provided', () => {
      const warnings = ['Warning 1', 'Another warning'];
      renderComponent({warningMessage: JSON.stringify(warnings)});

      expect(screen.getByText('Warning 1')).toBeInTheDocument();
      expect(screen.getByText('Another warning')).toBeInTheDocument();
      expect(screen.getAllByText('WarningIcon').length).toBe(2);
    });
  });

  describe('State: WAITING', () => {
    beforeEach(() => {
      renderComponent({state: 'WAITING'});
    });

    test('shows AutorenewIcon', () => {
      expect(screen.getByText('AutorenewIcon')).toBeInTheDocument();
    });

    test('disables the action button', () => {
      const autorenewIcon = screen.getByText('AutorenewIcon').closest('button');
      expect(autorenewIcon).toBeDisabled();
    });

    test('enables the cancel button', () => {
      const deleteIcon = screen.getByText('DeleteIcon').closest('button');
      expect(deleteIcon).not.toBeDisabled();
    });
  });

  describe('State: RUNNING_UPLOAD_FILE', () => {
    test('shows a determinate CircularProgress', () => {
      const progress = {
        uploadedFiles: 0,
        totalFiles: 2,
        uploadedSize: 50,
        totalSize: 100,
      };
      renderComponent({state: 'RUNNING_UPLOAD_FILE', progress});
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toBeInTheDocument();
      expect(progressBar).toHaveAttribute('aria-valuenow', '50');
    });
  });

  describe('State: RUNNING_WAIT_RESPONSE', () => {
    test('shows an indeterminate CircularProgress', () => {
      renderComponent({state: 'RUNNING_WAIT_RESPONSE'});
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toBeInTheDocument();
    });
  });

  describe('State: SUCCEEDED', () => {
    beforeEach(() => {
      renderComponent({state: 'SUCCEEDED'});
    });
    test('shows DismissIcon', () => {
      expect(screen.getByText('CheckCircleIcon')).toBeInTheDocument();
    });
    test('disables the cancel button', () => {
      expect(screen.getByText('DeleteIcon').closest('button')).toBeDisabled();
    });
  });

  describe('State: FAILED', () => {
    test('shows ErrorIcon', () => {
      renderComponent({state: 'FAILED'});
      expect(screen.getByText('ErrorIcon')).toBeInTheDocument();
    });
  });

  describe('Cancel Button', () => {
    test('is disabled when state is not cancellable', () => {
      renderComponent({state: 'SUCCEEDED'});  // SUCCEEDED is not cancellable
      expect(screen.getByText('DeleteIcon').closest('button')).toBeDisabled();
    });
  });
});
