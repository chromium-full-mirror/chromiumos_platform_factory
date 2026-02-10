# copy_minios

**Source code:** [copy_minios.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/copy_minios.py)

Selectively copies the miniOS part that has the same recovery key ver as FW.

## Description

miniOS A/B are signed with different recovery key, with A signed with the old
one and B signed with the new one. This test copies the miniOS partition with
the same recovery key version as firmware and overrides the other miniOS
partition.

## Test Procedure

1. Checks if DUT is using disk_layout_v3. If not, ends the test.
2. Gets the recovery key version from the firmware.
3. If the recovery key version is 1, uses miniOS A as source part.
   Else uses miniOS B.
4. Copies the source partition to the destination partition.
5. Now the miniOS A and minios B are the same.

## Dependency

gbb_utility, futility

## Examples

To run the test, do:

```default
{
  "pytest_name": "copy_minios"
}
```

## Test Arguments

This test does not have any arguments.
