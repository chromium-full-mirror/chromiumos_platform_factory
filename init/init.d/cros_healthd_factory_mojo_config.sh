#!/bin/sh
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

content=\
"[
  {
    \"identity\": \"u:r:cros_init_scripts:s0\",
    \"request\": [
      \"CrosHealthdDiagnostics\",
      \"CrosHealthdEvent\",
      \"CrosHealthdProbe\",
      \"CrosHealthdRoutines\"
    ]
  }
]"

MOJO_POLICY_DIR="/usr/local/etc/mojo/service_manager/policy"
mkdir -p "${MOJO_POLICY_DIR}"
echo "${content}" > "${MOJO_POLICY_DIR}/factory_cros_healthd.jsonc"
