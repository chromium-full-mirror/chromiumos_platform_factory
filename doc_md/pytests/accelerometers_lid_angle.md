# accelerometers_lid_angle

**Source code:** [accelerometers_lid_angle.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/accelerometers_lid_angle.py)

This is a lid angle test based on accelerometers.

## Description

There are two accelerometers in ChromeOS for lid angle calculation.
This test asks OP to turn lid angle into a desired angle and then
checks whether the lid angle is within some threshold.
Please notice this test requires the hinge to be in a horizontal plane.

## Test Procedure

1. Bend the device (base/lid) into a desired angle then press space.
2. Wait for completion.

## Dependency

- Device API (`cros.factory.device.accelerometer`).

## Examples

Usage examples:

```default
{
  "pytest_name": "accelerometers_lid_angle",
  "label": "Accelerometers Lid Angle",
  "run_if": "not constants.has_device_data or (device.component.has_lid_accelerometer and device.component.has_base_accelerometer)",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER",
    "test_tags.TestCategory.VPD"
  ],
  "args": {
    "angle": 180,
    "tolerance": 5,
    "spec_offset": [
      0.5,
      0.5
    ]
  }
}
```

## Test Arguments

| Name           | Type   | Description                                                                                                     |
|----------------|--------|-----------------------------------------------------------------------------------------------------------------|
| angle          | int    | (optional; default: `180`) The target lid angle in degree to test.                                              |
| tolerance      | int    | (optional; default: `5`) The tolerance in degree.                                                               |
| capture_count  | int    | (optional; default: `20`) How many times to capture the raw data to calculate the lid angle.                    |
| spec_offset    | list   | Two numbers, ex: [0.5, 0.5] indicating the tolerance in m/s^2 for the digital output of sensors under 0 and 1G. |
| autostart      | bool   | (optional; default: `False`) Starts the test automatically without prompting.                                   |
| sample_rate_hz | int    | (optional; default: `200`) The sample rate in Hz to get raw data from accelerometers.                           |
