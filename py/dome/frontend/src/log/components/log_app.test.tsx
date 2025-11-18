// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureMockStore from 'redux-mock-store';

import * as logActions from '@app/log/actions';
import LogApp from '@app/log/components/log_app';
import LogForm from '@app/log/components/log_form';
import LogPile from '@app/log/components/log_pile';
import * as logSelectors from '@app/log/selectors';
import {LogFormData} from '@app/log/types';
import * as projectSelectors from '@app/project/selectors';
import {RootState} from '@app/types';

jest.mock('@app/log/components/log_form', () => jest.fn());
jest.mock('@app/log/components/log_pile', () => jest.fn());

jest.mock('@app/project/selectors');
jest.mock('@app/log/actions');
jest.mock('@app/log//selectors');

const mockStore = configureMockStore<RootState>([]);

/**
 * LogApp component test.
 */
describe('LogApp', () => {
  let store: ReturnType<typeof mockStore>;

  // Typed mocks
  const mockGetCurrentProject = projectSelectors.getCurrentProject as jest.Mock;
  const mockGetPiles = logSelectors.getPiles as jest.Mock;
  const mockExportLog = logActions.exportLog as jest.Mock;

  // These are now correctly typed as Jest mock functions
  const MockLogForm = LogForm as jest.Mock;
  const MockLogPile = LogPile as unknown as jest.Mock;

  const testFormData: LogFormData = {
    logType: 'testLogType',
    archiveSize: 123,
    archiveUnit: 'MB',
    startDate: '2024-01-01',
    endDate: '2024-01-02',
    actionType: 'testAction',
  };

  beforeEach(() => {
    jest.clearAllMocks();

    // Default mock return values for selectors/actions
    mockGetCurrentProject.mockReturnValue('default-project');
    mockGetPiles.mockReturnValue({pileA: {}, pileB: {}});
    mockExportLog.mockReturnValue({type: 'MOCK_EXPORT_LOG_ACTION'});

    // Mock Child Component implementations
    MockLogForm.mockImplementation((
      props: {projectName: string, onSubmit: (data: LogFormData) => void},
    ) => (
      <div data-testid="log-form">
        <button
          data-testid="log-form-submit"
          onClick={() => props.onSubmit(testFormData)}
        >
          Submit-{props.projectName}
        </button>
      </div>
    ));
    MockLogPile.mockImplementation((
      props: {key: string, pileKey: string, projectName: string},
    ) => (
      <div data-testid={`log-pile-${props.pileKey}`}>
        Pile-{props.pileKey}-{props.projectName}
      </div>
    ));

    store = mockStore({} as RootState);
  });

  const renderWithStore = () => {
    return render(
      <Provider store={store}>
        <LogApp />
      </Provider>,
    );
  };

  test('should render LogForm and pass the correct projectName prop', () => {
    mockGetCurrentProject.mockReturnValue('special-project');
    renderWithStore();
    expect(MockLogForm).toHaveBeenCalledWith(expect.objectContaining({
      projectName: 'special-project',
    }), {});
    const submitButton = screen.getByTestId('log-form-submit');
    expect(submitButton.textContent).toBe('Submit-special-project');
  });

  test('should render LogPile components for each key', () => {
    mockGetPiles.mockReturnValue({key1: {}, key2: {}});
    mockGetCurrentProject.mockReturnValue('pile-project');
    renderWithStore();
    expect(MockLogPile).toHaveBeenCalledWith(expect.objectContaining({
      pileKey: 'key1', projectName: 'pile-project',
    }), {});
    expect(MockLogPile).toHaveBeenCalledWith(expect.objectContaining({
      pileKey: 'key2', projectName: 'pile-project',
    }), {});
    expect(MockLogPile).toHaveBeenCalledTimes(2);
  });

  test('should call exportLog on form submit', () => {
    mockGetCurrentProject.mockReturnValue('submit-project');
    renderWithStore();
    fireEvent.click(screen.getByTestId('log-form-submit'));
    expect(mockExportLog).toHaveBeenCalledWith(
      'submit-project',
      testFormData.logType,
      testFormData.archiveSize,
      testFormData.archiveUnit,
      testFormData.startDate,
      testFormData.endDate,
      testFormData.actionType,
    );
    expect(store.getActions()[0]).toEqual({type: 'MOCK_EXPORT_LOG_ACTION'});
  });
});
