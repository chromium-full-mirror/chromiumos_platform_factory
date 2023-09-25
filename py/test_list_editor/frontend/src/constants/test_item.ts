// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import { RadioOption } from "../components/common/radio_group_field";

const TRUE_OPTION: RadioOption = {
  label: "True",
  value: true,
};

const FALSE_OPTION: RadioOption = {
  label: "False",
  value: false,
};

export const ALLOW_REBOOT_OPTIONS: RadioOption[] = [TRUE_OPTION, FALSE_OPTION];

export const DISABLE_ABORT_OPTIONS: RadioOption[] = [TRUE_OPTION, FALSE_OPTION];

export const PARALLEL_OPTIONS: RadioOption[] = [TRUE_OPTION, FALSE_OPTION];

export const ACTION_ON_FAILURE_OPTIONS: RadioOption[] = [
  {
    label: "Stop",
    value: "STOP",
  },
  {
    label: "Next",
    value: "NEXT",
  },
  {
    label: "Parent",
    value: "PARENT",
  },
];
