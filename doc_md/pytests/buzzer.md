# buzzer

**Source code:** [buzzer.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/buzzer.py)

This is a buzzer test.

## Description

This test checks the functionality of the buzzer of a ChromeOS device.

## Test Procedure

1. Press space and DUT will start buzzing.
2. Press the number of buzz heard to pass the test or press ‘r’ to play again.

## Dependency

None.

## Examples

To test buzzer with default parameters on puff, add this in test list:

```default
{
  "pytest_name": "buzzer"
  "args": {
    "gpio_index": "382"
  }
}
```

If you want to change the mute duration between two beeps and the duration of a
beep and test buzzer on brask:

```default
{
  "pytest_name": "buzzer",
  "args": {
    "gpio_index": "166"
    "beep_duration_secs": 0.8,
    "mute_duration_secs": 1.5
  }
}
```

## Test Arguments

| Name               | Type   | Description                                                |
|--------------------|--------|------------------------------------------------------------|
| beep_duration_secs | float  | (optional; default: `0.3`) How long for one beep           |
| mute_duration_secs | float  | (optional; default: `0.5`) Mute duration between two beeps |
| gpio_index         | str    | Index for gpio file depending on the board                 |
