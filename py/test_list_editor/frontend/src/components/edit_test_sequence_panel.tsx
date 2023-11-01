// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { TreeItem } from "@mui/x-tree-view/TreeItem";
import { TreeView } from "@mui/x-tree-view/TreeView";
import React, { useState } from "react";
import { useLoaderData, useLocation, useNavigate } from "react-router";
import {
  FlattenedTestSequenceItem,
  useTestSequence,
} from "../hooks/test_sequence";
import { NestedTestSequence } from "../services/testService";

interface EditorTreeItemProps {
  flattenedSequence: Map<string, FlattenedTestSequenceItem>;
  itemId: string;
}

function EditorTreeItem({
  flattenedSequence,
  itemId,
}: EditorTreeItemProps): React.ReactElement {
  const currentItem = flattenedSequence.get(itemId);
  if (!currentItem) {
    return <></>;
  }
  return (
    <TreeItem
      nodeId={itemId}
      label={currentItem.displayName}
      key={itemId}
    >
      {currentItem.subtests.length !== 0 &&
        currentItem.subtests.map((subtestItem) => {
          return EditorTreeItem({ flattenedSequence, itemId: subtestItem });
        })}
    </TreeItem>
  );
}

export function EditTestSequencePanel(): React.ReactElement {
  const location = useLocation();
  const testListId = location.pathname.split("/")[2];
  const testSequenceData = useLoaderData() as NestedTestSequence[];
  const navigate = useNavigate();
  const { flattenedMap: flattenedSequence } = useTestSequence(
    testListId,
    testSequenceData,
  );
  const [selected, setSelected] = useState<string>("");
  const handleSelectNode = (nodeId: string) => {
    setSelected(nodeId);
    navigate(`/edit/${testListId}/${nodeId.replace(/-\d+$/, "")}`);
  };

  const testListNode = flattenedSequence.get(testListId);
  if (!testListNode) {
    // TODO(louischiu): Raise an error if the flattenedSequence returns
    // undefined value on the root node.
    return <div>No data available.</div>;
  }

  const treeItems = testListNode.subtests.map((subtestItemId) => {
    return EditorTreeItem({ flattenedSequence, itemId: subtestItemId });
  });

  return (
    <div>
      <TreeView
        aria-label="Test sequence panel component"
        defaultCollapseIcon={<ExpandMoreIcon />}
        defaultExpandIcon={<ChevronRightIcon />}
        sx={{ height: "1000px", overflowY: "scroll" }}
        selected={selected}
        onNodeSelect={(event: React.SyntheticEvent, nodeId: string) => {
          handleSelectNode(nodeId);
        }}
      >
        {treeItems.length === 0
          ? 'No test item in the "tests" section'
          : treeItems}
      </TreeView>
    </div>
  );
}
