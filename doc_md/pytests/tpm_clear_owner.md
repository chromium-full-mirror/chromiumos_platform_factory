# tpm_clear_owner

**Source code:** [tpm_clear_owner.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/tpm_clear_owner.py)

Requests that the firmware clear the TPM owner on the next reboot.

## Description

It’s required that the owner is cleared on the first boot out of factory.

Users want to minimize the number of reboot in GRT so we don’t put this in GRT.

If a user forgets to clear the owner before [Finalize](finalize.md) then the
Finalize will fail at the VerifyTPM.

This should generally be followed by a reboot step.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- `crossystem clear_tpm_owner_request`
- `crossystem clear_tpm_owner_done`

## Examples

An example:

```default
{
  "label": "ClearTPMOwnerRequestGroup",
  "subtests": [
    {
      "pytest_name": "tpm_clear_owner",
      "label": "TPM Clear Owner",
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT",
        "test_tags.TestCategory.TPM"
      ],
      "action_on_failure": "STOP"
    },
    {
      "inherit": "ShutdownStep",
      "pytest_name": "shutdown",
      "label": "Reboot",
      "allow_reboot": true,
      "action_on_failure": "STOP",
      "args": {
        "operation": "reboot"
      }
    }
  ]
}
```

## Test Arguments

| Name                  | Type   | Description                                                               |
|-----------------------|--------|---------------------------------------------------------------------------|
| only_check_clear_done | bool   | (optional; default: `False`) Only check crossystem clear_tpm_owner_done=1 |
