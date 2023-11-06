#!/bin/sh
# Copyright 2019 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

main() {
  local override_job
  local job_name
  local job_path

  for job in "${SCRIPT_DIR}/override_jobs/"*; do
    override_job="${job}.conf"
    job_name="$(basename "${job}")"
    job_path="/etc/init/${job_name}.conf"

    if [ -e "${job_path}" ]; then
      cp "${job_path}" "${override_job}"
      # If a stanza is duplicated,  the last occurrence will be used. So we can
      # siimply append the override config in the end.
      cat "${job}" >> "${override_job}"
      mount --bind "${override_job}" "${job_path}"
    fi
  done
}

main
