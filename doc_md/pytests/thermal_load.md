# thermal_load

**Source code:** [thermal_load.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/thermal_load.py)

Tests thermal response under load.

## Description

Tests that under given load:

- Temperatures don’t go over temperature_limit before heat up.
- Temperatures go over lower_threshold within heat_up_timeout_secs.
- Temperatures don’t go over temperature_limit throughout the entire test.

## Test Procedure

This is an automated test without user interaction.

## Dependency

- Device API `cros.factory.device.thermal`.

## Examples

To use the test:

```default
{
  "pytest_name": "thermal_load",
  "args": {
    "lower_threshold": 40,
    "temperature_limit": 100,
    "heat_up_timeout_secs": 12,
    "duration_secs": 15
  }
}
```

## Test Arguments

| Name                    | Type            | Description                                                                                                                                      |
|-------------------------|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| load                    | int, None       | (optional; default: `None`) Number of threads stressapptest uses.  If None is used, this will default to the number of processors in the system. |
| heat_up_timeout_secs    | int             | (optional; default: `40`) Timeout interval in seconds for temperature to go over lower_threshold                                                 |
| duration_secs           | int             | (optional; default: `80`) Time in seconds for the test to run                                                                                    |
| lower_threshold         | int, list       | (optional; default: `45`) Minimum temperature value required within heat_up_timeout_secs                                                         |
| temperature_limit       | int, list       | (optional; default: `75`) Maximum temperature value allowed throughout the entire test.                                                          |
| sensors                 | str, list, None | (optional; default: `None`) List of temperature sensors to test. Default to main sensor, or “\*” for all sensors.                                |
| temperatures_difference | int, None       | (optional; default: `None`) The difference of temperatures should be under a specified limit.                                                    |
