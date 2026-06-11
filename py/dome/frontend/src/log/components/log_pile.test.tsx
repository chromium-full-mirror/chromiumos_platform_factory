// Copyright 2026 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, within} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {createStore, Store} from 'redux';

import LogPile from '@app/log/components/log_pile';
import rootReducer from '@app/root_reducer';
import {createTheme, ThemeProvider} from '@mui/material/styles';

import * as actions from '../actions';

jest.mock('../actions', () => {
  const originalModule = jest.requireActual('../actions');
  return {
    ...originalModule,
    expandLogPile: jest.fn((key) => ({
      type: 'EXPAND_DOWNLOAD_COMPONENT',
      payload: {key},
    })),
    collapseLogPile: jest.fn((key) => ({
      type: 'COLLAPSE_DOWNLOAD_COMPONENT',
      payload: {key},
    })),
    removeLogPile: jest.fn((key) => ({
      type: 'REMOVE_DOWNLOAD_PILE',
      payload: {key},
    })),
    downloadLog: jest.fn(() => ({
      type: 'MOCK_DOWNLOAD_LOG',
    })),
    downloadLogs: jest.fn(() => ({
      type: 'MOCK_DOWNLOAD_LOGS',
    })),
    removeDownloadFile: jest.fn((key, file) => ({
      type: 'REMOVE_DOWNLOAD_FILE',
      payload: {key, file},
    })),
    removeDownloadFiles: jest.fn((key) => ({
      type: 'REMOVE_DOWNLOAD_FILES',
      payload: {key},
    })),
    deleteDirectory: jest.fn(),
  };
});

const mockExpandLogPile = actions.expandLogPile as jest.Mock;
const mockCollapseLogPile = actions.collapseLogPile as jest.Mock;
const mockDownloadLog = actions.downloadLog as jest.Mock;
const mockDownloadLogs = actions.downloadLogs as jest.Mock;
const mockRemoveDownloadFile = actions.removeDownloadFile as jest.Mock;
const mockRemoveDownloadFiles = actions.removeDownloadFiles as jest.Mock;
const mockDeleteDirectory = actions.deleteDirectory as jest.Mock;

const theme = createTheme();

const createTestStore = (pilesOverride?: any, expandedOverride?: any) => {
  const piles = pilesOverride || {
    'test-pile-key': {
      title: 'Test Pile Title',
      tempDir: 'test-temp-dir',
      projectName: 'test-project',
      compressState: 'SUCCEEDED',
      compressReports: ['compress-report.log'],
      cleanupState: 'WAITING',
      cleanupReports: [],
      downloadStateMap: {
        'file1.log': 'SUCCEEDED',
        'file2.log': 'FAILED',
      },
      actionType: 'download',
    },
  };
  const expanded = expandedOverride !== undefined ? expandedOverride : {
    'test-pile-key': true,
  };

  const logState = {
    defaultDownloadDate: {} as any,
    piles,
    expanded,
  };

  const initialState = {
    app: {
      display: {
        log: logState,
      },
      real: {
        log: logState,
      },
    },
  };
  return createStore(rootReducer, initialState as any);
};

const renderComponent = (
  store: Store<any, any>,
  pileKey = 'test-pile-key',
) => {
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <LogPile pileKey={pileKey} projectName="test-project" />
      </ThemeProvider>
    </Provider>,
  );
};

/**
 * LogPile component test.
 */
describe('LogPile', () => {
  let store: Store<any, any>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Render & UI structure', () => {
    test('should render header and download sections correctly when expanded',
      () => {
      store = createTestStore();
      renderComponent(store);

      expect(screen.getByText('Test Pile Title')).toBeInTheDocument();
      expect(screen.getByText('compress')).toBeInTheDocument();
      expect(screen.getByText('compress-report.log')).toBeInTheDocument();
      expect(screen.getByText('download')).toBeInTheDocument();
      expect(screen.getByText('test-project-file1.log')).toBeInTheDocument();
      expect(screen.getByText('test-project-file2.log')).toBeInTheDocument();
    });

    test('should not show sections if expanded is false', () => {
      store = createTestStore({
        'test-pile-key': {
          title: 'Test Pile Title',
          tempDir: 'test-temp-dir',
          projectName: 'test-project',
          compressState: 'SUCCEEDED',
          compressReports: ['compress-report.log'],
          cleanupState: 'WAITING',
          cleanupReports: [],
          downloadStateMap: {
            'file1.log': 'SUCCEEDED',
          },
          actionType: 'download',
        },
      }, {
        'test-pile-key': false,
      });
      renderComponent(store);

      expect(screen.getByText('Test Pile Title')).toBeInTheDocument();
      expect(screen.getByText('compress')).not.toBeVisible();
    });
  });

  describe('Toggle Expand', () => {
    test('should collapse pile when clicking toggle while expanded', () => {
      store = createTestStore();
      renderComponent(store);

      const toggleBtn = screen.getByTestId('ExpandLessIcon').closest('button')!;
      fireEvent.click(toggleBtn);

      expect(mockCollapseLogPile).toHaveBeenCalledTimes(1);
      expect(mockCollapseLogPile).toHaveBeenCalledWith('test-pile-key');
    });

    test('should expand pile when clicking toggle while collapsed', () => {
      store = createTestStore({
        'test-pile-key': {
          title: 'Test Pile Title',
          tempDir: 'test-temp-dir',
          projectName: 'test-project',
          compressState: 'SUCCEEDED',
          compressReports: [],
          cleanupState: 'WAITING',
          cleanupReports: [],
          downloadStateMap: {},
          actionType: 'download',
        },
      }, {
        'test-pile-key': false,
      });
      renderComponent(store);

      const toggleBtn = screen.getByTestId('ExpandMoreIcon').closest('button')!;
      fireEvent.click(toggleBtn);

      expect(mockExpandLogPile).toHaveBeenCalledTimes(1);
      expect(mockExpandLogPile).toHaveBeenCalledWith('test-pile-key');
    });
  });

  describe('Download specific actions', () => {
    test('should retry all failed downloads when download item retry clicked',
      () => {
      store = createTestStore();
      renderComponent(store);

      const downloadContainer = screen
        .getByText('download')
        .closest('.MuiCardContent-root') as HTMLElement;
      const retryBtn = within(downloadContainer)
        .getByLabelText('retry')
        .querySelector('button')!;
      fireEvent.click(retryBtn);

      expect(mockDownloadLogs).toHaveBeenCalledTimes(1);
      expect(mockDownloadLogs).toHaveBeenCalledWith(
        'test-project',
        'test-temp-dir',
        ['file2.log'],
        'test-pile-key',
      );
    });

    test('should remove download files and delete directory ' +
      'when download item remove clicked', () => {
      store = createTestStore();
      renderComponent(store);

      const downloadContainer = screen
        .getByText('download')
        .closest('.MuiCardContent-root') as HTMLElement;
      const removeBtn = within(downloadContainer)
        .getByLabelText('remove')
        .querySelector('button')!;
      fireEvent.click(removeBtn);

      expect(mockRemoveDownloadFiles).toHaveBeenCalledTimes(1);
      expect(mockRemoveDownloadFiles).toHaveBeenCalledWith('test-pile-key');
      expect(mockDeleteDirectory).toHaveBeenCalledTimes(1);
      expect(mockDeleteDirectory)
        .toHaveBeenCalledWith('test-project', 'test-temp-dir');
    });

    test('should retry single file download', () => {
      store = createTestStore();
      renderComponent(store);

      const file2Container = screen
        .getByText('test-project-file2.log')
        .closest('.MuiCardContent-root') as HTMLElement;
      const retryBtn = within(file2Container)
        .getByLabelText('retry')
        .querySelector('button')!;
      fireEvent.click(retryBtn);

      expect(mockDownloadLog).toHaveBeenCalledTimes(1);
      expect(mockDownloadLog).toHaveBeenCalledWith(
        'test-project',
        'test-temp-dir',
        'file2.log',
        'test-pile-key',
      );
    });

    test('should remove single download file without deleting directory ' +
      'if overall state is FAILED', () => {
      store = createTestStore();
      renderComponent(store);

      const file2Container = screen
        .getByText('test-project-file2.log')
        .closest('.MuiCardContent-root') as HTMLElement;
      const removeBtn = within(file2Container)
        .getByLabelText('remove')
        .querySelector('button')!;
      fireEvent.click(removeBtn);

      expect(mockRemoveDownloadFile).toHaveBeenCalledTimes(1);
      expect(mockRemoveDownloadFile)
        .toHaveBeenCalledWith('test-pile-key', 'file2.log');
      expect(mockDeleteDirectory).not.toHaveBeenCalled();
    });

    test('should remove single download file and delete directory ' +
      'if overall state is SUCCEEDED', () => {
      store = createTestStore({
        'test-pile-key': {
          title: 'Test Pile Title',
          tempDir: 'test-temp-dir',
          projectName: 'test-project',
          compressState: 'SUCCEEDED',
          compressReports: ['compress-report.log'],
          cleanupState: 'WAITING',
          cleanupReports: [],
          downloadStateMap: {
            'file1.log': 'SUCCEEDED',
          },
          actionType: 'download',
        },
      });
      renderComponent(store);

      const file1Container = screen
        .getByText('test-project-file1.log')
        .closest('.MuiCardContent-root') as HTMLElement;
      const removeBtn = within(file1Container)
        .getByLabelText('remove')
        .querySelector('button')!;
      fireEvent.click(removeBtn);

      expect(mockRemoveDownloadFile).toHaveBeenCalledTimes(1);
      expect(mockRemoveDownloadFile)
        .toHaveBeenCalledWith('test-pile-key', 'file1.log');
      expect(mockDeleteDirectory).toHaveBeenCalledTimes(1);
      expect(mockDeleteDirectory)
        .toHaveBeenCalledWith('test-project', 'test-temp-dir');
    });
  });

  describe('Cleanup actionType', () => {
    test('should render status and reports correctly', () => {
      store = createTestStore({
        'test-pile-key': {
          title: 'Cleanup Pile Title',
          tempDir: '',
          projectName: 'test-project',
          compressState: 'WAITING',
          compressReports: [],
          cleanupState: 'SUCCEEDED',
          cleanupReports: ['cleanup-report-1.log'],
          downloadStateMap: {},
          actionType: 'cleanup',
        },
      });
      renderComponent(store);

      expect(screen.getByText('Cleanup Pile Title')).toBeInTheDocument();
      expect(screen.getByText('status')).toBeInTheDocument();
      expect(screen.getByText('cleanup-report-1.log')).toBeInTheDocument();
      expect(screen.queryByText('compress')).not.toBeInTheDocument();
      expect(screen.queryByText('download')).not.toBeInTheDocument();
    });
  });
});
