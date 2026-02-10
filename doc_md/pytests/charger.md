# charger

**Source code:** [charger.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/charger.py)

Test if the charger can charge battery in time.

## Description

Test that charger can charge/discharge battery for certain amount of change
within certain time under certain load.

## Test Procedure

1. The battery and AC must present before running the test.
2. This is an automated test without user interaction.

## Dependency

Device API cros.factory.device.power.

## Examples

A test that charges/discharges until the battery percentage is 87 with 1 hour
timeout:

```default
{
  "pytest_name": "charger",
  "label": "Charger",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ],
  "args": {
    "min_starting_charge_pct": 87,
    "max_starting_charge_pct": 87,
    "check_battery_current": false,
    "starting_timeout_secs": 3600,
    "spec_list": []
  }
}
```

## Test Arguments

| Name                    | Type       | Description                                                                                                                                                                                                                                                                                                                                                                                                          |
|-------------------------|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| min_starting_charge_pct | int, float | (optional; default: `20.0`) minimum starting charge level when testing                                                                                                                                                                                                                                                                                                                                               |
| max_starting_charge_pct | int, float | (optional; default: `90.0`) maximum starting charge level when testing                                                                                                                                                                                                                                                                                                                                               |
| starting_timeout_secs   | int        | (optional; default: `300`) Maximum allowed time to regulatebattery to starting_charge_pct                                                                                                                                                                                                                                                                                                                            |
| check_battery_current   | bool       | (optional; default: `True`) Check battery current > 0when charging and < 0 when discharging                                                                                                                                                                                                                                                                                                                          |
| battery_check_delay_sec | int        | (optional; default: `3`) Delay of checking battery current. This can be used to handle slowly settled battery current.                                                                                                                                                                                                                                                                                               |
| verbose_log_period_secs | int        | (optional; default: `3`) Log debug data every x seconds to verbose log file.                                                                                                                                                                                                                                                                                                                                         |
| log_period_secs         | int        | (optional; default: `60`) Log test data every x seconds.                                                                                                                                                                                                                                                                                                                                                             |
| use_percentage          | bool       | (optional; default: `True`) True if using percentage as charge unit in spec list. False if using mAh.                                                                                                                                                                                                                                                                                                                |
| charger_type            | str, None  | (optional; default: `None`) Type of charger required.                                                                                                                                                                                                                                                                                                                                                                |
| spec_list               | list       | (optional; default: `[[2, 300, 1], [-2, 300]]`) A list of [charge_change, timeout_secs, load]<br/>Charger needs to achieve charge_change difference within<br/>timeout_secs seconds under load.<br/>Positive charge_change is for charging and negative one is<br/>for discharging.<br/>One unit of load is one thread doing memory copy in stressapptest.<br/>The default value for load is the number of processor |
