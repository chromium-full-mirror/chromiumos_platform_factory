// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import "@testing-library/jest-dom";
import { Status } from "../interfaces/common";
import {
  getTestItemConfig,
  ItemService,
  ParamsUndefined,
  TestItem,
  TestItemDisplay,
} from "./itemService";

jest.mock("uuid", () => ({
  v4: () => "12345678",
}));

describe("Item service testing", () => {
  const fakeResponse = {
    status: Status.SUCCESS,
    data: {},
    message: "success",
  };

  const fakeModifiedTestItem: TestItem = {
    test_item_id: "ABC",
    display_name: "ABC",
  };

  const fakeTestItemForDisplay: TestItemDisplay = {
    test_item_id: "a",
    display_name: "a",
    subtests: [],
  };

  const customMock = jest.fn();
  beforeEach(() => {
    customMock.mockResolvedValue({
      ok: jest.fn().mockReturnValue(true),
      json: jest.fn().mockResolvedValue(fakeResponse),
    });
    global.fetch = customMock;
  });

  test("Get item", async () => {
    const itemService = new ItemService("fake.test_list");
    const response = await itemService.getTestItem("ABC");

    expect(response.data).toStrictEqual({});

    const expectedURL = new URL(
      "http://localhost:5000/api/v1/items/fake.test_list/ABC",
    );
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

  test("Get item list", async () => {
    fakeResponse.data = { a: fakeTestItemForDisplay };

    const itemService = new ItemService("fake.test_list");
    const response = await itemService.getItemList();

    expect(response.data).toStrictEqual({ a: fakeTestItemForDisplay });

    const expectedURL = new URL(
      "http://localhost:5000/api/v1/items/fake.test_list",
    );
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

  test("Update test item", async () => {
    fakeResponse.data = fakeModifiedTestItem;

    const itemService = new ItemService("fake.test_list");
    const response = await itemService.updateTestItem(fakeModifiedTestItem);

    expect(response).toStrictEqual(fakeResponse);

    const expectedURL = new URL(
      "http://localhost:5000/api/v1/items/fake.test_list",
    );
    const expectedCallOptions = {
      method: "PUT",
      headers: new Headers({
        "Content-Type": "application/json",
        user_id: "12345678",
        session_id: "12345678",
      }),
      body: '{"data":{"test_item_id":"ABC","display_name":"ABC"}}',
    };
    expect(customMock).toHaveBeenLastCalledWith(
      expectedURL,
      expectedCallOptions,
    );
  });

  test("Create test item", async () => {
    fakeResponse.data = fakeModifiedTestItem;

    const itemService = new ItemService("fake.test_list");
    const response = await itemService.createTestItem(fakeModifiedTestItem);

    expect(response).toStrictEqual(fakeResponse);

    const expectedURL = new URL(
      "http://localhost:5000/api/v1/items/fake.test_list",
    );
    const expectedCallOptions = {
      method: "POST",
      headers: new Headers({
        "Content-Type": "application/json",
        user_id: "12345678",
        session_id: "12345678",
      }),
      body: '{"data":{"test_item_id":"ABC","display_name":"ABC"}}',
    };
    expect(customMock).toHaveBeenLastCalledWith(
      expectedURL,
      expectedCallOptions,
    );
  });

  test("Raise error when testListId or testItemId is missing", async () => {
    const params = { testItemId: "ABC" };
    const target = async () => await getTestItemConfig({ params });

    await expect(target).rejects.toThrow(ParamsUndefined);
  });

  test("Make API call from loader function", async () => {
    fakeResponse.data = {};
    const params = { testItemId: "a", testListId: "123" };
    const result = await getTestItemConfig({ params });

    expect(result).toEqual({
      testItemId: "a",
      testItemData: {},
    });
  });
});
