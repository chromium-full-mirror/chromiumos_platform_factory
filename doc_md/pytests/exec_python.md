# exec_python

**Source code:** [exec_python.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/exec_python.py)

A test to run arbitrary python scripts.

## Description

This test executes the python script specified in script argument in an
empty context with only the current test_info object
(an instance of `cros.factory.goofy.invocation.PytestInfo`) provided.

This is intended to be a dummy test for other unittests like
goofy_unittest, usual factory procedure should not use this test.

## Test Procedure

This is an automated test without user interaction.

Runs the given script and fails if any exception raises during
execution.

## Dependency

None.

## Examples

A test that always pass:

```default
{
  "pytest_name": "exec_python",
  "args": {
    "script": "assert 1 == 1"
  }
}
```

## Test Arguments

| Name   | Type   | Description            |
|--------|--------|------------------------|
| script | str    | Python code to execute |
