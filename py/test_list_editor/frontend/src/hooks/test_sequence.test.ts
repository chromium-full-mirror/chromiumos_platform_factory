// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { renderHook } from "@testing-library/react";
import {
  FlattenedTestSequenceItem,
  TestSubtestsResult,
  useTestSequence,
} from "./test_sequence";

import { NestedTestSequence } from "../services/testService";

describe("Test useTestSequence hook", () => {
  test("Returns a flattened map.", () => {
    const fakeSequence: NestedTestSequence[] = [
      {
        test_item_id: "item1",
        display_name: "name1",
        subtests: [
          {
            test_item_id: "item2",
            display_name: "name2",
            subtests: [],
          },
          {
            test_item_id: "item2",
            display_name: "name2",
            subtests: [],
          },
        ],
      },
    ];
    const expected = new Map<string, FlattenedTestSequenceItem>();
    expected.set("fake.test_list", {
      nodeId: 0,
      testItemId: "fake.test_list",
      displayName: "fake.test_list",
      parentId: "fake.test_list",
      subtests: ["item1-1"],
    });
    expected.set("item1-1", {
      nodeId: 1,
      testItemId: "item1",
      displayName: "name1",
      parentId: "fake.test_list",
      subtests: ["item2-2", "item2-3"],
    });
    expected.set("item2-2", {
      nodeId: 2,
      testItemId: "item2",
      displayName: "name2",
      parentId: "item1-1",
      subtests: [],
    });
    expected.set("item2-3", {
      nodeId: 3,
      testItemId: "item2",
      displayName: "name2",
      parentId: "item1-1",
      subtests: [],
    });
    const { result } = renderHook(() =>
      useTestSequence("fake.test_list", fakeSequence),
    );
    const hookResult: TestSubtestsResult = result.current;
    expect(hookResult.flattenedMap).toStrictEqual(expected);
  });

  test("Same item shared.", () => {
    const fakeSequence: NestedTestSequence[] = [
      {
        test_item_id: "item1",
        display_name: "name1",
        subtests: [
          {
            test_item_id: "item2",
            display_name: "name2",
            subtests: [],
          },
          {
            test_item_id: "item2",
            display_name: "name2",
            subtests: [],
          },
        ],
      },
      {
        test_item_id: "item3",
        display_name: "name3",
        subtests: [
          {
            test_item_id: "item2",
            display_name: "name2",
            subtests: [],
          },
        ],
      },
    ];
    const expected = new Map<string, FlattenedTestSequenceItem>();
    expected.set("fake.test_list", {
      nodeId: 0,
      testItemId: "fake.test_list",
      displayName: "fake.test_list",
      parentId: "fake.test_list",
      subtests: ["item1-1", "item3-4"],
    });
    expected.set("item1-1", {
      nodeId: 1,
      testItemId: "item1",
      displayName: "name1",
      parentId: "fake.test_list",
      subtests: ["item2-2", "item2-3"],
    });
    expected.set("item2-2", {
      nodeId: 2,
      testItemId: "item2",
      displayName: "name2",
      parentId: "item1-1",
      subtests: [],
    });
    expected.set("item2-3", {
      nodeId: 3,
      testItemId: "item2",
      displayName: "name2",
      parentId: "item1-1",
      subtests: [],
    });
    expected.set("item3-4", {
      nodeId: 4,
      testItemId: "item3",
      displayName: "name3",
      parentId: "fake.test_list",
      subtests: ["item2-5"],
    });
    expected.set("item2-5", {
      nodeId: 5,
      testItemId: "item2",
      displayName: "name2",
      parentId: "item3-4",
      subtests: [],
    });

    const { result } = renderHook(() =>
      useTestSequence("fake.test_list", fakeSequence),
    );
    const hookResult: TestSubtestsResult = result.current;
    expect(hookResult.flattenedMap).toStrictEqual(expected);
  });
});
