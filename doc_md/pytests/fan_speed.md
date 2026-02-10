# fan_speed

**Source code:** [fan_speed.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/fan_speed.py)

A factory test to ensure the functionality of CPU fan.

## Description

It provides two types of test:

1. target_rpm mode
2. spin_max_then_half mode.

For mode B, it first spins fan up to a max_rpm to get an empirical maximum
fan rpm; then it runs mode A with half of the empirical max rpm as target_rpm.

In mode A, the steps are:

1. Sets the fan speed to a target RPM.
2. Monitors the fan speed for a given period (duration_secs) with sampling
   interval (probe_interval_secs). Then it takes average of the latest
   num_samples_to_use samples as the stabilized fan speed reading.
3. Checks that the averaged reading is within range
   [target_rpm - error_margin, target_rpm + error_margin].

Some system services like dptf may change the fan speed while testing so users
have to disable them with test object option “disable_services”. See Examples.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- Device API `cros.factory.device.fan`.

## Examples

An example:

```default
{
  "pytest_name": "fan_speed",
  "label": "Fan Speed",
  "run_if": "constants.has_fan",
  "disable_services": [
    "dptf"
  ],
  "args": {
    "probe_interval_secs": 0.2,
    "target_rpm": [
      3000,
      4500,
      6000
    ],
    "error_margin": 300
  }
}
```

If you prefer to use 7% as error margin:

```default
{
  "pytest_name": "fan_speed",
  "label": "Fan Speed",
  "run_if": "constants.has_fan",
  "disable_services": [
    "dptf"
  ],
  "args": {
    "probe_interval_secs": 0.2,
    "target_rpm": [
      3000,
      4500,
      6000
    ],
    "error_margin": 7,
    "error_margin_use_percentage": true
  }
}
```

## Test Arguments

| Name                        | Type       | Description                                                                                                                                                                         |
|-----------------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| target_rpm                  | int, list  | (optional; default: `0`) A list of target RPM to set during test.Unused if spin_max_then_half is set.                                                                               |
| error_margin                | int        | (optional; default: `200`) Fail the test if actual fan speed is off the target by the margin default in units of RPM                                                                |
| duration_secs               | int, float | (optional; default: `10`) Duration of monitoring fan speed in seconds.                                                                                                              |
| spin_max_then_half          | bool       | (optional; default: `False`) If True, spin the fan to max_rpm, measure the actual reading, and set fan speed to half of actual max speed. Note that if True, target_rpm is invalid. |
| max_rpm                     | int        | (optional; default: `10000`) A relatively high RPM for probing maximum fan speed. It is used when spin_max_then_half=True.                                                          |
| probe_interval_secs         | float      | (optional; default: `0.2`) Interval of probing fan speed in seconds.                                                                                                                |
| num_samples_to_use          | int        | (optional; default: `5`) Number of lastest samples to count average as stablized speed.                                                                                             |
| speed_use_percentage        | bool       | (optional; default: `False`) Use percentage to set fan speed                                                                                                                        |
| error_margin_use_percentage | bool       | (optional; default: `False`) Use percentage to set error margin                                                                                                                     |
| fan_id                      | int, None  | (optional; default: `None`) The ID of fan to test, use None to test all fans.                                                                                                       |
