# thermal_slope

**Source code:** [thermal_slope.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/thermal_slope.py)

Determines how fast the processor heats/cools.

## Description

The purpose of this test is to detect devices without thermal paste.

The user should prepare one device with thermal paste and another device without
it, run the tests on both of them, and then select the threshold of max_slope.

Different CPUs on the same board or the same CPU on different boards may have
different max_slope distribution so the user should set different thresholds for
different (model, CPU).

## Test Procedure

This is an automated test without user interaction.

### Details

1. ‘cool_down’ stage: Runs the fan at <cool_down_fan_rpm> until it
   reaches <cool_down_temperature_c> (at least
   <cool_down_min_duration_secs> but at most
   <cool_down_max_duration_secs>).  Fails if unable to cool down to
   <cool_down_max_temperature_c>.
2. ‘idle’ stage: Spins the fan to <target_fan_rpm> and waits
   <fan_spin_down_secs>.
3. ‘one_core’ stage: Runs one core at full speed for <duration_secs>.
4. Determines the thermal slope during this period.  The thermal slope
   is defined as
   > ΔT / ΔP / Δt

   where
   > ΔT is the change in temperature between the idle and one_core stages.
   > ΔP is the change in power usage between the idle and one_core stages.
   > Δt is the amount of time the one_core stage was run

   If the thermal slope is not between min_slope and max_slope, the test
   fails.

## Dependency

- Device API `cros.factory.device.fan`.
- Device API `cros.factory.device.memory`.
- Device API `cros.factory.device.storage`.
- Device API `cros.factory.device.thermal`.

## Examples

To collect the slope of a setting:

```default
{
  "pytest_name": "thermal_slope",
  "args": {
    "cool_down_fan_rpm": 9999,
    "cool_down_min_duration_secs": 100,
    "cool_down_max_duration_secs": 600,
    "cool_down_temperature_c": 81,
    "cool_down_max_temperature_c": 94,
    "target_fan_rpm": 5001,
    "fan_spin_down_secs": 10,
    "duration_secs": 60,
    "min_slope": null,
    "max_slope": null
  }
}
```

To fail the device with slope out of range:

```default
{
  "pytest_name": "thermal_slope",
  "args": {
    "cool_down_fan_rpm": 9999,
    "cool_down_min_duration_secs": 100,
    "cool_down_max_duration_secs": 600,
    "cool_down_temperature_c": 81,
    "cool_down_max_temperature_c": 94,
    "target_fan_rpm": 5001,
    "fan_spin_down_secs": 10,
    "duration_secs": 60,
    "min_slope": 0.05,
    "max_slope": 0.20
  }
}
```

## Test Arguments

| Name                        | Type             | Description                                                                                                                                                 |
|-----------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| cool_down_fan_rpm           | int, float, str  | (optional; default: `10000`) Fan RPM during cool_down, or the string “auto”.                                                                                |
| cool_down_min_duration_secs | int, float       | (optional; default: `10`) Minimum duration of cool_down                                                                                                     |
| cool_down_max_duration_secs | int, float       | (optional; default: `60`) Maximum duration of cool_down                                                                                                     |
| cool_down_temperature_c     | int, float       | (optional; default: `50`) Target temperature for cool_down                                                                                                  |
| cool_down_max_temperature_c | int, float, None | (optional; default: `None`) Maximum allowable temperature after cool_down (if higher than this, the test will not run). Defaults to cool_down_temperature_c |
| target_fan_rpm              | int, float, str  | (optional; default: `4000`) Target RPM of fan during slope test, or the string “auto”.                                                                      |
| fan_spin_down_secs          | int, float       | (optional; default: `5`) Number of seconds to allow for fan spin down                                                                                       |
| duration_secs               | int, float       | (optional; default: `5`) Duration of slope test                                                                                                             |
| min_slope                   | int, float, None | (optional; default: `None`) Minimum allowable thermal slope in °C/J                                                                                         |
| max_slope                   | int, float, None | (optional; default: `None`) Maximum allowable thermal slope in °C/J                                                                                         |
| console_log                 | bool             | (optional; default: `False`) Enable console log (disabling may make results more accurate since updating the console log on screen requires CPU cycles)     |
| sensor_id                   | str, None        | (optional; default: `None`) An id to specify the power sensor. See Thermal.GetPowerUsage.                                                                   |
