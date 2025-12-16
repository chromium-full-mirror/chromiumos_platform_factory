// Copyright 2026 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {Store} from 'redux';
import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import * as actions from '@app/project/actions';
import ProjectsApp from '@app/project/components/projects_app';
import * as selectors from '@app/project/selectors';
import {Project} from '@app/project/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

// Mock the modules
jest.mock('../actions', () => ({
  createProject: jest.fn(),
  deleteProject: jest.fn(),
  fetchProjects: jest.fn(),
  switchProject: jest.fn(),
}));

jest.mock('../selectors', () => ({
  getProjects: jest.fn(),
}));

jest.mock('redux-form', () => ({
  ...jest.requireActual('redux-form'),
  reset: jest.fn(),
}));

const mockedActions = actions as jest.Mocked<typeof actions>;
const mockedSelectors = selectors as jest.Mocked<typeof selectors>;

const middlewares = [thunk];
const mockStore = configureMockStore(middlewares);

// Helper function to create a mock Project object with default values
const createMockProject = (overrides: Partial<Project> = {}): Project => ({
  name: 'DefaultProject',
  isAndroid: false,
  umpireReady: false,
  umpireEnabled: false,
  umpirePort: null,
  netbootBundle: null,
  hasExistingUmpire: false,
  ...overrides,
});

/**
 * ProjectsApp component test.
 */
describe('ProjectsApp', () => {
  const theme = createTheme();
  let store: Store;

  beforeEach(() => {
    jest.clearAllMocks();

    // Default empty projects
    mockedSelectors.getProjects.mockReturnValue({});

    store = mockStore({
      form: {},
    });

    store.dispatch = jest.fn();
  });

  const renderComponent = () =>
    render(
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <ProjectsApp />
        </ThemeProvider>
      </Provider>,
    );

  it('should render the component and fetch projects on mount', () => {
    renderComponent();
    expect(screen.getByText('Project list')).toBeInTheDocument();
    expect(mockedActions.fetchProjects).toHaveBeenCalledTimes(1);
  });

  it('should display "no projects" message when project list is empty', () => {
    mockedSelectors.getProjects.mockReturnValue({});
    renderComponent();
    expect(screen.getByTestId('no-projects')).toBeInTheDocument();
    expect(
      screen.getByText('no projects, create or add an existing one'),
    ).toBeInTheDocument();
  });

  it('should display list of projects when available', () => {
    mockedSelectors.getProjects.mockReturnValue({
      ProjectA: createMockProject({name: 'ProjectA', isAndroid: false}),
      ProjectB: createMockProject({name: 'ProjectB', isAndroid: true}),
    });
    renderComponent();

    expect(screen.queryByTestId('no-projects')).not.toBeInTheDocument();
    expect(screen.getByText('ProjectA')).toBeInTheDocument();
    expect(screen.getByText('ProjectB (Android)')).toBeInTheDocument();
    expect(
      screen.getAllByRole('button', {name: 'delete this project'}),
    ).toHaveLength(2);
  });

  it('should call switchProject when a project item is clicked', () => {
    mockedSelectors.getProjects.mockReturnValue({
      ProjectA: createMockProject({name: 'ProjectA'}),
    });
    renderComponent();

    const projectItem = screen.getByText('ProjectA');
    fireEvent.click(projectItem);

    expect(mockedActions.switchProject).toHaveBeenCalledTimes(1);
    expect(mockedActions.switchProject).toHaveBeenCalledWith('ProjectA');
  });

  describe('Delete Project Dialog', () => {
    beforeEach(() => {
      mockedSelectors.getProjects.mockReturnValue({
        TestProject: createMockProject({name: 'TestProject'}),
      });
    });

    it('should open confirmation dialog when delete icon is clicked', () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', {
        name: 'delete this project',
      });
      fireEvent.click(deleteButton);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Alert')).toBeInTheDocument();
      expect(
        screen.getByText(/All files .* will be deleted/),
      ).toBeInTheDocument();
    });

    it('should close dialog when Cancel is clicked', async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', {
        name: 'delete this project',
      });
      fireEvent.click(deleteButton);

      const cancelButton = screen.getByRole('button', {name: 'Cancel'});
      fireEvent.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
      expect(mockedActions.deleteProject).not.toHaveBeenCalled();
    });

    it('should call deleteProject and close dialog when \
      OK is clicked',
    async () => {
      renderComponent();
      const deleteButton = screen.getByRole('button', {
        name: 'delete this project',
      });
      fireEvent.click(deleteButton);

      const okButton = screen.getByRole('button', {name: 'OK'});
      fireEvent.click(okButton);

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
      expect(mockedActions.deleteProject).toHaveBeenCalledTimes(1);
      expect(mockedActions.deleteProject).toHaveBeenCalledWith('TestProject');
    });
  });
});
