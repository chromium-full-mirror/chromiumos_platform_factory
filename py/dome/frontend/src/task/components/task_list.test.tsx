// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import {cancelWaitingTaskAfter, dismissTask} from '@app/task/actions';
import TaskList from '@app/task/components/task_list';
import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

jest.mock('../actions');

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

const renderWithProviders = (tasks: object) => {
  const initialState = {
    app: {
      display: {
        task: {
          tasks,
        },
      },
    },
  } as unknown as RootState;
  const store = mockStore(initialState);
  const theme = createTheme();
  store.dispatch = jest.fn();

  return {
    render: render(
      <ThemeProvider theme={theme}>
        <Provider store={store}>
          <TaskList />
        </Provider>
      </ThemeProvider>,
    ),
    dispatch: store.dispatch,
  };
};

/**
 * TaskList component test.
 */
describe('TaskList', () => {
  test('should render without tasks', () => {
    renderWithProviders([]);
    expect(screen.queryByText(/Task/)).not.toBeInTheDocument();
  });

  test('should render a list of tasks', () => {
    const tasks = [
      {
        taskId: '82e310b8-d3d4-4828-90b2-c6e29ef9fa0d',
        state: 'SUCCEEDED',
        description: 'Task 1',
        warningMessage: '',
        progress: 50,
      },
      {
        taskId: '82e310b8-d3d4-4828-90b2-c6e29ef9fa0e',
        state: 'WAITING',
        description: 'Task 2',
        warningMessage: '',
        progress: 0,
      },
    ];
    renderWithProviders(tasks);

    expect(screen.getByText(/Task 1/)).toBeInTheDocument();
    expect(screen.getByText(/Task 2/)).toBeInTheDocument();
  });

  test('should call cancelWaitingTaskAfter when cancel all is clicked', () => {
    const tasks = [
      {
        taskId: '82e310b8-d3d4-4828-90b2-c6e29ef9fa0d',
        state: 'WAITING',
        description: 'Task 1',
        warningMessage: '',
        progress: 0,
      },
    ];
    const {dispatch} = renderWithProviders(tasks);

    const allBtn = screen.getAllByTestId(/DeleteIcon/i);
    allBtn.map((btn) => {
      fireEvent.click(btn);
    });

    expect(dispatch).toHaveBeenCalledWith(
      cancelWaitingTaskAfter('82e310b8-d3d4-4828-90b2-c6e29ef9fa0d'),
    );
  });

  test('call dismissTask for succeeded tasks when dismiss is clicked', () => {
    const tasks = [
      {
        taskId: '82e310b8-d3d4-4828-90b2-c6e29ef9fa0d',
        state: 'SUCCEEDED',
        description: 'Task 1',
        warningMessage: '',
        progress: 100,
      },
      {
        taskId: '82e310b8-d3d4-4828-90b2-c6e29ef9fa0e',
        state: 'WAITING',
        description: 'Task 2',
        warningMessage: '',
        progress: 50,
      },
      {
        taskId: '82e310b8-d3d4-4828-90b2-c6e29ef9fa0f',
        state: 'SUCCEEDED',
        description: 'Task 3',
        warningMessage: '',
        progress: 100,
      },
    ];
    const {dispatch} = renderWithProviders(tasks);

    const allBtn = screen.getAllByRole('button', {name: /dismiss/i});
    allBtn.map((btn) => {
      fireEvent.click(btn);
    });

    expect(dispatch).toHaveBeenCalledWith(
      dismissTask('82e310b8-d3d4-4828-90b2-c6e29ef9fa0d'),
    );
    expect(dispatch).toHaveBeenCalledWith(
      dismissTask('82e310b8-d3d4-4828-90b2-c6e29ef9fa0f'),
    );
  });

  test('should collapse and expand the task list', () => {
    const tasks = [
      {
        taskId: '82e310b8-d3d4-4828-90b2-c6e29ef9fa0d',
        state: 'WAITING',
        description: 'Task 1',
        warningMessage: '',
        progress: 50,
      },
    ];
    renderWithProviders(tasks);
    // Collapse the task list
    fireEvent.click(screen.getByTestId(/ExpandLessIcon/i));
    expect(() => screen.getByText('Task 1')).toThrow();
    // Expand the task list
    fireEvent.click(screen.getByTestId(/ExpandMoreIcon/i));
    expect(screen.getByText('Task 1')).toBeVisible();
  });
});
