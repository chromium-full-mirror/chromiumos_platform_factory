# battery_basic

**Source code:** [battery_basic.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/battery_basic.py)

A basic battery test.

## Description

This is a basic battery test that charges and discharges the battery on DUT.
The goal of this factory test is to perform a quick basic verification of
battery functions (typically less than 30 seconds).

## Test Procedure

1. Prompt the operator to plug in the AC power source.
2. The battery current is sampled periodically, and its value is checked.
3. Prompt the operator to unplug the AC power source.
4. The battery current is sampled periodically, and its value is checked.
5. Prompt the operator to plug in the AC power source, again.
6. The battery current is sampled periodically, and its value is checked.

## Dependency

Depend on the sysfs driver to control and read information from the battery.

## Examples

To perform a basic battery test, add this in test list:

```default
{
  "pytest_name": "battery_basic",
  "label": "Battery Basic",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ]
}
```

To relax the limitation of battery cycle count to 5:

```default
{
  "pytest_name": "battery_basic",
  "label": "Battery Basic Cycle Count At Most 5",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ],
  "args": {
    "max_cycle_count": 5
  }
}
```

## Test Arguments

| Name                         | Type             | Description                                                                                                            |
|------------------------------|------------------|------------------------------------------------------------------------------------------------------------------------|
| charge_duration_secs         | int, float       | (optional; default: `5`) the duration in seconds to charge the battery                                                 |
| discharge_duration_secs      | int, float       | (optional; default: `5`) the duration in seconds to discharge the battery                                              |
| min_charge_current_mA        | int, float, None | (optional; default: `None`) the minimum charge current in mA that the battery needs to reach during charge test        |
| min_discharge_current_mA     | int, float       | (optional; default: `-2000`) the minimum discharge current in mA that the battery needs to reach during discharge test |
| current_sampling_period_secs | int, float       | (optional; default: `0.5`) the period in seconds to sample charge/discharge current during test                        |
| max_cycle_count              | int              | (optional; default: `1`) the maximum cycle count beyond which the battery is consideredused                            |
