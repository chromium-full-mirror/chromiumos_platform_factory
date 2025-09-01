// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import DomeAppBar from '@app/dome_app/components/dome_app_bar';
import {getDomeInfo} from '@app/dome_app/selectors';
import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Mock the selector
jest.mock('../selectors', () => ({
  getDomeInfo: jest.fn(),
}));
// Mock the child component to isolate the test
jest.mock('./dome_info_component', () => {
  return jest.fn((props) => (
    <div data-testid="dome-info">
      <span data-testid="dome-info-name">{props.domeInfo?.name}</span>
      <span data-testid="dome-info-version">{props.domeInfo?.version}</span>
    </div>
  ));
});

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

const mockGetDomeInfo = getDomeInfo as jest.Mock;
const mockToggleAppMenu = jest.fn();
const theme = createTheme();

// Helper function to render the component with Redux Provider and ThemeProvider
const renderComponent = (initialState: Partial<RootState> = {}) => {
  const store = mockStore(initialState as RootState);
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <DomeAppBar toggleAppMenu={mockToggleAppMenu} />
      </ThemeProvider>
    </Provider>,
  );
};

/**
 * DomeAppBar component test.
 */
describe('DomeAppBar', () => {
  beforeEach(() => {
    // Reset mocks before each test
    mockToggleAppMenu.mockClear();
    mockGetDomeInfo.mockClear();
  });

  test('renders without crashing', () => {
    mockGetDomeInfo.mockReturnValue({version: '1.0', name: 'Test Dome'});
    renderComponent();
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  test('calls toggleAppMenu when the menu icon button is clicked', () => {
    mockGetDomeInfo.mockReturnValue({version: '1.0', name: 'Test Dome'});
    renderComponent();

    // The Menu IconButton is the first button in the AppBar
    const menuButton = screen.getAllByRole('button')[0];
    fireEvent.click(menuButton);

    expect(mockToggleAppMenu).toHaveBeenCalledTimes(1);
  });

  test('renders DomeInfoComponent and passes correct domeInfo prop', () => {
    const mockDomeInfo = {version: 'v2.1', name: 'FactoryDomeTest'};
    mockGetDomeInfo.mockReturnValue(mockDomeInfo);

    renderComponent();

    // Check that the mock DomeInfoComponent is rendered
    expect(screen.getByTestId('dome-info')).toBeInTheDocument();

    // Check if the props are passed correctly to the mocked DomeInfoComponent
    expect(screen.getByTestId('dome-info-name'))
      .toHaveTextContent(mockDomeInfo.name);
    expect(screen.getByTestId('dome-info-version'))
      .toHaveTextContent(mockDomeInfo.version);
  });
});
