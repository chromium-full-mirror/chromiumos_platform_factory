# gyroscope

**Source code:** [gyroscope.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/gyroscope.py)

A factory test for gyroscopes.

## Description

There are steps required to run a complete gyroscope test::
: - Motion sensor setup via ectool motionsense odr ${gyro_id} ${freq}
  - (optional) Calibration for tri-axis (x, y, and z) gyroscopes.
  - The main gyroscope test.

This pytest executes the motion sensor setup and main gyro test in sequence.

## Test Procedure

This test supports and enables auto start by default.  In this case:

1. Put the device (base/lid) on a static plane then press space.
2. Wait for completion.

Otherwise operators will be asked to place DUT on a horizontal plane and
press space.

## Dependency

- Device API (`cros.factory.device.gyroscope`).

## Examples

To run a test on base gyroscope:

```default
{
  "pytest_name": "gyroscope",
  "label": "Gyroscope",
  "run_if": "not constants.has_device_data or device.component.has_base_gyroscope",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "rotation_threshold": 1.0,
    "stop_threshold": 0.1
  }
}
```

## Test Arguments

| Name               | Type            | Description                                                                                                                     |
|--------------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------|
| rotation_threshold | float           | The expected value (rad/s) to read when dut start rotating.                                                                     |
| stop_threshold     | float           | The expected value to read when dut stop moving.                                                                                |
| gyro_id            | int, None       | (optional; default: `None`) Gyroscope ID.  Will read a default ID via ectool if not set.                                        |
| freq               | int, None       | (optional; default: `None`) Gyroscope sampling frequency in mHz.  Will apply the minimal frequency from ectool info if not set. |
| timeout_secs       | int             | (optional; default: `30`) Timeout in seconds for gyro to return expected value.                                                 |
| setup_time_secs    | int             | (optional; default: `2`) Seconds to wait before starting the test.                                                              |
| autostart          | bool            | (optional; default: `False`) Auto start this test.                                                                              |
| setup_sensor       | bool            | (optional; default: `True`) Setup gyro sensor via ectool                                                                        |
| location           | [‘base’, ‘lid’] | (optional; default: `'base'`) Gyro is located in “base” or “lid”.                                                               |
| capture_count      | int             | (optional; default: `50`) How many records to read for each time getting data                                                   |
| sample_rate        | int             | (optional; default: `200`) Sample rate in Hz to read data from sensors                                                          |
| is_ish_connected   | bool            | (optional; default: `False`) If the sensor is connected via ISH or not                                                          |
