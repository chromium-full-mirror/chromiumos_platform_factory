# check_test_list

**Source code:** [check_test_list.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_test_list.py)

A step to check test list.

## Description

Check if the test list exists before we use it.
ref: go/factory-smt-flow

## Test Procedure

1. Check if the given test list id exists.

## Dependency

None

## Examples

To check if RMA test list exists, add this to test list:

```default
{
  "pytest_name": "check_test_list",
  "args": {
    "test_list_id": "generic_rma"
  }
}
```

## Test Arguments

| Name         | Type   | Description                                |
|--------------|--------|--------------------------------------------|
| test_list_id | str    | An id of a test list needed to be checked. |
