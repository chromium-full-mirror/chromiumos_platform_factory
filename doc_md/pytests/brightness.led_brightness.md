# brightness.led_brightness

**Source code:** [brightness/led_brightness.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/brightness/led_brightness.py)

This is a factory test to check the LED brightness.

## Description

This test is to test LED functionality.

## Test Procedure

1. Changes the brightness and color of the specific LED.
2. Operators decide pass or fail.

## Dependency

- Device API `cros.factory.device.led.SetColor`.

## Examples

An example:

```default
{
  "pytest_name": "brightness.led_brightness",
  "args": {
    "msg": "Check if the LED color is correct",
    "interval_secs": 1,
    "led_name": "LEFT",
    "levels": [1, 2]
  }
}
```

## Test Arguments

| Name          | Type       | Description                                                      |
|---------------|------------|------------------------------------------------------------------|
| msg           | str, dict  | Message HTML                                                     |
| timeout_secs  | int        | (optional; default: `10`) Timeout value for the test in seconds. |
| levels        | list       | A sequence of brightness levels.                                 |
| interval_secs | int, float | Time for each brightness level in seconds.                       |
| led_name      | str        | (optional; default: `'battery'`) The name of the LED to test.    |
| color         | str        | (optional; default: `<Color.WHITE: 'WHITE'>`) The color to test. |
