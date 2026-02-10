# brightness.lcd_backlight

**Source code:** [brightness/lcd_backlight.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/brightness/lcd_backlight.py)

This is a factory test to check the functionality of LCD backlight module.

## Description

This is another version of [backlight](backlight.md).

The goal is to share code between led, lcd_backlight, keyboard_backlight, and so
on. However, users still use the backlight test.

## Test Procedure

1. Enumerate levels and set brightness to each level.
2. Operators decide pass or fail.

## Dependency

- Device API `cros.factory.device.display.SetBacklightBrightness`.

## Examples

An example:

```default
{
  "pytest_name": "brightness.lcd_backlight",
  "label": "Brightness LCD Backlight",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "levels": [
      0.2,
      0.4,
      0.6,
      0.8,
      1.0
    ]
  }
}
```

## Test Arguments

| Name          | Type       | Description                                                                                                            |
|---------------|------------|------------------------------------------------------------------------------------------------------------------------|
| msg           | str, dict  | (optional; default: `{'en-US': 'Please check if backlight brightness is changing from dark to bright.'}`) Message HTML |
| timeout_secs  | int        | (optional; default: `10`) Timeout value for the test in seconds.                                                       |
| levels        | list, None | (optional; default: `None`) A sequence of brightness levels.                                                           |
| interval_secs | int, float | (optional; default: `0.5`) Time for each brightness level in seconds.                                                  |
