# tpm_state

**Source code:** [tpm_state.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/tpm_state.py)

A test to check the state of TPM die.

## Description

A test to verify if TPM is in fused off state from the cbmem command. This
test requires a normal version of the firmware. We cannot use “serial” or “dev”
version of firmware. We need the normal version because the HSP state log will
be washed off if using serial or dev firmware.

Only needed and applicable for certain projects.

### Internal references

- b/198711349

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- Normal firmware.
- `cbmem` utility.

## Examples

To verify the tpm state, add this to test list:

```default
{
  "pytest_name": "tpm_state",
  "label": "Verify TPM state",
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT",
    "test_tags.TestCategory.TPM"
  ]
}
```

## Test Arguments

This test does not have any arguments.
