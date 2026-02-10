# check_release_lvm_stateful

**Source code:** [check_release_lvm_stateful.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_release_lvm_stateful.py)

Check if release image has enabled LVM stateful partition.

## Description

This test checks whether Chrome OS release image has enabled LVM stateful
partition. The test fails if it has not enabled.

To run the check with shell script:

```default
#!/bin/sh

root_dev="$(rootdev -s -d)"
release_dev="${root_dev}p5"
mount_pnt="$(mktemp -d)"
chromeos_startup_path="${mount_pnt}"/sbin/chromeos_startup

mount -o ro "${release_dev}" "${mount_pnt}"
if grep -q 'USE_LVM_STATEFUL_PARTITION=1' "${chromeos_startup_path}"; then
  echo "Release image uses LVM stateful partition!"
else
  echo "Release image uses EXT4 stateful partition!"
fi

umount "${mount_pnt}"
rmdir "${mount_pnt}"
```

To run the check with gooftool:

```default
gooftool get_release_fs_type
```

## Test Procedure

1. Mount the release rootfs.
2. Grep the flag USE_LVM_STATEFUL_PARTITION from
   mount_point/sbin/chromeos_startup.
3. Check if step 2 returns True.

## Dependency

grep

## Examples

To check if release image has enabled LVM stateful partition, add this to test
list:

```default
{
  "pytest_name": "check_release_lvm_stateful"
}
```

## Test Arguments

This test does not have any arguments.
