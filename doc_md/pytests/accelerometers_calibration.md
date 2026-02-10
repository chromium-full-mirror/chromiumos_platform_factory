# accelerometers_calibration

**Source code:** [accelerometers_calibration.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/accelerometers_calibration.py)

A factory test for accelerometers calibration.

## Description

This is a calibration test for tri-axis (x, y, and z) accelerometers.

From one accelerometer, we can obtain digital output proportional to the linear
acceleration in each axis. If we put it on a flat table we can get
(x, y, z) = (0, 0, 9.8) at an ideal case. For upside down we’ll have
(x, y, z) = (0, 0, -9.8).

Since accelerometer is very sensitive, the digital output will be different
for each query. For example, (0.325, -0.278, 9.55).
In addition, temperature or the assembly quality may impact the accuracy
of the accelerometer during manufacturing (ex, position is tilt). To mitigate
this kind of errors, we’ll sample several records of raw data and compute
its average value under an ideal environment. Then store the offset as
a calibrated value for future calculation.

In a horizontal calibration, we’ll put accelerometers on a flat position then
sample 100 records of raw data. In this position, two axes are under 0g and
one axis is under 1g. Then we’ll update the calibration bias using the
difference between the ideal value (0 and +/-9.8 in the example above) and
the average value of 100 samples.

## Test Procedure

1. Put the device (base/lid) on a horizontal plane then press space.
2. Wait for completion.

## Dependency

- Device API (`cros.factory.device.accelerometer`).

## Examples

To run horizontal calibration on base accelerometer:

```default
{
  "pytest_name": "accelerometers_calibration",
  "label": "Base Accelerometers Calibration",
  "run_if": "not constants.has_device_data or device.component.has_base_accelerometer",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "orientation": {
      "in_accel_x": 0,
      "in_accel_y": 0,
      "in_accel_z": 1
    },
    "spec_offset": [
      0.5,
      0.5
    ],
    "location": "base"
  }
}
```

To run horizontal calibration on lid accelerometer:

```default
{
  "pytest_name": "accelerometers_calibration",
  "label": "Lid Accelerometers Calibration",
  "run_if": "not constants.has_device_data or device.component.has_lid_accelerometer",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "orientation": {
      "in_accel_x": 0,
      "in_accel_y": 0,
      "in_accel_z": 1
    },
    "spec_offset": [
      0.5,
      0.5
    ],
    "location": "lid"
  }
}
```

## Test Arguments

| Name               | Type            | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|--------------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| calibration_method | [‘horizontal’]  | (optional; default: `'horizontal'`) Currently there is only one calibration method available: horizontal calibration.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| orientation        | dict            | Keys: the name of the accelerometer signal. For example, “in_accel_x_base” or “in_accel_x_lid”. The possible keys are “in_accel_(x|y|z)_(base|lid)”.Values: an int or a list of [orientation-1, orientation-2, …].Each orientation is 0, 1 or -1 representing the ideal value for gravity under such orientation. For example, 1 or [0, 0, 1, 0, 0, -1].An example of orientation for horizontal calibration: {    “in_accel_x_base”: 0,    “in_accel_y_base”: 0,    “in_accel_z_base”: 1,    “in_accel_x_lid”: 0,    “in_accel_y_lid”: 0,    “in_accel_z_lid”: -1}.Another example of orientation_gravity for six-sided calibration: {    “in_accel_x_base”: [0, 0, 1, -1, 0, 0],    “in_accel_y_base”: [0, 0, 0, 0, 1, -1],    “in_accel_z_base”: [1, -1, 0, 0, 0, 0],    “in_accel_x_lid”: [0, 0, 1, -1, 0, 0],    “in_accel_y_lid”: [0, 0, 0, 0, 1, -1],    “in_accel_z_lid”: [1, -1, 0, 0, 0, 0]}. |
| sample_rate_hz     | int             | (optional; default: `20`) The sample rate in Hz to get raw data from accelerometers.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| capture_count      | int             | (optional; default: `100`) How many times to capture the raw data to calculate the average value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| setup_time_secs    | int             | (optional; default: `2`) How many seconds to wait before starting to calibration.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| spec_offset        | list            | Two numbers, ex: [0.5, 0.5] indicating the tolerance in m/s^2 for the digital output of sensors under 0 and 1G.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| autostart          | bool            | (optional; default: `False`) Starts the test automatically without prompting.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| location           | [‘base’, ‘lid’] | (optional; default: `'base'`) The location for the accelerometer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| variance_threshold | float           | (optional; default: `5.0`) The variance of capture data can not belarger than the threshold.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
