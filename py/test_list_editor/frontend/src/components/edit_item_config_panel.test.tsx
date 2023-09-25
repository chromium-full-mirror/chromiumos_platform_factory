// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import "@testing-library/jest-dom";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useLoaderData, useLocation } from "react-router";
import {
  EditorTestItem,
  TestItemHookResult,
  useTestItem,
} from "../hooks/test_item";
import { TestItem, TestItemLoaderResponse } from "../services/itemService";
import { EditItemConfigPanel } from "./edit_item_config_panel";

jest.mock("react-router", () => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return {
    ...jest.requireActual("react-router"),
    useLoaderData: jest.fn(),
    useLocation: jest.fn(),
  };
});

jest.mock("../hooks/test_item", () => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return {
    ...jest.requireActual("../hooks/test_item"),
    useTestItem: jest.fn(),
  };
});

describe("Edit Item Config Panel", () => {
  const updateFieldMock = jest.fn();
  const updateTestItemMock = jest.fn();
  const mockLoaderResponse: TestItemLoaderResponse = {
    testItemData: {},
    testItemId: "test_item",
  };
  const mockTestItemResponse: TestItemHookResult = {
    testItem: {},
    updateField: updateFieldMock,
    updateTestItem: updateTestItemMock,
  };
  beforeEach(() => {
    updateFieldMock.mockReset();
    updateTestItemMock.mockReset();
    mockLoaderResponse.testItemData = {};
    mockTestItemResponse.testItem = {};

    jest.mocked(useLocation).mockReturnValue({
      pathname: "/edit/empty.test_list/test_item",
      state: undefined,
      key: "",
      search: "",
      hash: "",
    });
    jest.mocked(useLoaderData).mockReturnValue(mockLoaderResponse);
    jest.mocked(useTestItem).mockReturnValue(mockTestItemResponse);
  });
  test("Renders correctly", () => {
    render(<EditItemConfigPanel />);

    expect(screen.getByText(/Pytest name/i)).toBeInTheDocument();
  });

  test("Renders a complete test item.", async () => {
    const user = userEvent.setup();
    const testItem: TestItem = {
      test_item_id: "test item 123",
      pytest_name: "pytest 123",
      inherit: "inherit item 123",
      last_modified: "2023-01-23",
      display_name: "Testing test item",
      run_if: "run_if ABC",
      args: { some_args: true },
      locals: { some_locals: true },
      disable_services: ["disabled_1"],
      allow_reboot: false,
      action_on_failure: "NEXT",
      disable_abort: false,
      parallel: false,
      __comment: "Some comment",
    };
    const editorTestItem: EditorTestItem = {
      ...testItem,
      args: '{"some_args": true}',
      locals: '{"some_locals": true}',
      disable_services: '["disabled_1"]',
    };
    mockLoaderResponse.testItemData = testItem;
    mockTestItemResponse.testItem = editorTestItem;
    render(<EditItemConfigPanel />);

    // Verify the updateField function works in each field.
    await user.type(screen.getByDisplayValue(/Testing test item/i), "D");
    expect(updateFieldMock).toHaveBeenCalledWith(
      "display_name",
      "Testing test itemD",
    );

    await user.type(screen.getByDisplayValue(/Some comment/i), "D");
    expect(updateFieldMock).toHaveBeenCalledWith("__comment", "Some commentD");

    await user.type(screen.getByDisplayValue(/run_if ABC/i), "D");
    expect(updateFieldMock).toHaveBeenCalledWith("run_if", "run_if ABCD");

    await user.type(screen.getByDisplayValue(/pytest 123/i), "D");
    expect(updateFieldMock).toHaveBeenCalledWith("pytest_name", "pytest 123D");

    await user.type(screen.getByDisplayValue(/inherit item 123/i), "D");
    expect(updateFieldMock).toHaveBeenCalledWith(
      "inherit",
      "inherit item 123D",
    );

    await user.type(screen.getByDisplayValue(/{"some_args": true}/), "D");
    expect(updateFieldMock).toHaveBeenCalledWith(
      "args",
      '{"some_args": true}D',
    );

    await user.type(screen.getByDisplayValue(/{"some_locals": true}/), "D");
    expect(updateFieldMock).toHaveBeenCalledWith(
      "locals",
      '{"some_locals": true}D',
    );
    await user.type(screen.getByDisplayValue('["disabled_1"]'), "D");
    expect(updateFieldMock).toHaveBeenCalledWith(
      "disable_services",
      '["disabled_1"]D',
    );

    /* eslint-disable testing-library/no-node-access */
    await user.click(
      within(
        (screen.getByText(/Allow reboot/i).parentElement as HTMLElement)
          ?.parentElement as HTMLElement,
      ).getByDisplayValue(/True/i),
    );
    expect(updateFieldMock).toHaveBeenCalledWith("allow_reboot", true);

    await user.click(screen.getByDisplayValue(/STOP/i));
    expect(updateFieldMock).toHaveBeenCalledWith("action_on_failure", "STOP");

    await user.click(
      within(
        (screen.getByText(/Disable abort/i).parentElement as HTMLElement)
          ?.parentElement as HTMLElement,
      ).getByDisplayValue(/True/i),
    );
    expect(updateFieldMock).toHaveBeenCalledWith("disable_abort", true);

    await user.click(
      within(
        (screen.getByText(/Parallel/i).parentElement as HTMLElement)
          ?.parentElement as HTMLElement,
      ).getByDisplayValue(/True/i),
    );
    expect(updateFieldMock).toHaveBeenCalledWith("parallel", true);
    /* eslint-enable testing-library/no-node-access */

    await user.click(screen.getByText("Save"));
    expect(updateTestItemMock).toHaveBeenCalled();
  });
});
