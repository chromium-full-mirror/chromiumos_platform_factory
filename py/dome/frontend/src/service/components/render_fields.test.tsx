// Copyright 2026 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {fireEvent, render, screen, within} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import {combineReducers, createStore} from 'redux';
import {InjectedFormProps, reducer as formReducer, reduxForm} from 'redux-form';

import RenderFields from '@app/service/components/render_fields';
import {Schema} from '@app/service/types';

// Helper to create a store with the redux-form reducer
const createTestStore = () => {
  return createStore(combineReducers({form: formReducer}));
};

// Helper component to wrap RenderFields with reduxForm
interface FormProps {
  schema: Schema;
}

const TestForm: React.FC<FormProps & InjectedFormProps<{}, FormProps>> = ({
  schema,
}) => {
  return (
    <form aria-label="test-form">
      <RenderFields schema={schema} />
    </form>
  );
};

const DecoratedTestForm = reduxForm<{}, FormProps>({
  form: 'testForm',
})(TestForm);

const renderWithProviders = (schema: Schema) => {
  const store = createTestStore();
  const renderResult = render(
    <Provider store={store}>
      <DecoratedTestForm schema={schema} />
    </Provider>,
  );
  return {...renderResult, store};
};

/**
 * RenderFields component test.
 */
describe('RenderFields', () => {
  test('should render a string field and update form state', async () => {
    const schema: Schema = {
      type: 'object',
      properties: {
        firstName: {type: 'string', description: 'Your first name'},
      },
    };
    const {store} = renderWithProviders(schema);

    const input = screen.getByLabelText('firstName') as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveAttribute('placeholder', 'Your first name');

    fireEvent.change(input, {target: {value: 'John'}});
    expect(input.value).toBe('John');

    const formState = store.getState().form.testForm;
    expect(formState).toBeDefined();
    expect(formState.values).toBeDefined();
    expect(formState.values!.firstName).toBe('John');
  });

  test('should render an integer field and update form state', async () => {
    const schema: Schema = {
      type: 'object',
      properties: {
        age: {type: 'integer', description: 'Your age'},
      },
    };
    const {store} = renderWithProviders(schema);

    const input = screen.getByLabelText('age') as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');

    fireEvent.change(input, {target: {value: '30'}});
    expect(input.value).toBe('30');

    const formState = store.getState().form.testForm;
    expect(formState).toBeDefined();
    expect(formState.values).toBeDefined();
    expect(formState.values!.age).toBe(30);
  });

  test('should render nested fields for an object type', () => {
    const schema: Schema = {
      type: 'object',
      properties: {
        address: {
          type: 'object',
          properties: {
            street: {type: 'string'},
            city: {type: 'string'},
          },
        },
      },
    };
    renderWithProviders(schema);

    expect(screen.getByText('address')).toBeInTheDocument();
    expect(screen.getByLabelText('street')).toBeInTheDocument();
    expect(screen.getByLabelText('city')).toBeInTheDocument();
  });

  describe('array type fields', () => {
    const arraySchema: Schema = {
      type: 'object',
      properties: {
        phoneNumbers: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              type: {type: 'string'},
              number: {type: 'string'},
            },
          },
        },
      },
    };

    test('should render array controls and allow adding items', async () => {
      const {store} = renderWithProviders(arraySchema);

      expect(screen.getByText('phoneNumbers')).toBeInTheDocument();
      const addButton = screen.getByRole('button', {name: 'Add'});
      expect(addButton).toBeInTheDocument();

      // Initially no items
      expect(screen.queryByLabelText('type')).not.toBeInTheDocument();

      // Add one item
      fireEvent.click(addButton);
      expect(screen.getByLabelText('type')).toBeInTheDocument();
      expect(screen.getByLabelText('number')).toBeInTheDocument();
      let formState = store.getState().form.testForm;
      expect(formState).toBeDefined();
      expect(formState.values).toBeDefined();
      expect(formState.values!.phoneNumbers).toHaveLength(1);

      // Add another item
      fireEvent.click(addButton);
      expect(screen.getAllByLabelText('type')).toHaveLength(2);
      expect(screen.getAllByLabelText('number')).toHaveLength(2);
      formState = store.getState().form.testForm;
      expect(formState).toBeDefined();
      expect(formState.values).toBeDefined();
      expect(formState.values!.phoneNumbers).toHaveLength(2);
    });

    test('should allow input within array items', async () => {
      const {store} = renderWithProviders(arraySchema);

      const addButton = screen.getByRole('button', {name: 'Add'});
      fireEvent.click(addButton);

      const typeInput = screen.getByLabelText('type') as HTMLInputElement;
      const numberInput = screen.getByLabelText('number') as HTMLInputElement;

      fireEvent.change(typeInput, {target: {value: 'Home'}});
      fireEvent.change(numberInput, {target: {value: '123-4567'}});

      expect(typeInput.value).toBe('Home');
      expect(numberInput.value).toBe('123-4567');

      const formState = store.getState().form.testForm;
      expect(formState).toBeDefined();
      expect(formState.values).toBeDefined();
      expect(formState.values!.phoneNumbers[0]).toEqual({
        type: 'Home',
        number: '123-4567',
      });
    });
  });

  test('should handle a complex schema', async () => {
    const refinedSchema: Schema = {
      type: 'object',
      properties: {
        user: {
          type: 'object',
          properties: {
            name: {type: 'string'},
            email: {type: 'string'},
            isAdmin: {type: 'boolean'},
          },
        },
        roles: {
          type: 'array',
          items: {
            type: 'object',
            properties: {roleName: {type: 'string'}},
          },
        },
        settings: {
          type: 'object',
          properties: {
            theme: {type: 'string'},
          },
        },
      },
    };
    renderWithProviders(refinedSchema);

    // Check user fields
    expect(screen.getByLabelText('name')).toBeInTheDocument();
    expect(screen.getByLabelText('email')).toBeInTheDocument();
    expect(screen.getByLabelText('isAdmin')).toBeInTheDocument();

    // Check settings fields
    expect(screen.getByLabelText('theme')).toBeInTheDocument();

    // Check array section
    expect(screen.getByText('roles')).toBeInTheDocument();
    const rolesContainer = screen.getByText('roles').closest('div')!;
    const addRoleButton = within(rolesContainer).getByRole('button', {
      name: 'Add',
    });
    fireEvent.click(addRoleButton);
    expect(screen.getByLabelText('roleName')).toBeInTheDocument();
  });
});
