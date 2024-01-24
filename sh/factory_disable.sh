#!/bin/bash
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# This scripts removes the `enabled` stub file used to detect whether
# to enable factory software or not, while also removes files generated
# by factory software to make sure after disabling factory software, the
# behavior of the original test image is unaffected.

FACTORY_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
ENABLE_STUB_FILE="${FACTORY_DIR}/enabled"
POWER_MANAGER_FACTORY_MODE_STUB="/var/lib/power_manager/factory_mode"

CLEANUP_FILES=("${ENABLE_STUB_FILE}" "${POWER_MANAGER_FACTORY_MODE_STUB}")

for file in "${CLEANUP_FILES[@]}"; do
  rm "${file}"
done

echo "Factory software disabled. Reboot to switch to normal test image."
