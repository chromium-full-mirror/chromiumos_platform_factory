# brightness.brightness

**Source code:** [brightness/brightness.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/brightness/brightness.py)

This is a factory test to check the brightness of LCD backlight or LEDs.

## Test Arguments

| Name          | Type       | Description                                                      |
|---------------|------------|------------------------------------------------------------------|
| msg           | str, dict  | Message HTML                                                     |
| timeout_secs  | int        | (optional; default: `10`) Timeout value for the test in seconds. |
| levels        | list       | A sequence of brightness levels.                                 |
| interval_secs | int, float | Time for each brightness level in seconds.                       |
