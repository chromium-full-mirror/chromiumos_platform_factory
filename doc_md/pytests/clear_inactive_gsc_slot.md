# clear_inactive_gsc_slot

**Source code:** [clear_inactive_gsc_slot.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/clear_inactive_gsc_slot.py)

Clears the inactive GSC RW slot.

## Description

Clears the inactive GSC RW slot to prevent unexpected version rollback.

## Test Procedure

The test clears the inactive GSC slot by running gsctool -a -c. No user
interaction is required.

## Dependency

gsctool

## Examples

To run the test, do:

```default
{
  "pytest_name": "clear_inactive_gsc_slot",
  "label": "Clear Inactive Ti50 Slot",
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT"
  ]
}
```

## Test Arguments

This test does not have any arguments.
