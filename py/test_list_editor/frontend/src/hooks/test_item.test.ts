// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { renderHook, waitFor } from "@testing-library/react";
import { TestItemHookResult, useTestItem } from "./test_item";

import { Status } from "../interfaces/common";
import { ItemService, TestItem } from "../services/itemService";

describe("Test TestItem hook", () => {
  const spy = jest.spyOn(ItemService.prototype, "getTestItem");
  const spyUpdate = jest.spyOn(ItemService.prototype, "updateTestItem");
  const fakeGetResponse = {
    status: Status.SUCCESS,
    data: {},
    message: "",
  };
  const fakeUpdateResponse = {
    status: Status.SUCCESS,
    data: {},
    message: "",
  };
  const items: TestItem = {
    test_item_id: "ABC",
    display_name: "ABC",
  };
  const newItem: TestItem = {
    test_item_id: "ABC",
    display_name: "NewA",
  };
  beforeEach(() => {
    spy.mockReset();
    spyUpdate.mockReset();

    fakeGetResponse.data = {};
    fakeUpdateResponse.data = {};

    spy.mockResolvedValue(fakeGetResponse);
    spyUpdate.mockResolvedValue(fakeUpdateResponse);
  });

  test("Returns a test item", () => {
    const { result } = renderHook(() => useTestItem("fake.test_list", items));
    const hookResult: TestItemHookResult = result.current;
    expect(hookResult.testItem).toStrictEqual(items);
  });

  test("Updates when item data has changed", () => {
    const { result: result1 } = renderHook(() =>
      useTestItem("fake.test_list", items),
    );
    const hookResult1: TestItemHookResult = result1.current;
    expect(hookResult1.testItem).toStrictEqual(items);

    const { result: result2 } = renderHook(() =>
      useTestItem("fake.test_list", newItem),
    );
    const hookResult2: TestItemHookResult = result2.current;
    expect(hookResult2.testItem).toStrictEqual(newItem);
  });

  test("Convert object field of a test item.", () => {
    const fakeItem = {
      args: { some_field: true },
      locals: {},
      disable_services: [],
    };
    const { result } = renderHook(() =>
      useTestItem("fake.test_list", fakeItem),
    );
    const hookResult: TestItemHookResult = result.current;
    expect(hookResult.testItem.args).toStrictEqual(
      JSON.stringify(fakeItem.args, null, 2),
    );
    expect(hookResult.testItem.locals).toStrictEqual(
      JSON.stringify(fakeItem.locals, null, 2),
    );
    expect(hookResult.testItem.disable_services).toStrictEqual(
      JSON.stringify(fakeItem.disable_services, null, 2),
    );
  });

  test("Update test item filed", async () => {
    const { result } = renderHook(() => useTestItem("fake.test_list", items));

    let hookResult: TestItemHookResult = result.current;
    await waitFor(() => {
      hookResult.updateField("test_item_id", "Modified ABC");
    });

    hookResult = result.current;
    expect(hookResult.testItem).toStrictEqual({
      ...items,
      test_item_id: "Modified ABC",
    });
  });

  test("Update test item with JSON object", async () => {
    const { result } = renderHook(() => useTestItem("fake.test_list", items));

    let hookResult: TestItemHookResult = result.current;
    await waitFor(() => {
      hookResult.updateField("disable_services", "[]");
    });
    hookResult = result.current;
    await waitFor(() => {
      hookResult.updateField("locals", "{}");
    });
    hookResult = result.current;
    await waitFor(() => {
      hookResult.updateField("args", "{}");
    });

    hookResult = result.current;
    await waitFor(async () => {
      await hookResult.updateTestItem();
    });
    expect(spyUpdate).toHaveBeenCalledWith({
      ...items,
      args: {},
      locals: {},
      disable_services: [],
    });
  });

  test("Update test item with incorrect JSON string", async () => {
    const { result } = renderHook(() => useTestItem("fake.test_list", items));

    let hookResult: TestItemHookResult = result.current;
    await waitFor(() => {
      hookResult.updateField("args", "{");
    });

    hookResult = result.current;
    await waitFor(async () => {
      await hookResult.updateTestItem();
    });
    expect(spyUpdate).not.toBeCalled();
  });

  test("Call updateTestItem and expect updated test item", async () => {
    fakeUpdateResponse.data = newItem;
    const { result } = renderHook(() => useTestItem("fake.test_list", items));

    let hookResult: TestItemHookResult = result.current;
    await waitFor(async () => {
      await hookResult.updateTestItem();
    });
    expect(spyUpdate).toBeCalledTimes(1);

    hookResult = result.current;
    expect(hookResult.testItem).toStrictEqual(newItem);
  });
});
