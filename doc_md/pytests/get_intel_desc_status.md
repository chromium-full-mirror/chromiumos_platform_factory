# get_intel_desc_status

**Source code:** [get_intel_desc_status.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/get_intel_desc_status.py)

Gets the status of Intel SI_DESC and sets the status to device data.

## Description

This pytest gets the status of Intel SI_DESC (lock/unlock) and sets the device
data factory.intel_desc_locked accordingly.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- flashrom and ifdtool

## Examples

To get the status of Intel SI_DESC, add this in test list:

```default
{
  "pytest_name": "get_intel_desc_status"
}
```

## Test Arguments

This test does not have any arguments.
