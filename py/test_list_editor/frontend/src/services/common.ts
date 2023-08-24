// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { getUserSessionToken } from "../utils/user_session";

// TODO: setup a mechanism for using different endpoints
// based on the config (dev, staging, prod).
export const backendURL = "http://localhost:5000";

export class ValidationError extends Error {
  public response: Response;

  constructor(message: string, response: Response) {
    super(message);
    this.name = "ValidationError";
    this.response = response;
  }
}

function responseHandler<T>(response: Response): Promise<T> {
  if (response.ok) {
    return response.json() as Promise<T>;
  }
  if (response.status === 422) {
    throw new ValidationError("Some fields are incorrect", response);
  }
  throw new Error(response.statusText);
}

// TODO: Add session to this class
export abstract class BaseService {
  protected backendURL: string;
  protected headers: HeadersInit;
  protected body: BodyInit | null;

  constructor() {
    this.backendURL = backendURL;
    // TODO: Add a timeout handler
    this.headers = {
      ...getUserSessionToken(),
    };
    this.body = null;
  }

  protected async get<T>(endpoint: URL, options: RequestInit = {}): Promise<T> {
    const requestOptions: RequestInit = {
      method: "GET",
      headers: new Headers({ ...this.headers, ...(options.headers ?? {}) }),
    };
    const response = await fetch(endpoint, requestOptions);
    return responseHandler<T>(response);
  }

  protected async put<T>(endpoint: URL, options: RequestInit = {}): Promise<T> {
    const requestOptions: RequestInit = {
      method: "PUT",
      headers: new Headers({
        "Content-Type": "application/json",
        ...this.headers,
        ...(options.headers ?? {}),
      }),
    };
    if (options.body !== undefined) {
      requestOptions.body = options.body;
    }
    const response = await fetch(endpoint, requestOptions);
    return responseHandler<T>(response);
  }

  protected async post<T>(
    endpoint: URL,
    options: RequestInit = {},
  ): Promise<T> {
    const requestOptions: RequestInit = {
      method: "POST",
      headers: new Headers({
        "Content-Type": "application/json",
        ...this.headers,
        ...(options.headers ?? {}),
      }),
    };
    if (options.body !== undefined) {
      requestOptions.body = options.body;
    }
    const response = await fetch(endpoint, requestOptions);
    return responseHandler<T>(response);
  }
}

/** Exception to raise when parameters are undefined. */
export class ParamsUndefined extends Error {}
