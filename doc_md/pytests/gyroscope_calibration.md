# gyroscope_calibration

**Source code:** [gyroscope_calibration.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/gyroscope_calibration.py)

A factory test for gyroscopes calibration.

## Description

This is a calibration test for tri-axis (x, y, and z) gyroscopes.

## Test Procedure

1. Put the device (base/lid) on a static plane then press space.
2. Wait for completion.

## Dependency

- Device API (`cros.factory.device.gyroscope`).

## Examples

To run calibration on base gyroscope:

```default
{
  "pytest_name": "gyroscope_calibration",
  "args": {
    "location": "base"
  }
}
```

## Test Arguments

| Name            | Type            | Description                                                                                                                     |
|-----------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------|
| capture_count   | int             | (optional; default: `100`) Number of records to read to compute the average.                                                    |
| gyro_id         | int, None       | (optional; default: `None`) Gyroscope ID.  Will read a default ID via ectool if not set.                                        |
| freq            | int, None       | (optional; default: `None`) Gyroscope sampling frequency in mHz.  Will apply the minimal frequency from ectool info if not set. |
| sample_rate     | int             | (optional; default: `20`) Sample rate in Hz to read data from the gyroscope sensor.                                             |
| setup_time_secs | int             | (optional; default: `2`) Seconds to wait before starting the test.                                                              |
| autostart       | bool            | (optional; default: `True`) Auto start this test.                                                                               |
| setup_sensor    | bool            | (optional; default: `True`) Setup gyro sensor via ectool                                                                        |
| location        | [‘base’, ‘lid’] | (optional; default: `'base'`) Gyro is located in “base” or “lid”.                                                               |
| is_ish_enabled  | bool            | (optional; default: `False`) Whether the sensor data is sourced via ISH                                                         |
