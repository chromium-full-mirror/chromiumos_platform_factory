# bad_blocks

**Source code:** [bad_blocks.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/bad_blocks.py)

Tests a storage device by running the badblocks command.

## Description

This test uses `badblocks(8)` command to search for badblocks on a device.  By
default the unused portion of the stateful partition is used
(`mode=stateful_partition_free_space`).  (For instance, on
a device with a 32 GB hard drive, cgpt reports that partition 1 is about 25 GB,
but the size of the filesystem is only about 1 GB.  We run the test on the
unused 24 GB.)

Alternatively one can specify the use of a file in the filesystem allocated by
the test, or raw mode where a specific file/partition must be provided.
(`mode=file` or `mode=raw`)

When `mode=stateful_partition_free_space`, unused portion after stateful
partition must exist.  An error message `'There is no unused space after
stateful partition.'` will be shown if it cannot find any extra space.
(If you install the image by `chromeos-install`, by default, there will be no
free space after stateful partition.)

### Default Behavior

The test will use 1GB of **unused portion of the stateful partition** for
testing by default.  On most devices, `badblocks` takes ~0.5s/MB (for four
passes).  So the default setup will take about 9 minutes.

The test skips badblocks and only runs smartctl for SSD storage by default.

## Test Procedure

This test does not require operator interaction.  An UI will be shown to
indicate the process of testing.

## Dependency

This pytest depends on `badblocks(8)`.

## Examples

To run default test:

```default
{
  "pytest_name": "bad_blocks",
  "label": "Bad Blocks",
  "related_components": [
    "test_tags.TestCategory.BRIDGE_PCIE_EMMC",
    "test_tags.TestCategory.STORAGE"
  ],
  "args": {
    "timeout_secs": 120,
    "log_threshold_secs": 10,
    "max_bytes": 1073741824
  }
}
```

To change the portion of disk to 2 GB:

```default
{
  "pytest_name": "bad_blocks",
  "label": "Bad Blocks 2GB",
  "related_components": [
    "test_tags.TestCategory.BRIDGE_PCIE_EMMC",
    "test_tags.TestCategory.STORAGE"
  ],
  "args": {
    "timeout_secs": 120,
    "log_threshold_secs": 10,
    "max_bytes": 2147483648
  }
}
```

To force running badblocks:

```default
{
  "pytest_name": "bad_blocks",
  "label": "Bad Blocks Force badblocks On SSD",
  "related_components": [
    "test_tags.TestCategory.BRIDGE_PCIE_EMMC",
    "test_tags.TestCategory.STORAGE"
  ],
  "args": {
    "timeout_secs": 120,
    "log_threshold_secs": 10,
    "max_bytes": 1073741824,
    "force_badblocks_on_ssd": true
  }
}
```

## Troubleshooting

If the test image is installed by chromeos-install and pytest complains
there’s no unused space to be checked, re-install the image via factory shim
or netboot.  You can find different ways to install images at here:
[https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/README.md#Imaging-methods](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/README.md#Imaging-methods)

## Test Arguments

| Name                      | Type                                             | Description                                                                                                                                                                                               |
|---------------------------|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mode                      | [‘file’, ‘raw’, ‘stateful_partition_free_space’] | (optional; default: `<_TestModes.stateful_partition_free_space: 'stateful_partition_free_space'>`) Specify which operating mode to use.                                                                   |
| device_path               | str, None                                        | (optional; default: `None`) Override the device path on which to test. Also functions as a file path for file and raw modes.                                                                              |
| max_bytes                 | int, None                                        | (optional; default: `None`) Maximum size to test, in bytes.                                                                                                                                               |
| max_errors                | int                                              | (optional; default: `20`) Stops testing after the given number of errors.                                                                                                                                 |
| timeout_secs              | int, float                                       | (optional; default: `10`) Timeout in seconds for progress lines                                                                                                                                           |
| extra_log_cmd             | str, None                                        | (optional; default: `None`) Extra command to run at start/finish to collect logs.                                                                                                                         |
| log_threshold_secs        | int, float                                       | (optional; default: `5`) If no badblocks output is detected for this long, log an error but do not fail                                                                                                   |
| log_interval_secs         | int                                              | (optional; default: `60`) The interval between progress logs in seconds.                                                                                                                                  |
| drop_caches_interval_secs | int                                              | (optional; default: `120`) The interval between dropping caches in seconds.                                                                                                                               |
| destructive               | bool                                             | (optional; default: `True`) Do desctructive read / write test. If set to False, the data will be kept after testing, but longer testing time is expected.                                                 |
| force_badblocks_on_ssd    | bool                                             | (optional; default: `False`) SSD will maintain bad blocks on their own and only expose good blocks so badblocks is not that useful. smartctl output is still useful. Set this to force running badblocks. |
