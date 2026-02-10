# spatial_sensor_calibration

**Source code:** [spatial_sensor_calibration.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/spatial_sensor_calibration.py)

Perform calibration on spatial sensors

## Description

Spatial sensors are sensors with X, Y, Z values such as accelerometer or
gyroscope.

## Test Procedure

The step for calibration is as follows:
1) Put the device on a flat table, facing up.

1. Issue a command to calibrate them:

> - echo 1 > /sys/bus/iio/devices/iio:deviceX/calibrate
> - X being the ids of the accel and gyro.
1. Retrieve the calibration offsets

> - cat /sys/bus/iio/devices/iio:deviceX/in_(accel|anglvel)_(x|y|z)_calibbias
1. Save them in VPD.

## Dependency

- A spatial sensor whose driver implements [perform_calib](https://source.chromium.org/search?q=perform_calib%20f:platform%2Fec%2Fdriver) of accelgyro_drv in
  [accelgyro.h](https://source.chromium.org/search?q=accelgyro.h).

## Examples

To run this test, add this into test list:

```default
{
  "pytest_name": "spatial_sensor_calibration",
  "label": "Gyroscope Calibration By EC",
  "run_if": "not constants.has_device_data or device.component.has_base_gyroscope",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER",
    "test_tags.TestCategory.VPD"
  ],
  "args": {
    "device_name": "cros-ec-gyro",
    "device_location": "base",
    "raw_entry_template": "in_anglvel_%s_raw",
    "calibbias_entry_template": "in_anglvel_%s_calibbias",
    "vpd_entry_template": "in_anglvel_%s_base_calibbias"
  }
}
```

```default
{
  "pytest_name": "spatial_sensor_calibration",
  "label": "Base Accelerometers Calibration By EC",
  "run_if": "not constants.has_device_data or device.component.has_base_accelerometer",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER",
    "test_tags.TestCategory.VPD"
  ],
  "args": {
    "device_name": "cros-ec-accel",
    "device_location": "base",
    "raw_entry_template": "in_accel_%s_raw",
    "calibbias_entry_template": "in_accel_%s_calibbias",
    "vpd_entry_template": "in_accel_%s_base_calibbias"
  }
}
```

```default
{
  "pytest_name": "spatial_sensor_calibration",
  "label": "Lid Accelerometers Calibration By EC",
  "run_if": "not constants.has_device_data or device.component.has_lid_accelerometer",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER",
    "test_tags.TestCategory.VPD"
  ],
  "args": {
    "device_name": "cros-ec-accel",
    "device_location": "lid",
    "raw_entry_template": "in_accel_%s_raw",
    "calibbias_entry_template": "in_accel_%s_calibbias",
    "vpd_entry_template": "in_accel_%s_lid_calibbias"
  }
}
```

## Test Arguments

| Name                     | Type      | Description                                                                                                                                            |
|--------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| timeout_secs             | int       | (optional; default: `60`) Timeout in seconds when waiting for device.                                                                                  |
| sensor_name              | str, dict | (optional; default: `{'en-US': 'Accelerometer'}`) name of the sensor to calibrate.                                                                     |
| device_name              | str       | The “name” atribute of the sensor                                                                                                                      |
| device_location          | str       | The “location” atribute of the sensor                                                                                                                  |
| raw_entry_template       | str       | (optional; default: `'in_accel_%s_raw'`) Template for the sysfs raw value entry.                                                                       |
| calibbias_entry_template | str       | (optional; default: `'in_accel_%s_calibbias'`) Template for the sysfs calibbias value entry.                                                           |
| vpd_entry_template       | str       | (optional; default: `'in_accel_%s_base_calibbias'`) Template for the sysfs calibbias value entry.                                                      |
| stabilize_time           | int       | (optional; default: `1`) Time to wait until calibbias stabilize.                                                                                       |
| prompt                   | bool      | (optional; default: `True`) Prompt user to put the device in correct facing                                                                            |
| placement_range          | list      | (optional; default: `[None, None, None]`) A list of sequences asserting the range of X, Y, Z. Each element is [min, max] or None if it’s a don’t care. |
