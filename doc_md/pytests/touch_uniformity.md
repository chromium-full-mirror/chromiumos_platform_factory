# touch_uniformity

**Source code:** [touch_uniformity.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/touch_uniformity.py)

A factory test for checking touch uniformity.

## Description

This test is intended to be run during run-in without a fixture or operator.
The test recalibrates the touch device then reads raw reference (baseline) data.
Each value must fall within a specified max and min range. Delta values (the
baseline - current reading) are also checked.

The args thresholds in need to be experimentally determined by checking
a set of machines. The test logs the actual max and min values found.

Currently, the test only supports Atmel based touch devices.

## Test Procedure

The test runs automatically. The touch device shouldn’t be touched when
calibrating.

## Dependency

- Device API cros.factory.device.touch.

## Examples

Sample test_list entry:

```default
{
  "pytest_name": "touch_uniformity",
  "label": "Touchscreen Uniformity",
  "run_if": "not constants.has_device_data or device.component.has_touchscreen",
  "related_components": [
    "test_tags.TestCategory.TRACKPAD"
  ],
  "args": {
    "check_list": [
      [
        0,
        "i18n! References",
        23400,
        25100,
        0,
        0
      ],
      [
        1,
        "i18n! Deltas",
        -30,
        40,
        0,
        0
      ]
    ]
  }
}
```

## Test Arguments

| Name          | Type   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|---------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| device_index  | int    | (optional; default: `0`) Index of touch device to test.                                                                                                                                                                                                                                                                                                                                                                                                    |
| check_list    | list   | A list of sequence. Each sequence consists of six elements: frame_idx, label, min_val, max_val, rows, cols.<br/>frame_idx: Index of frame to check.<br/>label: A i18n translation dictionary of frame label.<br/>min_val: Lower bound for values in this frame.<br/>max_val: Upper bound for values in this frame.<br/>rows: Number of rows from top to check, or zero to check all.<br/>cols: Number of columns from left to check, or zero to check all. |
| keep_raw_logs | bool   | (optional; default: `True`) Whether to attach the log by Testlog                                                                                                                                                                                                                                                                                                                                                                                           |
