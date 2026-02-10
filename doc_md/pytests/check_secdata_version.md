# check_secdata_version

**Source code:** [check_secdata_version.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_secdata_version.py)

A factory test to check the secdata version.

## Description

This test checks if the secdata version is the expected version.

Secdata is set by AP firmware. If the test fails, please confirm the expected
secdata version with the firmware team, and check if the AP firmware is too old.

According to platform/vboot_reference/firmware/2lib/include/2secdata_struct.h,
secdata version is an 8-bit integer defined as (major << 4 | minor << 0).

## Test Procedure

This is an automatic test that doesn’t need any user interaction.
Ideally the test should always pass. However, if the test fails, we need to
clear secdata and let the system regenerate it again. It can be done by

> - Re-enable cr50 factory mode (gsctool -a -F enable), or
> - Run chromeos-tpm-recovery by “(T) Reset TPM” action or “(R) Reset” action
>   in a factory shim, depending on whether the device is finalized or not

## Dependency

- tpmc
- trunksd not running.

## Examples

To verify that secdata version is 1.0:

```default
{
  "pytest_name": "check_secdata_version",
  "label": "Check Secdata Version",
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT",
    "test_tags.TestCategory.TPM"
  ],
  "disable_services": [
    "trunksd"
  ],
  "args": {
    "major_version": 1,
    "minor_version": 0
  }
}
```

## Test Arguments

| Name          | Type   | Description                                        |
|---------------|--------|----------------------------------------------------|
| major_version | int    | (optional; default: `1`) Major version of secdata. |
| minor_version | int    | (optional; default: `0`) Minor version of secdata. |
