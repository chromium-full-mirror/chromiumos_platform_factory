# thermal_sensors

**Source code:** [thermal_sensors.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/thermal_sensors.py)

Test for temperature sensors control.

## Description

The test uses device API to check if temperature sensors is connected and the
temperature lies in the given range temp_range.

## Test Procedure

This is an automated test without user interaction.

## Dependency

Device API cros.factory.device.thermal.

This is usually implemented in /sys with properties like thermal_zone
or command ectool temps / ectool tempsinfo.

## Examples

To check if the temperature sensors is connected and temperature is in default
range ([0, 100]), add this in test list:

```default
{
  "pytest_name": "thermal_sensors"
}
```

To check if the temperature is in range [30, 80], add this in test list:

```default
{
  "pytest_name": "thermal_sensors",
  "args": {
    "temp_range": [30, 80]
  }
}
```

## Test Arguments

| Name                | Type            | Description                                                                                                                                  |
|---------------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| temp_sensor_to_test | str, list, None | (optional; default: `None`) List of temperature sensor(s) to test, “\*” for all sensors. Default to test only the main sensor (usually CPU). |
| temp_range          | list            | (optional; default: `[0, 100]`) [min_temp, max_temp] in Celsius.                                                                             |
