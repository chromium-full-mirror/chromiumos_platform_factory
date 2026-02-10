# setup_psr_feature

**Source code:** [setup_psr_feature.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/setup_psr_feature.py)

A test to set/check PSR EOM NVAR and start PSR Log.

## Description

This test does one of these action: set EOM NVAR(close manufacturing), check
EOM NVAR value equals 1 or start PSR log.

## Test Procedure

This pytest does not require operator interaction.

## Dependency

- intel-psrtool

## Examples

To set PSR EOM NVAR, add this to test list:

```default
{
  "pytest_name": "setup_psr_feature",
  "args": {
    "action": "set"
  }
}
```

To start PSR log, add this to test list:

```default
{
  "pytest_name": "setup_psr_feature",
  "args": {
    "action": "start"
  }
}
```

## Test Arguments

| Name   | Type             | Description         |
|--------|------------------|---------------------|
| action | [‘set’, ‘start’] | Which action to do. |
