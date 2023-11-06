# CrOS Factory Init: preinit.d

## Script

### 002-override\_jobs.sh

This script provides the override file functionality for init jobs. The file
under `override_jobs` should be a valid init config, and will override the
stanzas in `/etc/init/${JOB_NAME}.conf`.

See **Override File Handling** section in
[`init` manual](https://manpages.ubuntu.com/manpages/trusty/man5/init.5.html)
for details.

### 004-mount\_bind\_files.sh

This script provides a standard way to override system files with mount-bind.
You can follow the flow to easily override system files with this script:

1. We use mount-bind mechanism to override system files with the files under the
   fake root: `FAKE_ROOT=/usr/local/factory/init/preinit.d/mount_bind_files/`.
   You can add additional files to the fake root of toolkit using
   `factory_create_resource` in `ebuild`. Read the description in
   [ebuild](https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/refs/heads/main/chromeos-base/factory-board/factory-board-0.ebuild) for more info.

2. After adding the files to fake root, the factory init scripts will run this
   script automatically to recursively override the system files with the files
   under the fake root.
   e.g., it will overrides `/dir_1/dir_2/filename` with
   `${FAKE_ROOT}/dir_1/dir_2/filename`.
