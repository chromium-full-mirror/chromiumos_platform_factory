# hps

**Source code:** [hps.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/hps.py)

A factory test for HPS (Human Presence Sensor).

## Description

The test is a wrapper of hps-factory.

## Test Procedure

This is an automated test without user interaction.

## Dependency

- hps-factory

## Examples

To test HPS, add this into test list:

```default
{
  "pytest_name": "hps"
}
```

## Test Arguments

| Name             | Type      | Description                                                                                                |
|------------------|-----------|------------------------------------------------------------------------------------------------------------|
| hps_factory_path | str       | (optional; default: `'hps-factory'`) The path of the hps-factory binary.                                   |
| dev              | str, None | (optional; default: `None`) The path of the HPS device. If not set, use the default value in ‘hps-factory’ |
| timeout_secs     | int       | (optional; default: `3600`) The timeout of the test command.                                               |
