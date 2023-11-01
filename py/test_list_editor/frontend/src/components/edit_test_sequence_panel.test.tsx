// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  createMemoryRouter,
  RouterProvider,
  useLoaderData,
  useLocation,
  useNavigate,
} from "react-router";
import {
  FlattenedTestSequenceItem,
  TestSubtestsResult,
  useTestSequence,
} from "../hooks/test_sequence";
import { EditTestSequencePanel } from "./edit_test_sequence_panel";

jest.mock("react-router", () => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return {
    ...jest.requireActual("react-router"),
    useLoaderData: jest.fn(),
    useLocation: jest.fn(),
    useNavigate: jest.fn(),
  };
});

jest.mock("../hooks/test_sequence", () => {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-return
  return {
    ...jest.requireActual("../hooks/test_sequence"),
    useTestSequence: jest.fn(),
  };
});

describe("Edit Test Sequence Panel", () => {
  const mockTestSequenceHook: TestSubtestsResult = {
    flattenedMap: new Map<string, FlattenedTestSequenceItem>(),
  };
  const navigateMock = jest.fn();
  beforeEach(() => {
    jest.mocked(useLocation).mockReturnValue({
      pathname: "/edit/empty.test_list/test_item",
      state: undefined,
      key: "",
      search: "",
      hash: "",
    });
    jest.mocked(useLoaderData).mockReturnValue([]);
    jest.mocked(useTestSequence).mockReturnValue(mockTestSequenceHook);
    navigateMock.mockClear();
    jest.mocked(useNavigate).mockReturnValue(navigateMock);

    mockTestSequenceHook.flattenedMap.clear();
  });

  test("renders correctly", () => {
    mockTestSequenceHook.flattenedMap.set("empty.test_list", {
      nodeId: 0,
      testItemId: "empty.test_list",
      displayName: "empty.test_list",
      parentId: "empty.test_list",
      subtests: ["item1-1"],
    });
    mockTestSequenceHook.flattenedMap.set("item1-1", {
      nodeId: 1,
      testItemId: "item1",
      displayName: "name1",
      parentId: "empty.test_list",
      subtests: ["item2-2"],
    });
    mockTestSequenceHook.flattenedMap.set("item2-2", {
      nodeId: 2,
      testItemId: "item2",
      displayName: "name2",
      parentId: "item1-1",
      subtests: [],
    });
    const router = createMemoryRouter(
      [
        {
          path: "/",
          element: <EditTestSequencePanel />,
        },
      ],
      {
        initialEntries: ["/"],
        initialIndex: 0,
      },
    );
    render(<RouterProvider router={router} />);

    expect(screen.getByText(/name1/i)).toBeInTheDocument();
  });

  test("renders empty test list correctly", () => {
    mockTestSequenceHook.flattenedMap.set("incorrect.test_list", {
      nodeId: 0,
      testItemId: "incorrect.test_list",
      displayName: "incorrect.test_list",
      parentId: "incorrect.test_list",
      subtests: [],
    });
    const router = createMemoryRouter(
      [
        {
          path: "/",
          element: <EditTestSequencePanel />,
        },
      ],
      {
        initialEntries: ["/"],
        initialIndex: 0,
      },
    );
    render(<RouterProvider router={router} />);

    expect(screen.getByText(/No data/i)).toBeInTheDocument();
  });

  test("renders empty test sequence correctly", () => {
    mockTestSequenceHook.flattenedMap.set("empty.test_list", {
      nodeId: 0,
      testItemId: "empty.test_list",
      displayName: "empty.test_list",
      parentId: "empty.test_list",
      subtests: [],
    });
    const router = createMemoryRouter(
      [
        {
          path: "/",
          element: <EditTestSequencePanel />,
        },
      ],
      {
        initialEntries: ["/"],
        initialIndex: 0,
      },
    );
    render(<RouterProvider router={router} />);

    expect(screen.getByText(/No test item/i)).toBeInTheDocument();
  });

  test("Handles click correctly.", async () => {
    const user = userEvent.setup();
    mockTestSequenceHook.flattenedMap.set("empty.test_list", {
      nodeId: 0,
      testItemId: "empty.test_list",
      displayName: "empty.test_list",
      parentId: "empty.test_list",
      subtests: ["item1-1"],
    });
    mockTestSequenceHook.flattenedMap.set("item1-1", {
      nodeId: 1,
      testItemId: "item1",
      displayName: "name1",
      parentId: "empty.test_list",
      subtests: ["item2-2"],
    });
    mockTestSequenceHook.flattenedMap.set("item2-2", {
      nodeId: 2,
      testItemId: "item2",
      displayName: "name2",
      parentId: "item1-1",
      subtests: [],
    });

    const router = createMemoryRouter(
      [
        {
          path: "/",
          element: <EditTestSequencePanel />,
        },
      ],
      {
        initialEntries: ["/"],
        initialIndex: 0,
      },
    );
    render(<RouterProvider router={router} />);
    await user.click(screen.getByText(/name1/));
    expect(navigateMock).toHaveBeenCalledWith("/edit/empty.test_list/item1");

    expect(screen.getByText(/name2/i)).toBeInTheDocument();
  });
});
