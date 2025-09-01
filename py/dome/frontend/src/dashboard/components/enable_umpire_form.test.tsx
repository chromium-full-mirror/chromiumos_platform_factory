// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {reducer as formReducer} from 'redux-form';

import EnableUmpireForm from '@app/dashboard/components/enable_umpire_form';
import {ENABLE_UMPIRE_FORM} from '@app/dashboard/constants';
import {PortResponse} from '@app/dashboard/types';
import {Project} from '@app/project/types';

// Mocking formDialog selectors
jest.mock('@app/form_dialog', () => ({
  selectors: {
    isFormVisibleFactory: (formName: string) =>
      (state: any) => state.formDialog[formName]?.isOpen || false,
  },
}));

// Mocking getPorts selector
jest.mock('@app/dashboard/selectors', () => ({
  getPorts: (state: any) => state.ports,
}));

interface MockState {
  formDialog: {
    [key: string]: {isOpen: boolean};
  };
  ports: PortResponse;
  form: object;
}

/**
 * EnableUmpireForm component test.
 */
describe('EnableUmpireForm', () => {
  const mockOnCancel = jest.fn();
  const mockOnSubmit = jest.fn();

  const defaultProject: Project = {
    id: '1',
    name: 'Test Project',
    hasExistingUmpire: false,
    umpirePort: undefined,
  } as unknown as Project;

  const defaultPorts: PortResponse = {
    allPorts: [
      {
        name: 'OtherProject1', umpirePort: 9000,
        allPorts: [],
        maxPortOffset: 20,
      },
      {
        name: 'OtherProject2', umpirePort: 9090,
        allPorts: [],
        maxPortOffset: 20,
      },
    ],
    maxPortOffset: 20,
  };

  // Helper function to render the component with Redux Provider and a store
  const renderComponent = (project: Project, ports: PortResponse) => {
    const mockState: MockState = {
      formDialog: {[ENABLE_UMPIRE_FORM]: {isOpen: true}},
      ports,
      form: {},
    };

    // redux-form requires a real Redux store setup with its reducer
    const store = createStore(
      combineReducers({
        form: formReducer,
        ports: (state = mockState.ports) => state,
        formDialog: (state = mockState.formDialog) => state,
      }),
    );
    const dispatchSpy = jest.spyOn(store, 'dispatch');

    return {
      ...render(
        <Provider store={store}>
          <EnableUmpireForm
            project={project}
            onCancel={mockOnCancel}
            onSubmit={mockOnSubmit}
          />
        </Provider>,
      ),
      store,
      dispatchSpy,
    };
  };

  beforeEach(() => {
    // Clear mock call history before each test
    mockOnCancel.mockClear();
    mockOnSubmit.mockClear();
  });

  test('should render the dialog with title', () => {
    renderComponent(defaultProject, defaultPorts);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Enable Umpire')).toBeInTheDocument();
  });

  describe('when project has NO existing umpire', () => {
    const project = {...defaultProject, hasExistingUmpire: false};

    test('should show the port input field with default value 8080', () => {
      renderComponent(project, defaultPorts);
      const portInput = screen.getByLabelText('port');
      expect(portInput).toBeInTheDocument();
      expect(portInput).toHaveValue(8080);
      expect(screen.getByTestId('enable-confirm-btn'))
        .toHaveTextContent('Create');
    });
  });

  describe('when project has an existing umpire', () => {
    const project = {
      ...defaultProject,
      hasExistingUmpire: true,
      umpirePort: 6000,
    };

    test('should display existing info and NOT show the form input', () => {
      renderComponent(project, defaultPorts);
      const expectedMessage =
        `Umpire container for ${project.name} already exists, ` +
        `it would be added to Dome.`;
      expect(screen.getByText(expectedMessage)).toBeInTheDocument();
      expect(screen.queryByLabelText('port')).not.toBeInTheDocument();
      expect(screen.getByTestId('enable-confirm-btn')).toHaveTextContent('Add');
    });

    test('should call onSubmit with initialValues when Add is clicked', () => {
      renderComponent(project, defaultPorts);
      fireEvent.click(screen.getByTestId('enable-confirm-btn'));

      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    });
  });

  test('should call onCancel when the Cancel button is clicked', () => {
    renderComponent(defaultProject, defaultPorts);
    fireEvent.click(screen.getByText('Cancel'));
    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });
});
