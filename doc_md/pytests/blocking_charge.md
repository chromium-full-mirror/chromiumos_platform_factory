# blocking_charge

**Source code:** [blocking_charge.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/blocking_charge.py)

Test that waits the battery to be charged to specific level.

## Description

The test waits until the battery is charged to the given level, and pass.

The `target_charge_pct` sets the target charge level in percentage.
`target_charge_pct` can be set to some special values:

* `"goofy"`: Use `min_charge_pct` from Goofy’s charge_manager plugin as
  target charge level.
* `"cutoff"`: Use `CUTOFF_BATTERY_MIN_PERCENTAGE` from cutoff.json as
  target charge level.

If `target_charge_pct_is_delta` is True, `target_charge_pct` would be
interpreted as difference to current charge level.

If battery doesn’t reach the target level in `timeout_secs` seconds, the test
would fail.

## Test Procedure

This is an automated test without user interaction.

1. A screen would be shown with current battery level, target battery level,
   and time remaining.
2. Test would pass when battery reach target level, or fail if test run longer
   than `timeout_secs`.

## Dependency

Device API cros.factory.device.power.

## Examples

To charge the device to `min_charge_pct` in Goofy charge_manager (default
behavior), add this in test list:

```default
{
  "pytest_name": "blocking_charge",
  "label": "Blocking Charge",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ]
}
```

To charge the device to minimum battery level needed for cutoff, add this in
test list:

```default
{
  "pytest_name": "blocking_charge",
  "label": "Blocking Charge To Cut Off Setting",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ],
  "args": {
    "target_charge_pct": "cutoff"
  }
}
```

To charge the device to 75 percent, add this in test list:

```default
{
  "pytest_name": "blocking_charge",
  "label": "Blocking Charge To 75",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ],
  "args": {
    "target_charge_pct": 75
  }
}
```

To charge the device 10 percent more, and only allow 5 minutes time for
charging, add this in test list:

```default
{
  "pytest_name": "blocking_charge",
  "label": "Blocking Charge 10 Percent More In 5 Minutes",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ],
  "args": {
    "target_charge_pct_is_delta": true,
    "timeout_secs": 300,
    "target_charge_pct": 10
  }
}
```

## Test Arguments

| Name                       | Type                     | Description                                                                          |
|----------------------------|--------------------------|--------------------------------------------------------------------------------------|
| target_charge_pct          | int, [‘cutoff’, ‘goofy’] | (optional; default: `'goofy'`) Target charge level.                                  |
| target_charge_pct_is_delta | bool                     | (optional; default: `False`) Specify target_charge_pct is a delta of current charge  |
| timeout_secs               | int                      | (optional; default: `3600`) Maximum allowed time to charge battery                   |
| dim_backlight              | bool                     | (optional; default: `True`) Turn backlight/screen brightness lower to charge faster. |
| dim_backlight_pct          | float                    | (optional; default: `3.0`) The brightness in linear % when charging.                 |
| log_check_interval         | int                      | (optional; default: `10`) Period of Log checking in seconds                          |
