// Copyright 2026 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, within} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore, Store} from 'redux';
import {reducer as formReducer} from 'redux-form';

import LogForm from '@app/log/components/log_form';
import * as selectors from '@app/log/selectors';
import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Mock the selectors
jest.mock('@app/log/selectors', () => ({
  getDefaultDownloadStartDate: jest.fn(),
  getDefaultDownloadEndDate: jest.fn(),
}));

const mockGetDefaultDownloadStartDate =
  selectors.getDefaultDownloadStartDate as jest.Mock;
const mockGetDefaultDownloadEndDate =
  selectors.getDefaultDownloadEndDate as jest.Mock;

const rootReducer = combineReducers({
  form: formReducer,
});

const theme = createTheme();

const mockStartDate = '2023-01-05';
const mockEndDate = '2023-01-10';
const createTestStore = (initialStateOverrides = {}) => {
  const initialState = {
    form: {
      logForm: {
        values: {
          logType: 'log', // Ensure logType is initialized
          archiveSize: 200,
          archiveUnit: 'MB',
          startDate: mockGetDefaultDownloadStartDate(),
          endDate: mockGetDefaultDownloadEndDate(),
          actionType: '',
        },
      },
    },
    ...initialStateOverrides,
  };
  return createStore(rootReducer, initialState as unknown as RootState);
};

interface RenderProps {
  projectName: string;
  onSubmit: jest.Mock;
}

// Helper function to render the component with necessary providers
const renderComponent = (
  store: Store<any, any>,
  partialProps: Partial<RenderProps> = {},
) => {
  const defaultProps: RenderProps = {
    projectName: 'test-project',
    onSubmit: jest.fn(),
  };
  const props = {...defaultProps, ...partialProps};

  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <LogForm {...props} />
      </ThemeProvider>
    </Provider>,
  );
};

/**
 * LogForm component test.
 */
describe('LogForm', () => {
  let store: Store<any, any>;
  let onSubmitMock: jest.Mock;

  beforeEach(() => {
    mockGetDefaultDownloadStartDate.mockReturnValue(mockStartDate);
    mockGetDefaultDownloadEndDate.mockReturnValue(mockEndDate);
    // Now the store will be created with initial form values
    store = createTestStore();
    onSubmitMock = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Action Type: Download', () => {
    beforeEach(() => {
      renderComponent(store, {onSubmit: onSubmitMock});
      // Select 'download' action type
      fireEvent.mouseDown(screen.getByLabelText('action type'));
      fireEvent.click(screen.getByRole('option', {name: 'download'}));
    });

    it('should show download specific fields for "log" type', () => {
      expect(screen.getByLabelText('size')).toBeInTheDocument();
      expect(screen.getByLabelText('unit')).toBeInTheDocument();
      expect(screen.getByLabelText('start date')).toBeInTheDocument();
      expect(screen.getByLabelText('end date')).toBeInTheDocument();
      expect(
        screen.getByRole('button', {name: 'Download'}),
      ).toBeInTheDocument();
    });

    it('should call onSubmit with form values when \
      Download button is clicked',
    () => {
      const sizeInput = screen.getByLabelText('size');
      fireEvent.change(sizeInput, {target: {value: '150'}});

      fireEvent.mouseDown(screen.getByLabelText('unit'));
      fireEvent.click(screen.getByRole('option', {name: 'GB'}));

      fireEvent.click(screen.getByRole('button', {name: 'Download'}));

      expect(onSubmitMock).toHaveBeenCalledTimes(1);
      expect(onSubmitMock).toHaveBeenCalledWith(
        expect.objectContaining({
          logType: 'log',
          actionType: 'download',
          archiveSize: '150',
          archiveUnit: 'GB',
          startDate: mockStartDate,
          endDate: mockEndDate,
        }),
        expect.anything(),
        expect.anything(),
      );
    });
  });

  describe('Action Type: Cleanup', () => {
    beforeEach(() => {
      renderComponent(store, {onSubmit: onSubmitMock});
      // Select 'cleanup' action type
      fireEvent.mouseDown(screen.getByLabelText('action type'));
      fireEvent.click(screen.getByRole('option', {name: 'cleanup'}));
    });

    it('should show cleanup specific fields for "log" type', () => {
      expect(screen.getByLabelText('start date')).toBeInTheDocument();
      expect(screen.getByLabelText('end date')).toBeInTheDocument();
      expect(
        screen.getByRole('button', {name: /Delete log file/i}),
      ).toBeInTheDocument();
    });

    it('should hide date fields for "csv" type', () => {
      fireEvent.click(
        screen.getByRole('tab', {name: 'csv (echo code inside)'}),
      );
      expect(
        screen.getByRole('button', {name: /Delete csv file/i}),
      ).toBeInTheDocument();
    });

    it('should open confirmation dialog on delete button click', () => {
      fireEvent.click(screen.getByRole('button', {name: /Delete log file/i}));
      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
      expect(
        within(dialog).getByText(
          'All files will be deleted permanently. Do you want to continue?',
        ),
      ).toBeInTheDocument();
    });

    it('should call onSubmit when OK in dialog is clicked', () => {
      fireEvent.click(screen.getByRole('button', {name: /Delete log file/i}));
      const dialog = screen.getByRole('dialog');
      fireEvent.click(within(dialog).getByRole('button', {name: 'OK'}));

      expect(onSubmitMock).toHaveBeenCalledTimes(1);
      expect(onSubmitMock).toHaveBeenCalledWith(
        expect.objectContaining({
          logType: 'log',
          actionType: 'cleanup',
          startDate: mockStartDate,
          endDate: mockEndDate,
        }),
        expect.anything(),
        expect.anything(),
      );
    });
  });

  describe('Validation', () => {
    beforeEach(() => {
      renderComponent(store, {onSubmit: onSubmitMock});
      fireEvent.mouseDown(screen.getByLabelText('action type'));
      fireEvent.click(screen.getByRole('option', {name: 'download'}));
    });

    it('should show error if archiveSize is empty', async () => {
      const sizeInput = screen.getByLabelText('size');
      fireEvent.change(sizeInput, {target: {value: ''}});
      fireEvent.click(screen.getByRole('button', {name: 'Download'}));
      expect(await screen.findByText('required')).toBeInTheDocument();
    });

    it('should show error if archiveSize is zero', async () => {
      const sizeInput = screen.getByLabelText('size');
      fireEvent.change(sizeInput, {target: {value: '0'}});
      fireEvent.click(screen.getByRole('button', {name: 'Download'}));
      expect(
        await screen.findByText('archive size must be larger than 0'),
      ).toBeInTheDocument();
    });

    it('should show error if start date is after end date', async () => {
      const startDateInput = screen.getByLabelText('start date');
      const endDateInput = screen.getByLabelText('end date');

      fireEvent.change(startDateInput, {target: {value: '2023-01-11'}});
      fireEvent.change(endDateInput, {target: {value: '2023-01-10'}});

      fireEvent.click(screen.getByRole('button', {name: 'Download'}));

      const errorMessages = await screen.findAllByText(
        'start date must be before end date',
      );
      expect(errorMessages.length).toBeGreaterThanOrEqual(1);
    });
  });
});
