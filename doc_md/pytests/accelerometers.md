# accelerometers

**Source code:** [accelerometers.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/accelerometers.py)

A factory test for reading accelerometers

## Description

This is a test to check if values read back from accelerometers are within a
certain range.  If we put it on a flat table we can get (x, y, z) = (0, 0, 9.8)
at an ideal case. For upside down we’ll have (x, y, z) = (0, 0, -9.8).

Since accelerometer is very sensitive, the digital output will be different
for each query. For example, (0.325, -0.278, 9.55).
In addition, temperature or the assembly quality may impact the accuracy
of the accelerometer during manufacturing (ex, position is tilt). To mitigate
this kind of errors, we’ll sample several records of raw data and compute
its average value under an ideal environment.

## Test Procedure

1. The test will auto start unless argument autostart is false, otherwise, it
   will wait for operators to press SPACE.
2. Check if values are within the threshold, pass / fail automatically.

## Dependency

- Device API (`cros.factory.device.accelerometer`)

## Examples

If the device is expected to be place horizontally on desk, this test can be
added as simple as:

```default
{
  "pytest_name": "accelerometers",
  "label": "Base Accelerometers Test",
  "run_if": "not constants.has_device_data or device.component.has_base_accelerometer",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "location": "base"
  }
}
```

```default
{
  "pytest_name": "accelerometers",
  "label": "Lid Accelerometers Test",
  "run_if": "not constants.has_device_data or device.component.has_lid_accelerometer",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "location": "lid"
  }
}
```

You can also change the limits of each axis to loose the criteria:

```default
{
  "pytest_name": "accelerometers",
  "label": "Base Accelerometers Test With Looser Limits",
  "run_if": "not constants.has_device_data or device.component.has_base_accelerometer",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "location": "base",
    "limits": {
      "x": [
        -1.0,
        1.0
      ],
      "y": [
        -1.0,
        1.0
      ],
      "z": [
        8.0,
        11.0
      ]
    }
  }
}
```

## Test Arguments

| Name            | Type            | Description                                                                                                                                         |
|-----------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| autostart       | bool            | (optional; default: `True`) If this is false, this test will not start until operators press space                                                  |
| limits          | dict, None      | (optional; default: `None`) A dictionary of expected range for x, y, z values.  For example, {“x”: [-0.5, 0.5], “y”: [-0.5, 0.5], “z”: [8.8, 10.8]} |
| sample_rate_hz  | int             | (optional; default: `20`) The sample rate in Hz to get raw data from accelerometers.                                                                |
| capture_count   | int             | (optional; default: `100`) How many times to capture the raw data to calculate the average value.                                                   |
| setup_time_secs | int             | (optional; default: `2`) How many seconds to wait before starting to calibration.                                                                   |
| location        | [‘base’, ‘lid’] | (optional; default: `'base'`) The location for the accelerometer                                                                                    |
