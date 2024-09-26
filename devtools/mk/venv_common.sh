# shellcheck disable=SC2148
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

: "${BASE_TOOLING_REQUIREMENTS:="${SCRIPT_DIR}/base-tooling.requirements.txt"}"

remove_inconsist_venv() {
  local venv_path="$1"
  if [[ -d "${venv_path}" ]]; then
    local venv_python
    venv_python="$(readlink "${venv_path}/bin/python")"
    # Migrate existing venv created without --copies. We can remove this after
    # some time.
    if [[ "${venv_python}" == "/usr/bin/python3" ]]; then
      echo "venv is not created with --copies"
      echo "removing ${venv_path}..."
      rm -rf "${venv_path}"
      return
    fi
    local local_version virtual_version
    local_version="$(python --version)"
    virtual_version="$("${venv_path}/bin/python" --version)"
    if [[ "${local_version}" != "${virtual_version}" ]]; then
      echo "venv is ${virtual_version}, target is ${local_version}"
      echo "removing ${venv_path}..."
      rm -rf "${venv_path}"
    fi
  fi
}

hash_changed() {
  local hash_path="$1"
  local requirements="$2"
  if ! [ -e "${hash_path}" ] || \
     ! diff <(md5sum "${requirements}") "${hash_path}" ; then
    return 0
  fi
  return 1
}

load_venv() {
  local venv_path="$1"
  local venv_requirements="$2"

  remove_inconsist_venv "${venv_path}"
  if ! [ -d "${venv_path}" ]; then
    echo "Cannot find '${venv_path}', install virtualvenv"
    mkdir -p "${venv_path}"
    # system-site-package: Include system site packages for packages like
    # "yaml", "mox".
    # copies: Copy the python so we can run python installed out of chroot.
    python -m venv --system-site-package --copies "${venv_path}" || return 1
  fi

  source "${venv_path}/bin/activate"
  if hash_changed "${venv_path}"/base_tooling_hash \
     "${BASE_TOOLING_REQUIREMENTS}" ; then
    pip install --require-hashes --no-deps -r \
      "${BASE_TOOLING_REQUIREMENTS}" --quiet || return 1
    md5sum "${BASE_TOOLING_REQUIREMENTS}" > "${venv_path}"/base_tooling_hash
    pip install --require-hashes --no-deps -r \
      "${venv_requirements}" --quiet || return 1
    md5sum "${venv_requirements}" > "${venv_path}"/hash
  else
    if hash_changed "${venv_path}"/hash "${venv_requirements}" ; then
      pip install --require-hashes --no-deps -r \
        "${venv_requirements}" --quiet || return 1
      md5sum "${venv_requirements}" > "${venv_path}"/hash
    fi
  fi
}
