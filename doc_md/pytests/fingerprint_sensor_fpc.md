# fingerprint_sensor_fpc

**Source code:** [fingerprint_sensor_fpc.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/fingerprint_sensor_fpc.py)

A factory test for the FPC fingerprint sensor.

## Description

Tests that the FPC fingerprint sensor is connected properly and has no defect by
executing commands through the fingerprint micro-controller.

### Internal references

- go/cros-fingerprint-factory-requirements#Documents

The testing procedures, such as (inverted) checkerboard and reset pixel, are
defined in the MTS (Module Test Specification) and ITS (In-Device Test
Specification) docs. By default, the pytest uses the acceptance criteria of ITS.

## Test Procedure

1. The sensor must not be pressed until the test shows instruction on the UI.
2. Test performs automated test (e.g. pixel median) without user interaction.
3. If number_of_manual_captures is not 0, then an operator or a fixture must
   pressed a rubber finger or a real finger against the sensor.
4. If rubber_finger_present is true, then an operator or a fixture must pressed
   a rubber finger against the sensor to calculate the SNR.
5. The test fails if any of above three tests is marked as failed.

## Dependency

The pytest supposes that the system as a fingerprint MCU exposed through the
kernel cros_ec driver as `/dev/cros_fp`.

When available, it uses the vendor ‘libfputils’ shared library and its Python
helper to display the captured image and compute the image quality
signal-to-noise ratio.

## Examples

Minimum runnable example to check if the fingerprint sensor is connected
properly and fits the default quality settings:

```default
{
  "pytest_name": "fingerprint_sensor_fpc",
  "label": "FPC Fingerprint Sensor Test",
  "run_if": "device.component.has_fingerprint and (device.component.fingerprint_board == 'bloonchipper' or device.component.fingerprint_board == 'helipilot')",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "fpframe_retry_count": 2
  }
}
```

To check if the sensor has at most 10 dead pixels, with bounds for the pixel
grayscale median values and finger detection zones, add this in test list:

```default
{
  "pytest_name": "fingerprint_sensor_fpc",
  "label": "FPC Fingerprint Sensor Test + Pixel Median Test (Dartmonkey)",
  "run_if": "device.component.has_fingerprint and device.component.fingerprint_board == 'dartmonkey'",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "fpframe_retry_count": 2,
    "max_dead_pixels": 10,
    "pixel_median": {
      "cb_type1": [
        180,
        220
      ],
      "cb_type2": [
        80,
        120
      ],
      "icb_type1": [
        15,
        70
      ],
      "icb_type2": [
        155,
        210
      ]
    },
    "detect_zones": [
      [
        8,
        16,
        15,
        23
      ],
      [
        24,
        16,
        31,
        23
      ],
      [
        40,
        16,
        47,
        23
      ],
      [
        8,
        66,
        15,
        73
      ],
      [
        24,
        66,
        31,
        73
      ],
      [
        40,
        66,
        47,
        73
      ],
      [
        8,
        118,
        15,
        125
      ],
      [
        24,
        118,
        31,
        125
      ],
      [
        40,
        118,
        47,
        125
      ],
      [
        8,
        168,
        15,
        175
      ],
      [
        24,
        168,
        31,
        175
      ],
      [
        40,
        168,
        47,
        175
      ]
    ]
  }
}
```

To show 10 captures on the screen:

```default
{
  "pytest_name": "fingerprint_sensor_fpc",
  "label": "FPC Fingerprint Sensor Test + Manual Test",
  "run_if": "device.component.has_fingerprint and (device.component.fingerprint_board == 'bloonchipper' or device.component.fingerprint_board == 'helipilot')",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "fpframe_retry_count": 2,
    "number_of_manual_captures": 10
  }
}
```

To test SNR value with a rubber stamp. Only work for Dartmonkey, see b/180757318
for more info:

```default
{
  "pytest_name": "fingerprint_sensor_fpc",
  "label": "FPC Fingerprint Sensor Test + Rubber Stamper Test",
  "run_if": "device.component.has_fingerprint and (device.component.fingerprint_board == 'bloonchipper' or device.component.fingerprint_board == 'helipilot')",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "fpframe_retry_count": 2,
    "rubber_finger_present": true
  }
}
```

## Test Arguments

| Name                      | Type   | Description                                                                                                                                                      |
|---------------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| max_dead_pixels           | int    | (optional; default: `10`) The maximum number of dead pixels on the fingerprint sensor.                                                                           |
| max_dead_detect_pixels    | int    | (optional; default: `0`) The maximum number of dead pixels in the detection zone.                                                                                |
| max_pixel_dev             | int    | (optional; default: `35`) The maximum deviation from the median for a pixel of a given type.                                                                     |
| pixel_median              | dict   | (optional; default: `{}`) Keys: “(cb|icb)_(type1|type2)”, Values: a list of [minimum, maximum] Range constraints of the pixel median value of the checkerboards. |
| detect_zones              | list   | (optional; default: `[]`) a list of rectangles [x1, y1, x2, y2] defining the finger detection zones on the sensor.                                               |
| min_snr                   | float  | (optional; default: `0.0`) The minimum signal-to-noise ratio for the image quality.                                                                              |
| rubber_finger_present     | bool   | (optional; default: `False`) A Rubber finger is pressed against the sensor for quality testing.                                                                  |
| max_reset_pixel_dev       | int    | (optional; default: `65`) The maximum deviation from the median per column for a pixel from test reset image.                                                    |
| max_error_reset_pixels    | int    | (optional; default: `5`) The maximum number of error pixels in the test_reset image.                                                                             |
| fpframe_retry_count       | int    | (optional; default: `0`) The maximum number of retry for fpframe.                                                                                                |
| number_of_manual_captures | int    | (optional; default: `0`) The number of manual captures operators take. If it is not zero then the operator must manually judge pass or fail.                     |
| manual_test_timeout_secs  | float  | (optional; default: `5.0`) The timeout of captures in seconds.                                                                                                   |
