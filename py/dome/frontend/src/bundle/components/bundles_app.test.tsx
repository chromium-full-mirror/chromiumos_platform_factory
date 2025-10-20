// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import BundlesApp from '@app/bundle/components/bundles_app';
import {UPLOAD_BUNDLE_FORM} from '@app/bundle/constants';
import formDialog from '@app/form_dialog';
import {RootState} from '@app/types';

// Mock child components to isolate the test to BundlesApp
jest.mock('./bundle_list', () => () => <div>MockedBundleList</div>);
jest.mock('./resources_gc', () => () => <div>MockedResourcesGCButton</div>);
jest.mock(
  './update_resource_dialog',
  () => () => <div>MockedUpdateResourceDialog</div>,
);
jest.mock(
  './upload_bundle_dialog',
  () => () => <div>MockedUploadBundleDialog</div>,
);

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureMockStore<Partial<RootState>>(middlewares);

/**
 * BundlesApp component test.
 */
describe('BundlesApp', () => {
  let store: any;

  beforeEach(() => {
    // Initialize a new mock store for each test
    store = mockStore({});
    // Spy on the dispatch function
    jest.spyOn(store, 'dispatch').mockImplementation(() => undefined);
    // Spy on formDialog.actions.openForm
    jest.spyOn(formDialog.actions, 'openForm')
      .mockReturnValue({type: 'MOCK_OPEN_FORM'} as any);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = (
    props: Partial<React.ComponentProps<typeof BundlesApp>> = {},
  ) => {
    const defaultProps = {
      overlay: null,
    };
    return render(
      <Provider store={store}>
        <BundlesApp {...defaultProps} {...props} />
      </Provider>,
    );
  };

  test('should render child components', () => {
    renderComponent();
    expect(screen.getByText('MockedBundleList')).toBeInTheDocument();
    expect(screen.getByText('MockedUploadBundleDialog')).toBeInTheDocument();
    expect(screen.getByText('MockedUpdateResourceDialog')).toBeInTheDocument();
  });

  test('should not render Portal elements when overlay is not provided', () => {
    renderComponent({overlay: null});
    expect(screen.queryByTestId('upload-factory-bundle'))
      .not.toBeInTheDocument();
    expect(screen.queryByText('MockedResourcesGCButton'))
      .not.toBeInTheDocument();
  });

  describe('when overlay is provided', () => {
    let overlayDiv: HTMLDivElement;

    beforeEach(() => {
      // Create a div to act as the overlay container
      overlayDiv = document.createElement('div');
      overlayDiv.id = 'overlay-container';
      document.body.appendChild(overlayDiv);
    });

    afterEach(() => {
      document.body.removeChild(overlayDiv);
    });

    test('should render Fab button and ResourcesGarbageCollectionButton \
      in Portal',
    () => {
      renderComponent({overlay: overlayDiv});

      expect(screen.getByTestId('upload-factory-bundle')).toBeInTheDocument();
      expect(screen.getByText('MockedResourcesGCButton')).toBeInTheDocument();

      // Optionally, check if they are in the correct container
      expect(overlayDiv.contains(screen.getByTestId('upload-factory-bundle')))
        .toBe(true);
      expect(overlayDiv.contains(screen.getByText('MockedResourcesGCButton')))
        .toBe(true);
    });

    test('should dispatch openUploadNewBundleForm action when \
      Fab button is clicked',
    () => {
      renderComponent({overlay: overlayDiv});

      const uploadButton = screen.getByTestId('upload-factory-bundle');
      fireEvent.click(uploadButton);

      expect(formDialog.actions.openForm)
        .toHaveBeenCalledWith(UPLOAD_BUNDLE_FORM);
      expect(store.dispatch).toHaveBeenCalledWith({type: 'MOCK_OPEN_FORM'});
    });
  });
});
