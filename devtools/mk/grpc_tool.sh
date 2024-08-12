#!/bin/bash
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
. "${SCRIPT_DIR}/common.sh" || exit 1
. "${SCRIPT_DIR}/venv_common.sh" || exit 1

: "${VENV_PATH:="${SCRIPT_DIR}/grpc_tool.venv"}"
: "${REQUIREMENTS_PATH:="${SCRIPT_DIR}/grpc_tool.requirements.txt"}"

main(){
  load_venv "${VENV_PATH}" "${REQUIREMENTS_PATH}" || exit 1

  "$@"

  mk_success
}

main "$@"
