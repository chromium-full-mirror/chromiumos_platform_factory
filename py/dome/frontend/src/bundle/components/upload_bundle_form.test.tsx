// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {reducer as formReducer} from 'redux-form';

import UploadBundleForm from '@app/bundle/components/upload_bundle_form';

// Mock the imported validateRequired to control its behavior/message
jest.mock('@common/form', () => ({
  ...jest.requireActual('@common/form'),
  validateRequired: (value: string) => (value ? undefined : 'Required'),
}));

// Helper function to create a mock Redux store
const createMockStore = (initialState = {}) => {
  return createStore(
    combineReducers({
      form: formReducer,
    }),
    initialState,
  );
};

interface RenderComponentOptions {
  bundleNames?: string[];
  onSubmit?: jest.Mock<any, any>;
}

const renderComponent = (options: RenderComponentOptions = {}) => {
  const {bundleNames = [], onSubmit = jest.fn()} = options;
  const store = createMockStore();

  const rendered = render(
    <Provider store={store}>
      <UploadBundleForm
        bundleNames={bundleNames}
        onSubmit={onSubmit}
      />
    </Provider>,
  );

  return {
    ...rendered,
    store,
    onSubmitMock: onSubmit,
  };
};

/**
 * UploadBundleForm component test.
 */
describe('UploadBundleForm', () => {
  test('should render the form fields', () => {
    renderComponent();
    expect(screen.getByLabelText('New Bundle Name')).toBeInTheDocument();
    expect(screen.getByLabelText('New Bundle Note')).toBeInTheDocument();
  });

  test('should show validation error if name is empty on submit', async () => {
    const {container, onSubmitMock} = renderComponent();
    const formElement = container.querySelector('form');
    expect(formElement).toBeInTheDocument();
    fireEvent.submit(formElement!);
    expect(await screen.findByText('Required')).toBeInTheDocument();
    expect(onSubmitMock).not.toHaveBeenCalled();
  });

  test('should show validation error if name is not unique', async () => {
    const existingName = 'test-bundle';
    const {container, onSubmitMock} = renderComponent({
      bundleNames: [existingName],
    });

    const nameInput = screen.getByLabelText('New Bundle Name');
    fireEvent.change(nameInput, {target: {value: existingName}});

    const formElement = container.querySelector('form');
    expect(formElement).toBeInTheDocument();
    fireEvent.submit(formElement!);

    expect(
      await screen.findByText(`${existingName} already exist`),
    ).toBeInTheDocument();
    expect(onSubmitMock).not.toHaveBeenCalled();
  });

  test('should call onSubmit with form data \
    when form is valid and submitted',
  async () => {
    const name = 'new-valid-bundle';
    const note = 'This is a note.';
    const onSubmitMock = jest.fn();
    const {container} = renderComponent({
      bundleNames: ['other-bundle'],
      onSubmit: onSubmitMock,
    });

    const nameInput = screen.getByLabelText('New Bundle Name');
    const noteInput = screen.getByLabelText('New Bundle Note');

    fireEvent.change(nameInput, {target: {value: name}});
    fireEvent.change(noteInput, {target: {value: note}});

    const formElement = container.querySelector('form');
    expect(formElement).toBeInTheDocument();
    fireEvent.submit(formElement!);

    await waitFor(() => {
      expect(onSubmitMock).toHaveBeenCalledTimes(1);
    });

    expect(onSubmitMock).toHaveBeenCalledWith(
      {name, note},
      expect.anything(),  // dispatch
      expect.anything(),  // props
    );
  });

  test('should allow submission if name is unique', async () => {
    const onSubmitMock = jest.fn();
    const {container} = renderComponent({
      bundleNames: ['existing-bundle'],
      onSubmit: onSubmitMock,
    });

    const nameInput = screen.getByLabelText('New Bundle Name');
    fireEvent.change(nameInput, {target: {value: 'unique-bundle'}});

    const formElement = container.querySelector('form');
    expect(formElement).toBeInTheDocument();
    fireEvent.submit(formElement!);

    await waitFor(() => {
      expect(onSubmitMock).toHaveBeenCalledTimes(1);
    });

    expect(onSubmitMock).toHaveBeenCalledWith(
      {name: 'unique-bundle', note: ''},
      expect.anything(),  // dispatch
      expect.anything(),  // props
    );
  });
});
