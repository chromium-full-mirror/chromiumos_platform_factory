# verify_keybox

**Source code:** [verify_keybox.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/verify_keybox.py)

A test to check the correctness of widevine keybox.

## Description

To verify if the keybox is written by provision_drm_key.py.

## Test Procedure

1. Read keybox from vpd.
2. Calculate the checksum of the keybox.
3. Compare the calculated checksum with the current checksum.

## Dependency

This test relies on `vpd` component in Device API to access VPD.

## Examples

To verify the keybox, add this to test list:

```default
{
  "pytest_name": "verify_keybox",
}
```

## Test Arguments

This test does not have any arguments.
