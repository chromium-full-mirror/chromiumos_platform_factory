// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import React from "react";
import { useLoaderData, useLocation } from "react-router";
import {
  ACTION_ON_FAILURE_OPTIONS,
  ALLOW_REBOOT_OPTIONS,
  DISABLE_ABORT_OPTIONS,
  PARALLEL_OPTIONS,
} from "../constants/test_item";
import { useTestItem } from "../hooks/test_item";
import { TestItemLoaderResponse } from "../services/itemService";
import { DisplayLabel } from "./common/display_label";
import { LabeledInput } from "./common/labeled_input";
import { RadioGroupField } from "./common/radio_group_field";
import { StringTextField } from "./common/string_text_field";

/**
 * Represents the properties for a test item configuration row.
 * @interface
 */
export interface TestItemConfigRowProps {
  /**
   * The label for the configuration row.
   * @type {React.ReactElement}
   */
  label: React.ReactElement;
  /**
   * The input field for the configuration row.
   * @type {React.ReactElement}
   */
  inputField: React.ReactElement;
}

/**
 * Renders a test item configuration row.
 * @param {TestItemConfigRowProps} props - The props for the configuration row.
 * @returns {React.ReactElement}
 */
export function TestItemConfigRow({
  label,
  inputField,
}: TestItemConfigRowProps): React.ReactElement {
  return (
    <LabeledInput
      label={label}
      labelWidth={3}
      inputField={inputField}
      inputWidth={4}
    />
  );
}

/**
 * Renders one configuration value of a test item.
 * @param {string} label - The label for the configuration value.
 * @returns {React.ReactElement}
 */
export function TestItemConfigValue(label: string): React.ReactElement {
  return <Typography variant="body1">{label}</Typography>;
}

/**
 * Renders the complete configuration of a test item.
 *
 * TODO(louischiu): Allow user to modify the `test_item_id` field.
 * TODO(louischiu): Modify the inherit field to be a select item.
 */
export function EditItemConfigPanel(): React.ReactElement {
  const location = useLocation();
  const testListId = location.pathname.split("/")[2];
  const { testItemData, testItemId } =
    useLoaderData() as TestItemLoaderResponse;
  const { testItem, updateField, updateTestItem } = useTestItem(
    testListId,
    testItemData,
  );

  return (
    <>
      <TestItemConfigRow
        label={<></>}
        inputField={
          <Typography
            variant="h5"
            align="center"
            sx={{ marginBottom: 3, marginTop: 2 }}
          >
            {testItem?.display_name ?? testItemId}
          </Typography>
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Test item id" />}
        inputField={TestItemConfigValue(testItem?.test_item_id ?? "None")}
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Pytest name" />}
        inputField={
          <StringTextField
            value={testItem?.pytest_name ?? ""}
            onChange={(value) => {
              updateField("pytest_name", value);
            }}
            validateJSON={false}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Inherit" />}
        inputField={
          <StringTextField
            value={testItem?.inherit ?? ""}
            onChange={(value) => {
              updateField("inherit", value);
            }}
            validateJSON={false}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Last Modified" />}
        inputField={TestItemConfigValue(testItem.last_modified ?? "None")}
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Display name" />}
        inputField={
          <StringTextField
            value={testItem?.display_name ?? ""}
            onChange={(value) => {
              updateField("display_name", value);
            }}
            validateJSON={false}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Comments" />}
        inputField={
          <StringTextField
            value={testItem?.__comment ?? ""}
            onChange={(value) => {
              updateField("__comment", value);
            }}
            validateJSON={false}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Run if" />}
        inputField={
          <StringTextField
            value={testItem?.run_if ?? ""}
            onChange={(value) => {
              updateField("run_if", value);
            }}
            validateJSON={false}
            key="run_if"
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Arguments" />}
        inputField={
          <StringTextField
            value={(testItem?.args as string) ?? "{}"}
            onChange={(value) => {
              updateField("args", value);
            }}
            validateJSON={true}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Locals" />}
        inputField={
          <StringTextField
            value={(testItem?.locals as string) ?? "{}"}
            onChange={(value) => {
              updateField("locals", value);
            }}
            validateJSON={true}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Disable services" />}
        inputField={
          <StringTextField
            value={(testItem?.disable_services as string) ?? "[]"}
            onChange={(value) => {
              updateField("disable_services", value);
            }}
            validateJSON={true}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Allow reboot" />}
        inputField={
          <RadioGroupField
            value={testItem?.allow_reboot ?? false}
            options={ALLOW_REBOOT_OPTIONS}
            onChange={(value) => {
              updateField("allow_reboot", value as boolean);
            }}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Action on failure" />}
        inputField={
          <RadioGroupField
            value={testItem?.action_on_failure ?? "NEXT"}
            options={ACTION_ON_FAILURE_OPTIONS}
            onChange={(value) => {
              updateField("action_on_failure", value as boolean);
            }}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Disable abort" />}
        inputField={
          <RadioGroupField
            value={testItem?.disable_abort ?? false}
            options={DISABLE_ABORT_OPTIONS}
            onChange={(value) => {
              updateField("disable_abort", value as boolean);
            }}
          />
        }
      />
      <TestItemConfigRow
        label={<DisplayLabel label="Parallel" />}
        inputField={
          <RadioGroupField
            value={testItem?.parallel ?? false}
            options={PARALLEL_OPTIONS}
            onChange={(value) => {
              updateField("parallel", value as boolean);
            }}
          />
        }
      />
      <TestItemConfigRow
        label={<></>}
        inputField={
          <Button
            variant="contained"
            fullWidth
            onClick={async () => {
              await updateTestItem();
            }}
          >
            Save
          </Button>
        }
      />
    </>
  );
}
