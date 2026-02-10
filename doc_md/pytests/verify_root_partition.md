# verify_root_partition

**Source code:** [verify_root_partition.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/verify_root_partition.py)

Verifies the integrity of the root partition.

## Description

The root partition may be modified during the factory process. If the disk is
damaged or the flash process is broken, the root partition may also be wrong.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- Device API `cros.factory.device.partitions`.
- Device API `cros.factory.device.toybox`.

## Examples

An example:

```default
{
  "pytest_name": "verify_root_partition",
  "label": "Verify Root Partition",
  "related_components": [
    "test_tags.TestCategory.STORAGE"
  ],
  "args": {
    "max_bytes": 1048576
  }
}
```

## Test Arguments

| Name          | Type      | Description                                                                |
|---------------|-----------|----------------------------------------------------------------------------|
| kern_a_device | str, None | (optional; default: `None`) Path to the device containing KERN-A partition |
| root_device   | str, None | (optional; default: `None`) Path to the device containing rootfs partition |
| max_bytes     | int, None | (optional; default: `None`) Maximum number of bytes to read                |
