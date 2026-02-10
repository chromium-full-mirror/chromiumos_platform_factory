# switch_test_list

**Source code:** [switch_test_list.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/switch_test_list.py)

A step to switch test list.

## Description

Switching test list automatically to support different factory process.
ref: go/factory-smt-flow

## Test Procedure

1. Switch to the given test list id.

## Dependency

None

## Examples

To switch to RMA test list, add this to test list:

```default
{
  "pytest_name": "switch_test_list",
  "args": {
    "test_list_id": "generic_rma"
  }
}
```

## Test Arguments

| Name         | Type   | Description                                 |
|--------------|--------|---------------------------------------------|
| test_list_id | str    | An id of a test list needed to be switched. |
