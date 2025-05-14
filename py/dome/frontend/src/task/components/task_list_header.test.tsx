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

import TaskListHeader from '@app/task/components/task_list_header';
import {Task} from '@app/task/types';
import {RootState} from '@app/types';
import {indigo} from '@mui/material/colors';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

// Create a default MUI theme instance
const THEME = {
  palette: {
    primary: indigo,
  },
};

/**
 * TaskListHeader component test.
 */
describe('TaskListHeader', () => {
  let initialState: RootState;
  const mockCancelAllWaitingTasksFn = jest.fn();
  const mockDismissAllSucceededTasksFn = jest.fn();
  const mockSetCollapsedFn = jest.fn();
  const tasks: Task[] = [{
      taskId: '1',
      state: 'SUCCEEDED',
      description: 'string',
      warningMessage: null,
      method: 'GET',
      url: 'string',
      progress: {
        uploadedSize: 0,
        totalSize: 0,
        uploadedFiles: 0,
        totalFiles: 0,
      },
    },
  ];

  beforeEach(() => {
    initialState = {
      app: {
        display: {
        },
      },
    } as unknown as RootState;
  });

  test('verify setCollapsed have been called when collapsed is true', () => {
    const store = mockStore(initialState);
    store.dispatch = jest.fn();

    render(
      <ThemeProvider theme={createTheme(THEME)}>
        <Provider store={store}>
          <TaskListHeader
            tasks={tasks}
            cancelAllWaitingTasks={mockCancelAllWaitingTasksFn}
            dismissAllSucceededTasks={mockDismissAllSucceededTasksFn}
            setCollapsed={mockSetCollapsedFn}
            collapsed
          />
        </Provider>
      </ThemeProvider>,
    );

    fireEvent.click(screen.getByRole('button'));
    expect(mockSetCollapsedFn).toHaveBeenCalled();
  });

  test('verify setCollapsed have been called when collapsed is false', () => {
    const store = mockStore(initialState);
    store.dispatch = jest.fn();

    render(
      <ThemeProvider theme={createTheme(THEME)}>
        <Provider store={store}>
          <TaskListHeader
            tasks={tasks}
            cancelAllWaitingTasks={mockCancelAllWaitingTasksFn}
            dismissAllSucceededTasks={mockDismissAllSucceededTasksFn}
            setCollapsed={mockSetCollapsedFn}
            collapsed={false}
          />,
        </Provider>
      </ThemeProvider>,
    );

    fireEvent.click(screen.getByTestId('ExpandLessIcon'));
    expect(mockSetCollapsedFn).toHaveBeenCalled();
  });
});
