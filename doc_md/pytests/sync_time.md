# sync_time

**Source code:** [sync_time.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/sync_time.py)

Sync the clock of DUT with the clock of station.

## Description

This test set DUT clock to station clock time, and then check if the difference
between DUT clock time and station clock time exceeds a given threshold. If
exceeds, this test will fail.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. Firstly, this test will create a DUT link.
2. If the link is not a local link, DUT clock will be set to station clock time.
3. This test will check the difference between DUT clock time and station clock
   time, and fail if it exceeds the given tolerance. Otherwise, the test will
   pass.

## Dependency

- DUT link must be ready before running this test.

## Examples

To sync the clock of DUT with the clock of station with default tolerance, add
this in test list:

```default
{
  "pytest_name": "sync_time"
}
```

To sync with tolerance time set to 3 seconds:

```default
{
  "pytest_name": "sync_time",
  "args": {
    "tolerance": 3.0
  }
}
```

## Test Arguments

| Name      | Type   | Description                                                                                 |
|-----------|--------|---------------------------------------------------------------------------------------------|
| tolerance | float  | (optional; default: `5.0`) Max absolute time difference between DUT and station after sync. |
