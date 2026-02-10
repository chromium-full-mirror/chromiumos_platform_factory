# countdown

**Source code:** [countdown.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/countdown.py)

A count down monitor for better user interface in run-in tests.

## Description

Count down and display system load. This is helpful for run-in phase to run
multiple stress tests (for example, CPU, memory, disk, GPU, … etc) in
background so operator can see how long the run-in has been executed, and a
quick overview of system status.  It also alarms if there’s any abnormal status
(for example overheat) detected during run-in.

## Test Procedure

This test is designed to run in parallel with other background tests.
No user interaction is needed but if there were abnormal events operator should
collect debug logs for fault analysis.

## Dependency

- Thermal in Device API (cros.factory.device.thermal) for system thermal
  sensor readings.

## Examples

To run a set of tests for 120 seconds in parallel with countdown showing
progress, add this in test list:

```default
{
  "pytest_name": "countdown",
  "args": {
    "duration_secs": 120
  }
}
```

To run 8 hours and alert if main sensor (CPU) reaches 60 Celcius and fail when
exceeding 65 Celcius:

```default
{
  "pytest_name": "countdown",
  "args": {
    "duration_secs": 28800,
    "temp_criteria": [
      ["CPU", null, 60, 65]
    ]
  }
}
```

## Test Arguments

| Name                       | Type      | Description                                                                                                                                                                                                                                              |
|----------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| duration_secs              | int       | Duration of time to countdown.                                                                                                                                                                                                                           |
| log_interval               | int       | (optional; default: `120`) Interval of time in seconds to log system status.                                                                                                                                                                             |
| ui_update_interval         | int       | (optional; default: `10`) Interval of time in seconds to update system status on UI.                                                                                                                                                                     |
| wifi_update_interval       | int       | (optional; default: `0`) Interval of time in seconds to scan wifi.                                                                                                                                                                                       |
| bluetooth_update_interval  | int       | (optional; default: `0`) Interval of time in seconds to scan bluetooth.                                                                                                                                                                                  |
| als_update_interval        | int       | (optional; default: `0`) Interval of time in seconds to scan ALS.                                                                                                                                                                                        |
| grace_secs                 | int       | (optional; default: `120`) Grace period before starting abnormal status detection.                                                                                                                                                                       |
| temp_max_delta             | int, None | (optional; default: `None`) Allowed difference between current and last temperature of a sensor.                                                                                                                                                         |
| temp_criteria              | list      | (optional; default: `[]`) A list of rules to check that temperature is under the given range, rule format: (name, temp_sensor, warning_temp, critical_temp)                                                                                              |
| relative_temp_criteria     | list      | (optional; default: `[]`) A list of rules to check the difference between two temp sensors, rule format: (relation, first_sensor, second_sensor, max_diff). relation is a text output with warning messages to describe the two temp sensors in the rule |
| fan_min_expected_rpm       | int, None | (optional; default: `None`) Minimum fan rpm expected                                                                                                                                                                                                     |
| allow_invalid_temp         | bool      | (optional; default: `False`) Allow invalid temperature e.g. values less then or equal to zero, which may mean thermal nodes are not ready in early builds.                                                                                               |
| cpu_min_expected_freq      | int, None | (optional; default: `None`) Minimum CPU frequency expected. (unit: MHz)                                                                                                                                                                                  |
| cpu_max_expected_freq      | int, None | (optional; default: `None`) Maximum CPU frequency expected. (unit: MHz)                                                                                                                                                                                  |
| show_warn_on_display       | bool      | (optional; default: `True`) To show warnings on display during the test                                                                                                                                                                                  |
| terminate_on_critical_temp | bool      | (optional; default: `False`) To terminate all running tests when temperature reaches critical temperature.                                                                                                                                               |
