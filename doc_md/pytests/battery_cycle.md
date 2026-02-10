# battery_cycle

**Source code:** [battery_cycle.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/battery_cycle.py)

This test cycles the battery.

## Description

It runs for a particular number of cycles or number of hours and records,
cycling the battery between a minimum charge (e.g., 5%) and a maximum
charge (e.g., 95%).  Cycle times are logged to event logs.

### Internal references

- [https://chromeos.google.com/partner/dlm/docs/component-qual/index.html](https://chromeos.google.com/partner/dlm/docs/component-qual/index.html). See
  the “Power” section -> “Battery_Qualification Test Plan” ->
  “Battery Recharge Cycle Test”.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- Device API `cros.factory.device.power`.

## Examples

Add this into test list:

```default
{
  "pytest_name": "battery_cycle",
  "label": "Battery Cycle",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY"
  ]
}
```

## Test Arguments

| Name                  | Type             | Description                                                                                                                                                 |
|-----------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| num_cycles            | int, None        | (optional; default: `None`) Number of cycles to run                                                                                                         |
| max_duration_hours    | int, float, None | (optional; default: `None`) Maximum number of hours to run                                                                                                  |
| cycle_timeout_secs    | int              | (optional; default: `43200`) Maximum time for one charge/discharge cycle                                                                                    |
| minimum_charge_pct    | int, float       | (optional; default: `5`) Minimum charge, in percent                                                                                                         |
| maximum_charge_pct    | int, float       | (optional; default: `95`) Maximum charge, in percent                                                                                                        |
| charge_threshold_secs | int              | (optional; default: `30`) Amount of time the charge must remain above or below the specified threshold to have considered to have finished part of a cycle. |
| idle_time_secs        | int              | (optional; default: `1`) Time to idle between battery checks.                                                                                               |
| log_interval_secs     | int              | (optional; default: `30`) Interval at which to log system status.                                                                                           |
| verify_cutoff         | bool             | (optional; default: `False`) True to verify battery stops charging when ~100%                                                                               |
| cutoff_charge_pct     | int, float       | (optional; default: `98`) Minimum charge level in percent allowed in cutoff state.                                                                          |
| fast_discharge        | bool             | (optional; default: `True`) Use stressapptest in discharge phase to discharge faster                                                                        |
