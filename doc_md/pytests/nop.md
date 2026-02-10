# nop

**Source code:** [nop.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/nop.py)

An no-op test.

## Description

This test does nothing but waits for a given period of time.

The length of time is given in wait_secs.

## Test Procedure

No user interaction is required, the test waits wait_secs seconds and pass.

## Dependency

None.

## Examples

To wait for 5 seconds, add this in test list:

```default
{
  "pytest_name": "nop",
  "args": {
    "wait_secs": 5
  }
}
```

## Test Arguments

| Name      | Type       | Description                                  |
|-----------|------------|----------------------------------------------|
| wait_secs | int, float | (optional; default: `0`) Wait for N seconds. |
