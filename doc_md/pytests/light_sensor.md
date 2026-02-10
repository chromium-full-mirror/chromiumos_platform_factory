# light_sensor

**Source code:** [light_sensor.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/light_sensor.py)

A factory test for ambient light sensor.

## Description

Tests that ambient light sensor reacts to both darkening by covering with
finger as well as brightening by shining with flashlight.

## Test Procedure

When the test starts, all subtests will be listed on the screen.  Operator
needs to press `SPACE` to start subtests.

After `SPACE` is pressed, the first subtest will become `ACTIVE` and
operator should follow the instruction shown on the screen, e.g. “Cover light
sensor with finger”.  The pytest will keep polling light sensor value, as soon
as the  value meets the requirement, the subtest will be marked as `PASSED`
and next subtest will become `ACTIVE`  When all subtests are `PASSED` the
test will pass and stop.

## Dependency

- Device API (`cros.factory.device.ambient_light_sensor`).

## Examples

To perform 3 subtests,

1. `'Light sensor dark'` (below 30)
2. `'Light sensor exact'` (between 60 and 300)
3. `'Light sensor light'` (above 500)

```default
{
  "pytest_name": "light_sensor",
  "label": "Light Sensor",
  "related_components": [
    "test_tags.TestCategory.AMBIENTLIGHTSENSOR"
  ],
  "args": {
    "device_name": "eval! constants.light_sensor_name",
    "subtest_cfg": {
      "Light sensor dark": {
        "below": 30
      },
      "Light sensor exact": {
        "between": [
          60,
          300
        ]
      },
      "Light sensor light": {
        "above": 500
      }
    },
    "subtest_instruction": {
      "Light sensor dark": "i18n! Cover light sensor with finger",
      "Light sensor exact": "i18n! Remove finger from light sensor",
      "Light sensor light": "i18n! Shine light sensor with flashlight"
    },
    "subtest_list": [
      "Light sensor dark",
      "Light sensor exact",
      "Light sensor light"
    ],
    "timeout_per_subtest": 20
  }
}
```

The sensor value represents in lux. For reference, see
[https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-bus-iio](https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-bus-iio).

Note that you have to specify `subtest_list`, `subtests_instruction`,
`subtest_cfg` at the same time.

## Test Arguments

| Name                | Type       | Description                                                                      |
|---------------------|------------|----------------------------------------------------------------------------------|
| device_path         | str, None  | (optional; default: `None`) [Deprecated] device path                             |
| device_name         | str, None  | (optional; default: `'cros-ec-light'`) device name. If unset, do auto detection. |
| location            | str, None  | (optional; default: `None`) device location. If unset, do auto detection.        |
| device_input        | str, None  | (optional; default: `None`) [Deprecated] device input file                       |
| timeout_per_subtest | int        | (optional; default: `10`) timeout for each subtest                               |
| subtest_list        | list, None | (optional; default: `None`) subtest list                                         |
| subtest_cfg         | dict, None | (optional; default: `None`) subtest configuration                                |
| subtest_instruction | dict, None | (optional; default: `None`) subtest instruction                                  |
| check_per_subtest   | int        | (optional; default: `3`) check times for each subtest                            |
