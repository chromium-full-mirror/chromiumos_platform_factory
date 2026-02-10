# mrc_cache

**Source code:** [mrc_cache.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/mrc_cache.py)

A factory test to initiate and verify memory re-training process.

## Description

The test either requests memory re-training on next boot (if `mode` is
`'create'`), or verifies the MRC cache. (if `mode` is `'verify_update'`
or `'verify_no_update'`).

Please refer to py/tools/mrc_cache.py for more details.

## Test Procedure

This is an automated test without user interaction.

## Dependency

`flashrom`

## Examples

To run the complete memory training and verification flow described in
py/tools/mrc_cache.py, add this to test list:

```default
{
  "label": "MRC Cache",
  "subtests": [
    {
      "pytest_name": "mrc_cache",
      "label": "Create Cache",
      "related_components": [
        "test_tags.TestCategory.DRAM"
      ],
      "args": {
        "mode": "create"
      }
    },
    {
      "inherit": "ShutdownStep",
      "pytest_name": "shutdown",
      "label": "Reboot",
      "allow_reboot": true,
      "args": {
        "operation": "reboot"
      }
    },
    {
      "pytest_name": "mrc_cache",
      "label": "Verify Cache Update",
      "related_components": [
        "test_tags.TestCategory.DRAM"
      ],
      "args": {
        "mode": "verify_update"
      }
    },
    {
      "inherit": "ShutdownStep",
      "pytest_name": "shutdown",
      "label": "Reboot",
      "allow_reboot": true,
      "args": {
        "operation": "reboot"
      }
    },
    {
      "pytest_name": "mrc_cache",
      "label": "Verify Cache No Update",
      "related_components": [
        "test_tags.TestCategory.DRAM"
      ],
      "args": {
        "mode": "verify_no_update"
      }
    }
  ]
}
```

## Test Arguments

| Name   | Type   | Description                                                                                                                                                                                                                                                                                           |
|--------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mode   | str    | Specify the phase of the test, valid values are:<br/>- “create”: erase MRC cache and request memory retraining on the next boot.<br/>- “verify_update”: verify the MRC cache update result and request memory retraining on next boot.<br/>- “verify_no_update”: verify the MRC cache is not updated. |
