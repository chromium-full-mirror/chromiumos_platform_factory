# backlight

**Source code:** [backlight.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/backlight.py)

Test display backlight.

## Description

This test check if the backlight of display can be adjusted.

The test randomly change the backlight of display to either lower or higher,
and operator should answer the direction of change correctly to pass the test.

## Test Procedure

1. The backlight is reset to `reset_level`.
2. Operator press space key to adjust the backlight to lower or higher randomly,
   and press escape key to reset the backlight.
3. Operator press ‘H’ key if the backlight is higher when pressing space key,
   and press ‘L’ key if it is lower.
4. The test pass if the operator answer correctly two times, and fail if the
   operator answer incorrectly.

## Dependency

Device API display.SetBacklightBrightness.

## Examples

To test display backlight functionality, add this into test list:

```default
{
  "pytest_name": "backlight",
  "label": "Backlight",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ]
}
```

To test display backlight functionality, and have a smaller change on each
space pressed, add this into test list:

```default
{
  "pytest_name": "backlight",
  "label": "Backlight (Smaller Adjust Level)",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "adjust_level": 0.02
  }
}
```

## Test Arguments

| Name         | Type   | Description                                                                            |
|--------------|--------|----------------------------------------------------------------------------------------|
| adjust_level | float  | (optional; default: `0.05`) How much the brightness level should be adjusted. Max: 1.0 |
| reset_level  | float  | (optional; default: `0.5`) The brightness level when do reset. Max: 1.0                |
| min_level    | float  | (optional; default: `0.0`) The minimal brightness level during the test. Max: 1.0      |
