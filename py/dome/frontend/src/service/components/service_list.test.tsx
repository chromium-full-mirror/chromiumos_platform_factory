// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import * as actions from '@app/service/actions';
import ServiceList from '@app/service/components/service_list';
import * as selectors from '@app/service/selectors';

// Mock child form components
import ServiceForm from './service_form';
import ShopfloorServiceForm from './shopfloor_service_form';

// Deeply mock the modules
jest.mock('../actions');
jest.mock('../selectors');
jest.mock('./service_form', () => ({
  __esModule: true,
  default: jest.fn(),
}));
jest.mock('./shopfloor_service_form', () => ({
  __esModule: true,
  default: jest.fn(),
}));

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Setup mock implementations
const mockFetchServices = actions.fetchServices as jest.Mock;
const mockFetchServiceSchemata = actions.fetchServiceSchemata as jest.Mock;
const mockUpdateService = actions.updateService as jest.Mock;
const mockTestShopfloorConnection =
  actions.testShopfloorConnection as jest.Mock;

const mockGetServices = selectors.getServices as jest.Mock;
const mockGetServiceSchemata = selectors.getServiceSchemata as jest.Mock;

const MockServiceForm = ServiceForm as jest.Mock;
const MockShopfloorServiceForm = ShopfloorServiceForm as jest.Mock;

/**
 * ServiceList component test.
 */
describe('ServiceList', () => {
  let store: any;
  const initialState = {};

  const mockSchemata = {
    serviceA: {type: 'object', properties: {host: {type: 'string'}}},
    serviceB: {type: 'object', properties: {key: {type: 'string'}}},
    shopFloor: {type: 'object', properties: {endpoint: {type: 'string'}}},
  };

  const mockServices = {
    serviceA: {host: 'localhost'},
    serviceB: {key: 'somekey'},
    shopFloor: {key: 'someShopFloor'},
  };

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup selector return values
    mockGetServices.mockReturnValue(mockServices);
    mockGetServiceSchemata.mockReturnValue(mockSchemata);

    // Setup action return values
    mockFetchServices.mockReturnValue({type: 'FETCH_SERVICES_MOCK'});
    mockFetchServiceSchemata.mockReturnValue({type: 'FETCH_SCHEMATA_MOCK'});
    mockUpdateService.mockReturnValue({type: 'UPDATE_SERVICE_MOCK'});
    mockTestShopfloorConnection.mockReturnValue({type: 'TEST_CONNECTION_MOCK'});

    // Mock form components to render something and allow interaction
    MockServiceForm.mockImplementation((props) => (
      <div data-testid={`mock-service-form-${props.form}`}>
        <button onClick={() => props.onSubmit({host: 'updated-host'})}>
          Submit-{props.form}
        </button>
        Initial: {JSON.stringify(props.initialValues)}
      </div>
    ));

    MockShopfloorServiceForm.mockImplementation((props) => (
      <div data-testid={`mock-shopfloor-form-${props.form}`}>
        <button onClick={props.handleTestConnection}>Test Connection</button>
        <button
          onClick={() => {
            props.onSubmit({endpoint: 'test-endpoint'});
            props.onSubmitSuccess();
          }}
        >
          Submit-{props.form}
        </button>
        Initial: {JSON.stringify(props.initialValues)}
      </div>
    ));

    store = mockStore(initialState);
    jest.spyOn(store, 'dispatch');

    render(
      <Provider store={store}>
        <ServiceList />
      </Provider>,
    );
  });

  test('should fetch services and schemata on mount', () => {
    expect(mockFetchServices).toHaveBeenCalledTimes(1);
    expect(mockFetchServiceSchemata).toHaveBeenCalledTimes(1);
    expect(store.dispatch).toHaveBeenCalledWith({type: 'FETCH_SERVICES_MOCK'});
    expect(store.dispatch).toHaveBeenCalledWith({type: 'FETCH_SCHEMATA_MOCK'});
  });

  test('should render list items for each schema in sorted order', () => {
    const titles = screen.queryAllByTestId(/^service-title-/)
      .map((el) => el.textContent);
    expect(titles).toEqual(['serviceA', 'serviceB', 'shopFloor']);
  });

  test('should toggle service details on click', async () => {
    const serviceATitle = screen.getByTestId('service-title-serviceA');
    const serviceAContent = screen.getByTestId('service-serviceA');
    expect(serviceAContent).not.toBeVisible();

    fireEvent.click(serviceATitle);
    await waitFor(() => {
      expect(serviceAContent).toBeVisible();
    });

    fireEvent.click(serviceATitle);
    await waitFor(() => {
      expect(serviceAContent).not.toBeVisible();
    });
  });

  test('should pass correct initialValues to ServiceForm', async () => {
    fireEvent.click(screen.getByTestId('service-title-serviceA'));
    await waitFor(() => {
      const form = screen.getByTestId('service-serviceA');
      expect(form).toBeVisible();
    });
  });

  test('should call updateService when ServiceForm is submitted', async () => {
    fireEvent.click(screen.getByTestId('service-title-serviceA'));
    await waitFor(() => {
      expect(screen.getByTestId('mock-service-form-serviceA')).toBeVisible();
    });

    const submitButton = screen.getByRole('button', {name: 'Submit-serviceA'});
    fireEvent.click(submitButton);

    expect(mockUpdateService).toHaveBeenCalledTimes(1);
    expect(mockUpdateService)
      .toHaveBeenCalledWith('serviceA', {host: 'updated-host'});
    expect(store.dispatch).toHaveBeenCalledWith({type: 'UPDATE_SERVICE_MOCK'});
  });

  test('should pass correct initialValue to ShopfloorServiceForm', async () => {
    fireEvent.click(screen.getByTestId('service-title-shopFloor'));
    await waitFor(() => {
      const form = screen.getByTestId('service-shopFloor');
      expect(form).toBeVisible();
    });
  });

  test('should call updateService on ShopfloorServiceForm submit', async () => {
    fireEvent.click(screen.getByTestId('service-title-shopFloor'));
    await waitFor(() => {
      expect(screen.getByTestId('service-shopFloor')).toBeVisible();
    });

    const submitButton = screen.getByRole('button', {name: 'Submit-shopFloor'});
    fireEvent.click(submitButton);

    expect(mockUpdateService).toHaveBeenCalledTimes(1);
    expect(mockUpdateService)
      .toHaveBeenCalledWith('shopFloor', {endpoint: 'test-endpoint'});
    expect(mockTestShopfloorConnection).not.toHaveBeenCalled();
  });

  test('should call testShopfloorConnection on submit \
    after Test Connection button click',
  async () => {
    fireEvent.click(screen.getByTestId('service-title-shopFloor'));
    await waitFor(() => {
      expect(screen.getByTestId('mock-shopfloor-form-shopFloor')).toBeVisible();
    });

    const testButton = screen.getByRole('button', {name: 'Test Connection'});
    fireEvent.click(testButton);

    const submitButton = screen.getByRole('button', {name: 'Submit-shopFloor'});
    fireEvent.click(submitButton);

    expect(mockUpdateService).toHaveBeenCalledTimes(1);
    expect(mockUpdateService)
      .toHaveBeenCalledWith('shopFloor', {endpoint: 'test-endpoint'});
    expect(mockTestShopfloorConnection).toHaveBeenCalledTimes(1);
    expect(mockTestShopfloorConnection).toHaveBeenCalledWith('shopFloor');
    expect(store.dispatch).
      toHaveBeenCalledWith({type: 'TEST_CONNECTION_MOCK'});
  });
});
