#!/bin/bash
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
. "${SCRIPT_DIR}/common.sh" || exit 1
. "${SCRIPT_DIR}/venv_common.sh" || exit 1

: "${BASE_TOOLING_VENV:="${SCRIPT_DIR}/base-tooling.venv"}"

main(){
  local requirements_in=$1

  load_venv "${BASE_TOOLING_VENV}" "${BASE_TOOLING_REQUIREMENTS}" || exit 1

  pip-compile --generate-hashes "${requirements_in}" \
    --resolver=backtracking \
    --allow-unsafe

  mk_success
}

main "$1"
