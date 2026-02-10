# urandom

**Source code:** [urandom.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/urandom.py)

A factory test to stress CPU, by generating pseudo random numbers.

## Description

It stresses CPU by generating random number using /dev/urandom for a specified
period of time (specified by `duration_secs`).

## Test Procedure

This is an automated test without user interaction.

Start the test and it will run for the time specified in argument
`duration_secs`, and pass if no errors found; otherwise fail with error
messages and logs.

## Dependency

No dependencies.  This test does not support remote DUT.

## Examples

To generate random number and stress CPU for 4 hours, add this in test list:

```default
{
  "pytest_name": "urandom",
  "args": {
    "duration_secs": 14400
  }
}
```

## Test Arguments

| Name          | Type   | Description                   |
|---------------|--------|-------------------------------|
| duration_secs | int    | How long this test will take? |
