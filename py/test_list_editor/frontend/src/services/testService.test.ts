// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import "@testing-library/jest-dom";
import { Status } from "../interfaces/common";
import { backendURL, ParamsUndefined } from "./common";
import {
  getTestListSubtests,
  NestedTestSequence,
  TestSequenceResponse,
  TestService,
} from "./testService";

jest.mock("uuid", () => ({
  v4: () => "12345678",
}));

describe("Test service testing", () => {
  const fakeResponse: TestSequenceResponse = {
    status: Status.SUCCESS,
    data: [],
    message: "success",
  };

  const fakeSequence: NestedTestSequence[] = [
    {
      test_item_id: "ABC",
      display_name: "A B C",
      subtests: [
        {
          test_item_id: "ABC123",
          display_name: "ABC123",
          subtests: [],
        },
      ],
    },
  ];

  const customMock = jest.fn();

  beforeEach(() => {
    customMock.mockClear();
    customMock.mockResolvedValue({
      ok: jest.fn().mockReturnValue(true),
      json: jest.fn().mockResolvedValue(fakeResponse),
    });
    global.fetch = customMock;
  });
  test("Get resolved empty test sequence", async () => {
    const testService = new TestService("fake.test_list");
    const response = await testService.getTestListSubtests();

    expect(response).toStrictEqual([]);

    const expectedURL = new URL("/api/v1/tests/fake.test_list", backendURL);
    const expectedCallOptions = {
      method: "GET",
      headers: new Headers({
        user_id: "12345678",
        session_id: "12345678",
      }),
    };
    expect(customMock).toHaveBeenLastCalledWith(
      expectedURL,
      expectedCallOptions,
    );
  });

  test("Get resolved test sequence", async () => {
    fakeResponse.data = fakeSequence;

    const testService = new TestService("fake.test_list");
    const response = await testService.getTestListSubtests();

    expect(response).toStrictEqual(fakeSequence);

    const expectedURL = new URL("/api/v1/tests/fake.test_list", backendURL);
    const expectedCallOptions = {
      method: "GET",
      headers: new Headers({
        user_id: "12345678",
        session_id: "12345678",
      }),
    };
    expect(customMock).toHaveBeenLastCalledWith(
      expectedURL,
      expectedCallOptions,
    );
  });

  test("Loader has no testListId", async () => {
    const param = {
      params: {
        testListId: undefined,
      },
    };
    const target = async () => await getTestListSubtests(param);
    await expect(target).rejects.toThrow(ParamsUndefined);
  });

  test("Loader returns correct test subtests", async () => {
    const param = {
      params: {
        testListId: "fake.test_list",
      },
    };

    const spy = jest.spyOn(TestService.prototype, "getTestListSubtests");
    spy.mockResolvedValue([]);

    const result = await getTestListSubtests(param);
    expect(result).toStrictEqual([]);
  });
});
