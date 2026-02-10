# partition_table

**Source code:** [partition_table.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/partition_table.py)

Checks that the partition table extends nearly to the end of the storage
device.

## Description

This test checks if the partition table allocates at least `min_usage_pct`
percent of the storage. If not, this test expands stateful partition to the end
of the storage device by default. However, on disk_layout_v3, MINIOS-B locates
at the end of the partition table. This test will cache and remove MINIOS-B,
expand stateful partition and copy MINIOS-B back. This test will also resize
MINIOS-B so that its size is the same as MINIOS-A.

This test doesn’t check the actual size of the stateful partition, rather the
sector at which it ends.

This test doesn’t support remote device.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- pygpt utility.

## Examples

To run this pytest with default arguments, add this in test list:

```default
{
  "pytest_name": "partition_table"
}
```

This is also predefined in `generic_common.test_list.json` as
`PartitionTable`.

If you can’t expand stateful partition for some reason, override the argument
by:

```default
{
  "inherit": "PartitionTable",
  "args": {
    "expand_stateful": false
  }
}
```

## Test Arguments

| Name            | Type       | Description                                                                                                                                                                                                                                                  |
|-----------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| min_usage_pct   | int, float | (optional; default: `95`) Percentage of the storage device that must be before the end of the stateful partition.  For example, if this is 95%, then the stateful partition must end at a sector that is >=95% of the total number of sectors on the device. |
| expand_stateful | bool       | (optional; default: `True`) Repair partition headers and tables and expand stateful partition to all available free space                                                                                                                                    |
