# battery

**Source code:** [battery.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/battery.py)

A test to check if DUT can communicate with battery.

## Description

The test uses device API to get battery design capacity, and check that the
capacity lies in the range given in design_capacity_range.

## Test Procedure

This is an automated test without user interaction.

## Dependency

Device API power.GetBatteryDesignCapacity.

This is usually implemented in /sys with properties like charge_full_design
or command ectool battery.

## Examples

To check if the battery design capacity lies in default range ([1000, 10000]),
add this in test list:

```default
{
  "pytest_name": "battery",
  "label": "Battery Capacity",
  "run_if": "constants.has_battery",
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ]
}
```

To check if the battery design capacity lies in [4000, 8000], add this in test
list:

```default
{
  "pytest_name": "battery",
  "label": "Battery Capacity Between 4000 And 8000",
  "run_if": "constants.has_battery",
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ],
  "args": {
    "design_capacity_range": [
      4000,
      8000
    ]
  }
}
```

## Test Arguments

| Name                  | Type   | Description                                                                                            |
|-----------------------|--------|--------------------------------------------------------------------------------------------------------|
| design_capacity_range | list   | (optional; default: `[1000, 10000]`) Expected battery design capacity range in mAh.  Ex: [1000, 10000] |
