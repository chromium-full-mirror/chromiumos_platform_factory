// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { BaseResponse } from "../interfaces/common";
import { BaseService, ParamsUndefined } from "./common";

export interface NestedTestSequence {
  test_item_id: string;
  display_name: string;
  subtests: NestedTestSequence[];
}

/** Interface of the response to the `/api/v1/tests/` endpoint. */
export interface TestSequenceResponse extends BaseResponse {
  data: NestedTestSequence[];
}

/** Service class to make request to the `/api/v1/tests` endpoint. */
export class TestService extends BaseService {
  private readonly apiBaseEndpoint = "/api/v1/tests/";
  testListId: string;
  endpoint: URL;

  constructor(testListId: string) {
    super();
    this.testListId = testListId;
    const apiEndpoint = `${this.apiBaseEndpoint}${this.testListId}`;
    this.endpoint = new URL(apiEndpoint, this.backendURL);
  }

  public async getTestListSubtests(): Promise<NestedTestSequence[]> {
    const response = await this.get<TestSequenceResponse>(this.endpoint);
    return response.data;
  }
}

interface param {
  testListId?: string;
  [key: string]: unknown;
}

interface loaderParams {
  params: param;
}

/**
 * Test list test sequence loader function.
 *
 * This function is for react router to make request when we visit
 * the edit page.
 */
export async function getTestListSubtests({
  params,
}: loaderParams): Promise<NestedTestSequence[]> {
  if (!params.testListId) {
    throw new ParamsUndefined("Test list id is not defined");
  }
  const testService = new TestService(params.testListId);
  const result = await testService.getTestListSubtests();
  return result;
}
