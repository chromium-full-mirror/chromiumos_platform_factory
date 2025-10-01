// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen, waitFor} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import project from '@app/project';
import SyncStatusApp from '@app/sync_status/components/sync_status_app';
import {RootState} from '@app/types';
import {authorizedAxios} from '@common/utils';

// Mock the modules used by the component
jest.mock('@app/project');
jest.mock('@common/utils');

// Get the mocked functions
const mockedGetClientProject =
    project.selectors.getCurrentProject as
        jest.MockedFunction<typeof project.selectors.getCurrentProject>;
const mockedAuthorizedAxios =
    authorizedAxios as jest.MockedFunction<typeof authorizedAxios>;

const mockAxiosGet = jest.fn();

// Setup mock Redux store
const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

/**
 * SyncStatusApp component test.
 */
describe('SyncStatusApp', () => {
  let store: any;
  const testProjectName = 'my-test-project';

  beforeEach(() => {
    // Provide a mock implementation for the selector
    mockedGetClientProject.mockReturnValue(testProjectName);

    // Initial minimal state for the Redux store
    const initialState: Partial<RootState> = {};
    store = mockStore(initialState);

    // Mock the return value of authorizedAxios()
    mockedAuthorizedAxios.mockReturnValue({
      get: mockAxiosGet,
    } as any);

    // Reset any previous mock calls
    mockAxiosGet.mockReset();

    // Use fake timers to control setInterval/clearInterval
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();  // Restore real timers
  });

  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <SyncStatusApp />
      </Provider>,
    );
  };

  test('initially shows the setup message when no data is fetched', () => {
    // Prevent the API call from resolving immediately
    mockAxiosGet.mockImplementation(() => new Promise((resolve, reject) => {
      // This promise is intentionally left pending and never settles.
      // It's used to simulate an ongoing API request that hasn't completed yet.
    }));
    renderComponent();

    const expectMessage = /You haven't set up the secondary umpire./i;
    const expectInstructions = new RegExp(
      'You can go to the "Dashboard > Services > umpireSync" ' +
      'section to set up it.',
      'i',
    );
    expect(screen.getByText(expectMessage)).toBeInTheDocument();
    expect(screen.getByText(expectInstructions)).toBeInTheDocument();
  });

  test('shows setup message if API call fails', async () => {
    mockAxiosGet.mockRejectedValue(new Error('Network Error'));
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/You haven't set up the secondary umpire./i))
        .toBeInTheDocument();
    });
  });

  test('shows setup message if API returns an empty object', async () => {
    mockAxiosGet.mockResolvedValue({data: {}});
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/You haven't set up the secondary umpire./i))
        .toBeInTheDocument();
    });
  });

  test('polls the getStatus API every second', async () => {
    mockAxiosGet.mockResolvedValue({data: {}});
    renderComponent();

    // Should be called once on mount
    expect(mockAxiosGet).toHaveBeenCalledTimes(1);

    // Advance timers by 1000 ms
    jest.advanceTimersByTime(1000);
    expect(mockAxiosGet).toHaveBeenCalledTimes(2);

    // Advance timers by another 2000 ms
    jest.advanceTimersByTime(2000);
    expect(mockAxiosGet).toHaveBeenCalledTimes(4);
  });

  test('clears the interval timer on component unmount', async () => {
    mockAxiosGet.mockResolvedValue({data: {}});
    const {unmount} = renderComponent();

    const clearIntervalSpy = jest.spyOn(window, 'clearInterval');

    // Unmount the component
    unmount();

    // Expect clearInterval to have been called
    expect(clearIntervalSpy).toHaveBeenCalled();

    // Advance timers and ensure no more API calls are made
    jest.advanceTimersByTime(5000);
    expect(mockAxiosGet).toHaveBeenCalledTimes(1);
    clearIntervalSpy.mockRestore();
  });
});
