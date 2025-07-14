// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import '@testing-library/jest-dom/extend-expect';
import {render, screen} from '@testing-library/react';
import React from 'react';
import {Provider} from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

import * as actions from '@app/auth/actions';
import LoginApp from '@app/auth/components/login_app';
import LoginForm from '@app/auth/components/login_form';
import * as selectors from '@app/auth/selectors';
import {AuthData} from '@app/auth/types';
import {RootState} from '@app/types';
import * as formUtils from '@common/form';
import * as utils from '@common/utils';
import {indigo} from '@mui/material/colors';
import {createTheme, ThemeProvider} from '@mui/material/styles';
import {createGenerateClassName, StylesProvider} from '@mui/styles';

// Create a mock store function
const middlewares = [thunk];
const mockStore = configureStore<RootState>(middlewares);

// Create a default MUI theme instance
const THEME = {
  palette: {
    primary: indigo,
  },
};

jest.mock('@app/auth/actions');
jest.mock('@app/auth/selectors');
jest.mock('@common/form');
jest.mock('@common/utils');
jest.mock('./login_form', () => jest.fn(() =>
  <div data-testid="mock-login-form">Mocked LoginForm</div>,
));

const mockedTestAuthToken = actions.testAuthToken as jest.Mock;
const mockedTryLogin = actions.tryLogin as jest.Mock;
const mockedIsLoggedIn = selectors.isLoggedIn as jest.Mock;
const mockedToReduxFormError = formUtils.toReduxFormError as jest.Mock;
const mockedIsAxiosError = utils.isAxiosError as unknown as jest.Mock;
const MockedLoginForm = LoginForm as jest.Mock;

const generateClassName = createGenerateClassName({productionPrefix: 'c'});

const renderComponent = (store: any) => {
  return render(
    <Provider store={store}>
      <StylesProvider generateClassName={generateClassName}>
        <ThemeProvider theme={createTheme(THEME)}>
          <LoginApp />
        </ThemeProvider>
      </StylesProvider>
    </Provider>,
  );
};

/**
 * LoginApp component test.
 */
describe('LoginApp', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    MockedLoginForm.mockClear();
    mockedTestAuthToken.mockReturnValue(async (dispatch: any) => {
      return Promise.resolve();
    });
    mockedTryLogin.mockImplementation((data: AuthData) => {
      return async (dispatch: any) => {
        return Promise.resolve();
      };
    });
  });

  test('should show loader when isLoggedIn is null', () => {
    mockedIsLoggedIn.mockReturnValue(null);
    const store = mockStore({} as RootState);
    renderComponent(store);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.queryByTestId('mock-login-form')).not.toBeInTheDocument();
  });

  test('should call testAuthToken on mount', () => {
    mockedIsLoggedIn.mockReturnValue(null);
    const store = mockStore({} as RootState);
    const dispatchSpy = jest.spyOn(store, 'dispatch');
    renderComponent(store);
    expect(mockedTestAuthToken).toHaveBeenCalledTimes(1);
    expect(dispatchSpy).toHaveBeenCalledTimes(1);
  });

  test('should render LoginForm when not logged in', () => {
    mockedIsLoggedIn.mockReturnValue(false);
    const store = mockStore({} as RootState);
    renderComponent(store);
    expect(screen.getByTestId('mock-login-form')).toBeInTheDocument();
    expect(MockedLoginForm).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });

  describe('handleSubmit', () => {
    const mockAuthData: AuthData = {
      username: 'testuser',
      password: 'password',
    };
    let onSubmit: (data: AuthData) => Promise<void>;
    let store: any;

    beforeEach(() => {
      mockedIsLoggedIn.mockReturnValue(false);
      store = mockStore({} as RootState);
      renderComponent(store);
      expect(MockedLoginForm).toHaveBeenCalledTimes(1);
      onSubmit = MockedLoginForm.mock.calls[0][0].onSubmit;
    });

    test('should call tryLogin and succeed', async () => {
      await expect(onSubmit(mockAuthData)).resolves.toBeUndefined();
      expect(mockedTryLogin).toHaveBeenCalledWith(mockAuthData);
    });

    test('should catch and transform Axios error', async () => {
      const axiosError = {message: 'Network Error', isAxiosError: true};
      const reduxError = {_error: 'submit failed', original: axiosError};
      mockedTryLogin.mockImplementation((data: AuthData) => {
        return async (dispatch: any) => {
          throw axiosError;
        };
      });
      mockedIsAxiosError.mockReturnValue(true);
      mockedToReduxFormError.mockReturnValue(reduxError);
      await expect(onSubmit(mockAuthData)).rejects.toEqual(reduxError);
      expect(mockedTryLogin).toHaveBeenCalledWith(mockAuthData);
      expect(mockedIsAxiosError).toHaveBeenCalledWith(axiosError);
      expect(mockedToReduxFormError).toHaveBeenCalledWith(axiosError);
    });

    test('should catch and re-throw generic error', async () => {
      const errorMessage = 'Something went wrong';
      const genericError = new Error(errorMessage);
      mockedTryLogin.mockImplementation((data: AuthData) => {
        return async (dispatch: any) => {
          throw genericError;
        };
      });
      mockedIsAxiosError.mockReturnValue(false);
      await expect(onSubmit(mockAuthData)).rejects.toThrow(errorMessage);
      expect(mockedTryLogin).toHaveBeenCalledWith(mockAuthData);
      expect(mockedIsAxiosError).toHaveBeenCalledWith(genericError);
      expect(mockedToReduxFormError).not.toHaveBeenCalled();
    });
  });
});
