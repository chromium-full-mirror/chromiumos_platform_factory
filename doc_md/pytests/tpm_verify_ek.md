# tpm_verify_ek

**Source code:** [tpm_verify_ek.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/tpm_verify_ek.py)

Verifies the TPM endorsement key.

## Description

This test (whether it succeeds or fails) always requests a TPM clear
on reboot.  It works even if run multiple times without rebooting.

If the TPM is somehow owned but no password is available, the test
will fail but emit a reasonable error message (and it will pass on the
next boot).

This should generally be followed by a reboot step.

## Test Procedure

This is an automated test without user interaction.

## Dependency

A workable TPM with endorsement key on it.
And hardware security daemons & clients.

## Examples

Examples of how to use this test:

```default
{
  "label": "TPMVerifyEKGroup",
  "retries": 1,
  "subtests": [
    {
      "pytest_name": "tpm_verify_ek",
      "label": "TPM Verify EK",
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT",
        "test_tags.TestCategory.TPM"
      ]
    },
    {
      "inherit": "ShutdownStep",
      "pytest_name": "shutdown",
      "label": "Reboot",
      "allow_reboot": true,
      "args": {
        "operation": "reboot"
      }
    }
  ]
}
```

## Test Arguments

| Name         | Type   | Description                                                        |
|--------------|--------|--------------------------------------------------------------------|
| is_cros_core | bool   | (optional; default: `False`) Verify with ChromeOS Core endorsement |
