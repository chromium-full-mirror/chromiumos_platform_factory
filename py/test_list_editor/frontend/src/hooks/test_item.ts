// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { useEffect, useState } from "react";
import { ItemService, TestItem } from "../services/itemService";

// TODO: Make the fields required once we have defined the schema of `TestItem`.
export interface EditorTestItem {
  test_item_id?: string;
  display_name?: string;
  inherit?: string;
  last_modified?: string;
  pytest_name?: string;
  run_if?: string;
  action_on_failure?: string;
  allow_reboot?: boolean;
  disable_abort?: boolean;
  parallel?: boolean;
  args?: string;
  locals?: string;
  disable_services?: string;
}

/**
 * Converts a TestItem object to an EditorTestItem object.
 *
 * TODO: Handle JSON conversion error and show notification.
 *
 * @param {TestItem} item - The TestItem object to convert.
 * @return {EditorTestItem} - The converted EditorTestItem object.
 *
 * @throws {SyntaxError} If the properties of the TestItem object are not valid JSON.
 */
function _convertToEditorTestItem(item: TestItem): EditorTestItem {
  const { args, locals, disable_services, ...rest } = item;
  const editorTestItem: EditorTestItem = {
    ...rest,
    ...(args !== undefined && { args: JSON.stringify(args, null, 2) }),
    ...(locals !== undefined && { locals: JSON.stringify(locals, null, 2) }),
    ...(disable_services !== undefined && {
      disable_services: JSON.stringify(disable_services, null, 2),
    }),
  };
  return editorTestItem;
}

/**
 * Converts an EditorTestItem object to a TestItem object.
 *
 * TODO: Handle JSON conversion error and show notification.
 *
 * @param {EditorTestItem} item - The EditorTestItem object to convert.
 * @return {TestItem} - The converted TestItem object.
 *
 * @throws {SyntaxError} If the properties of the EditorTestItem object are not valid JSON.
 */
function _convertToTestItem(item: EditorTestItem): TestItem {
  const { args, locals, disable_services, ...rest } = item;
  return {
    ...rest,
    ...(args !== undefined && { args: JSON.parse(args) as object }),
    ...(locals !== undefined && { locals: JSON.parse(locals) as object }),
    ...(disable_services !== undefined && {
      disable_services: JSON.parse(disable_services) as object,
    }),
  };
}

/**
 * Result of the `TestItemHook`
 *
 * Use `updateField` to update a field of the test item the hook is managing.
 * Use `updateTestItem` to propagate the change in the frontend to the backend.
 */
export interface TestItemHookResult {
  testItem: EditorTestItem;
  /**
   * Updates the field of a `testItem` with `data`.
   *
   * This function updates the React state of the test item. It does not update
   * the state of the backend test item. To update the state of the backend item,
   * use `updateTestItem` instead.
   * @param field keyof the `TestItem`.
   * @param data the value to update the test item.
   * @returns {void}
   */
  updateField: (field: keyof TestItem, data: string | boolean | object) => void;

  /**
   * Update the test item in the backend to be the same as the frontend.
   * @returns {Promise<void>}
   */
  updateTestItem: () => Promise<void>;
}

/**
 * Custom hook to manage a test item.
 *
 * @param {string} testListId - The ID of the test list to which the test item belongs.
 * @param {TestItem} testItemData - The ID of the test item to manage.
 * @returns {TestItemHookResult} An object containing the test item and a function to update it.
 */
export function useTestItem(
  testListId: string,
  testItemData: TestItem,
): TestItemHookResult {
  const [testItem, setTestItem] = useState<EditorTestItem>(
    _convertToEditorTestItem(testItemData),
  );
  const itemService = new ItemService(testListId);

  function updateField(field: keyof TestItem, data: string | boolean | object) {
    setTestItem({
      ...testItem,
      [field]: data,
    });
  }

  async function updateTestItem() {
    let updateTestItem;
    try {
      updateTestItem = _convertToTestItem(testItem);
    } catch (e) {
      // TODO: Raise a notification at this point about serialization
      //       failure.
      return;
    }

    const response = await itemService.updateTestItem(updateTestItem);
    setTestItem(_convertToEditorTestItem(response.data));
  }

  useEffect(() => {
    setTestItem(_convertToEditorTestItem(testItemData));
  }, [testItemData]);

  return { testItem, updateField, updateTestItem };
}
