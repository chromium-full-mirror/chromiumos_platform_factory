// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { useMemo } from "react";
import { NestedTestSequence } from "../services/testService";

/**
 * Represents the results of the test subtests, including a map of flattened test sequences.
 */
export interface TestSubtestsResult {
  flattenedMap: Map<string, FlattenedTestSequenceItem>;
}

/**
 * Describes a single flattened test sequence item.
 */
export interface FlattenedTestSequenceItem {
  /** Unique identifier for the node. */
  nodeId: number;

  /** Unique key of a test item. */
  testItemId: string;

  /** Display name used in the editor system. */
  displayName: string;

  /** Array of test item IDs representing subtests. */
  subtests: string[];

  /** ID of the parent test item. */
  parentId: string;
}

/**
 * Recursively collects and flattens test sequences into a map.
 *
 * @param tests - The nested test sequence to flatten.
 * @param flattenedMap - The map to store the flattened test sequences.
 * @param parentId - The parent ID for the current test sequence.
 * @param getRenderId - Function to generate unique render IDs.
 */
function collectFlattenedTestSequences(
  tests: NestedTestSequence,
  flattenedMap: Map<string, FlattenedTestSequenceItem>,
  parentId: string,
  getRenderId: () => number,
): void {
  const currentRenderId = getRenderId();
  const currentItemId = `${tests.test_item_id}-${currentRenderId}`;
  const parentItem = flattenedMap.get(parentId);

  if (!parentItem) {
    // This case is unlikely to happen as the data is generated
    // by traversing the nested structure.
    // TODO(louischiu): Raise Exception or Notification on corruption
    return;
  }
  parentItem.subtests.push(currentItemId);
  flattenedMap.set(currentItemId, {
    nodeId: currentRenderId,
    testItemId: tests.test_item_id,
    displayName: tests.display_name,
    parentId: parentId,
    subtests: [],
  });

  tests.subtests.forEach((subtestItemId) => {
    collectFlattenedTestSequences(
      subtestItemId,
      flattenedMap,
      currentItemId,
      getRenderId,
    );
  });
}

/**
 * Custom hook for managing test sequences and subtests.
 *
 * @param testListId - The ID of the test list.
 * @param testSequence - Array of nested test sequences.
 * @returns An object containing the map of flattened test sequences.
 */
export function useTestSequence(
  testListId: string,
  testSequence: NestedTestSequence[],
): TestSubtestsResult {
  const flattenedMap = useMemo(() => {
    const map = new Map<string, FlattenedTestSequenceItem>();
    let renderId = 0;
    const getRenderId = () => renderId++;

    map.set(testListId, {
      nodeId: getRenderId(),
      testItemId: testListId,
      displayName: testListId,
      parentId: testListId,
      subtests: [],
    });

    testSequence.forEach((testItem) => {
      collectFlattenedTestSequences(testItem, map, testListId, getRenderId);
    });

    return map;
  }, [testListId, testSequence]);

  return { flattenedMap };
}
