// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';

import * as actions from '@app/factory_drives/actions';
import {
  RENAME_DIRECTORY_FORM,
  UPDATE_FACTORY_DRIVE_FORM,
} from '@app/factory_drives/constants';
import * as selectors from '@app/factory_drives/selector';
import {FactoryDrive} from '@app/factory_drives/types';
import formDialog from '@app/form_dialog';
import {RootState} from '@app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

import FactoryDriveList from './factory_drive_list';

// Mock MUI icons to prevent rendering issues in tests
jest.mock('@mui/icons-material/ArrowBack', () => () => 'ArrowBackIcon');

// Mock dependencies
jest.mock('@app/factory_drives/actions');
jest.mock('@app/factory_drives/selector');
jest.mock('@app/form_dialog', () => ({
  actions: {
    openForm: jest.fn(),
  },
  selectors: {
    isFormVisibleFactory: jest.fn(() => () => false),
    getFormPayloadFactory: jest.fn(() => () => ({})),
  },
}));

const theme = createTheme();
const mockStore = configureStore<RootState>([]);

/**
 * FactoryDriveList component test.
 */
describe('FactoryDriveList', () => {
  let store: any;
  let defaultProps: any;

  // Get typed mocks from the jest.mocked modules
  const mockFetchFactoryDrives = actions.fetchFactoryDrives as jest.Mock;
  const mockStartUpdateComponentVersion =
    actions.startUpdateComponentVersion as jest.Mock;
  const mockOpenForm = formDialog.actions.openForm as jest.Mock;
  const mockGetFactoryDrives = selectors.getFactoryDrives as jest.Mock;
  const mockGetFactoryDriveDirs = selectors.getFactoryDriveDirs as jest.Mock;
  const mockIsFormVisibleFactory =
    formDialog.selectors.isFormVisibleFactory as jest.Mock;
  const mockGetFormPayloadFactory =
    formDialog.selectors.getFormPayloadFactory as jest.Mock;

  const mockDirs: any[] = [
    {id: 1, name: 'Dir1', parentId: null},
    {id: 2, name: 'Dir2', parentId: null},
    {id: 3, name: 'SubDir1', parentId: 1},
  ];

  const mockDrives: FactoryDrive[] = [
    {id: 10, name: 'File1', dirId: null, revisions: [], usingVer: 0},
    {
      id: 11,
      name: 'File2',
      dirId: 1,
      revisions: ['path/file2.hash1', 'path/file2.hash2'],
      usingVer: 0,
    },
  ];

  beforeEach(() => {
    // Reset mock return values and calls for each test
    mockFetchFactoryDrives.mockReturnValue({type: 'MOCK_FETCH'});
    mockStartUpdateComponentVersion.mockReturnValue({
      type: 'MOCK_UPDATE_VERSION',
    });
    mockOpenForm.mockClear();
    mockGetFactoryDrives.mockReturnValue(mockDrives);
    mockGetFactoryDriveDirs.mockReturnValue(mockDirs);

    // Reset all mock functions in the formDialog mock
    mockIsFormVisibleFactory.mockImplementation(() => () => false);
    mockGetFormPayloadFactory.mockImplementation(() => () => ({}));

    store = mockStore({
      app: {
        display: {
          project: {
            currentProject: 'test-project',
            projects: {
              'test-project': {
                name: 'test-project',
                netbootBundle: 'test-bundle',
              },
            },
          },
        },
      },
    } as unknown as RootState);
    store.dispatch = jest.fn();

    defaultProps = {
      currentDirId: null,
      dirClicked: jest.fn(),
    };
  });

  const renderComponent = (props = defaultProps) => {
    return render(
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <FactoryDriveList {...props} />
        </ThemeProvider>
      </Provider>,
    );
  };

  test('renders without crashing and shows root elements', () => {
    renderComponent();
    expect(screen.getByText('Current directory: /')).toBeInTheDocument();
    expect(screen.getByText('Dir1')).toBeInTheDocument();
    expect(screen.getByText('Dir2')).toBeInTheDocument();
    expect(screen.getByText('File1')).toBeInTheDocument();
    expect(screen.queryByText('SubDir1')).not.toBeInTheDocument();
    expect(screen.queryByText('File2')).not.toBeInTheDocument();
  });

  test('fetches factory drives on mount', () => {
    renderComponent();
    expect(store.dispatch).toHaveBeenCalledWith({type: 'MOCK_FETCH'});
  });

  test('calls dirClicked when a directory button is clicked', () => {
    renderComponent();
    fireEvent.click(screen.getByRole('button', {name: 'Dir1'}));
    expect(defaultProps.dirClicked).toHaveBeenCalledWith(1);
  });

  test('navigates back when back button is clicked from a subdirectory', () => {
    renderComponent({...defaultProps, currentDirId: 1});

    const backButton = screen.getByRole('button', {name: /ArrowBackIcon/i});
    fireEvent.click(backButton);
    expect(defaultProps.dirClicked).toHaveBeenCalledWith(null);
  });

  test('opens rename directory form when rename is clicked', () => {
    renderComponent();
    const renameButton = screen.getAllByRole('button', {name: 'Rename'});
    fireEvent.click(renameButton[0]);
    expect(mockOpenForm).toHaveBeenCalledWith(RENAME_DIRECTORY_FORM, {
      id: 1,
      name: 'Dir2',
    });
  });

  test('opens update factory drive form when update is clicked', () => {
    renderComponent();
    const updateButton = screen.getByRole('button', {name: 'Update'});
    fireEvent.click(updateButton);
    expect(mockOpenForm).toHaveBeenCalledWith(UPDATE_FACTORY_DRIVE_FORM, {
      id: 10,
      dirId: null,
      name: 'File1',
      multiple: false,
    });
  });

  describe('Revision Dialog', () => {
    test('opens when version icon is clicked', async () => {
      mockGetFactoryDrives.mockReturnValue([mockDrives[1]]);
      renderComponent({...defaultProps, currentDirId: 1});

      const versionButton = screen.getByRole('button', {name: 'Versions'});
      fireEvent.click(versionButton);

      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
    });
  });
});
