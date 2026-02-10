# battery_sysfs

**Source code:** [battery_sysfs.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/battery_sysfs.py)

A hardware test for checking battery existence and its basic status.

## Description

This test checks the battery existence and its status like cycle count,
wear level, and health status.

## Test Procedure

This is an automated test without user interaction.

## Dependency

Depend on the sysfs driver to read information from the battery.

## Examples

To perform a battery test, add this in test list:

```default
{
  "pytest_name": "battery_sysfs",
  "label": "Battery Sysfs",
  "run_if": "constants.has_battery",
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ],
  "args": {
    "maximum_cycle_count": 10,
    "percent_battery_wear_allowed": 5
  }
}
```

- To disable max cycle count check, set `maximum_cycle_count` to `-1`.
- To disable wear level check, set `percent_battery_wear_allowed` to `-1`.

## Test Arguments

| Name                         | Type   | Description                                                                |
|------------------------------|--------|----------------------------------------------------------------------------|
| maximum_cycle_count          | int    | (optional; default: `10`) Maximum cycle count allowed to pass test         |
| percent_battery_wear_allowed | int    | (optional; default: `5`) Maximum percent battery wear allowed to pass test |
