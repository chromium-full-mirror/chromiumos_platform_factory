# fingerprint_sensor_elan

**Source code:** [fingerprint_sensor_elan.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/fingerprint_sensor_elan.py)

A factory test for the Elan fingerprint sensor.

## Description

This pytest is to test the Elan fingerprint sensor.

The Elan fingerprint test consists of four sub-tests: base test, sensor test,
reset test, and WOE test. Only WOE test requires user interactions.

## Test Procedure

The base, sensor and reset tests are automated. Don’t touch the fingerprint
sensor during the test.

The WOE test requires user interaction. Please take the following steps.

1. Start the test, and wait until the screen tells the user to touch the
   fingerprint sensor.
2. Place your finger on the fingerprint sensor and then lift it away.
3. The UI should show that the WOE test is running. If not, the sensor does not
   detect your finger. It may be malfunctioning.
4. The pytest collects required data and analyzes the sensor’s functionality
   automatically.

## Dependency

The pytest supposes that the system as a fingerprint MCU exposed through the
kernel cros_ec driver as `/dev/cros_fp`.

## Examples

Run only base test:

```default
{
  "pytest_name": "fingerprint_sensor_elan",
  "label": "Elan Fingerprint Sensor Base Test",
  "run_if": "device.component.has_fingerprint and device.component.fingerprint_board == 'buccaneer'",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "fpmode_retry_count": 2,
    "test_case": 1
  }
}
```

Run only non-interactive sub-tests:

```default
{
  "pytest_name": "fingerprint_sensor_elan",
  "label": "Elan Fingerprint Sensor Non-interactive Test",
  "run_if": "device.component.has_fingerprint and device.component.fingerprint_board == 'buccaneer'",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "fpmode_retry_count": 2,
    "test_case": 7
  }
}
```

Run all sub-tests:

```default
{
  "pytest_name": "fingerprint_sensor_elan",
  "label": "Elan Fingerprint Sensor Complete Test",
  "run_if": "device.component.has_fingerprint and device.component.fingerprint_board == 'buccaneer'",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "fpmode_retry_count": 2,
    "test_case": 15
  }
}
```

## Test Arguments

| Name                             | Type   | Description                                                                                                                                                                                              |
|----------------------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| test_case                        | int    | (optional; default: `7`) The test case(s) to run in bitmap format. 1 for base test, 2 sensor test, 4 reset test, and 8 WOE test.                                                                         |
| min_base_mean                    | float  | (optional; default: `1800.0`) The allowed minimum mean value of frames in the base image. Required in base test and reset test.                                                                          |
| max_base_mean                    | float  | (optional; default: `4200.0`) The allowed maximum mean value of frames in the base image. Required in base test and reset test.                                                                          |
| min_pixel_diff                   | int    | (optional; default: `700`) The minimum difference of frames between the raw image and the base image. Frames which difference lower than this value is considered a dead pixel. Required in sensor test. |
| max_pixel_diff                   | int    | (optional; default: `2300`) The maximum difference of frames between the raw image and the base image. Frames which difference exceeds this value is considered a dead pixel. Required in sensor test.   |
| max_dead_pixel_count             | int    | (optional; default: `19`) The allowed dead pixel count. Required in sensor test.                                                                                                                         |
| max_consecutive_dead_pixel_count | int    | (optional; default: `4`) The allowed consecutive dead pixel count in a horizontal or vertical line. Required in sensor test.                                                                             |
| contrast_threshold               | int    | (optional; default: `500`) The required difference to judge the vendor image. Required in WOE test.                                                                                                      |
| capture_fpmode_timeout_secs      | float  | (optional; default: `5.0`) The timeout of capturing fpmode, in seconds.                                                                                                                                  |
| fpmode_retry_count               | int    | (optional; default: `2`) The maximum number of retry for fpmode waitevent and fpframe.                                                                                                                   |
| log_fpframe                      | bool   | (optional; default: `False`) Whether to log fpframe for debugging.                                                                                                                                       |
