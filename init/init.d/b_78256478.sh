#!/bin/sh
# Copyright 2018 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Symlinks are by default disabled on Chrome OS since
# https://chromium-review.googlesource.com/966683.
# However, for factory we do want to allow symlink everywhere so 3rd party
# programs won't have trouble. Also for b/74420122.

# See platform2/init/chromeos_startup for the details.

LSM_INODE_POLICIES="/sys/kernel/security/chromiumos/inode_security_policies"

remount_security_fs() {
  mount -n -o nodev,noexec,nosuid,remount,"${1}" \
    securityfs /sys/kernel/security
}

main() {
  # After CL:5082410, /sys/kernel/security was mounted readonly.
  # So we remount it for allowing write operation.
  # See b/330451195 for the details.
  remount_security_fs rw
  trap 'remount_security_fs ro' EXIT

  if [ -e "${LSM_INODE_POLICIES}" ]; then
    # /var/factory may be already covered by /var, but we do want to allow it
    # explicitly in case if other init jobs mounted /var/factory in different
    # location.
    for path in /var /var/factory /mnt/stateful_partition; do
      printf "${path}" >"${LSM_INODE_POLICIES}/allow_symlink"
      printf "${path}" >"${LSM_INODE_POLICIES}/allow_fifo"
    done
  fi
}

main "$@"
