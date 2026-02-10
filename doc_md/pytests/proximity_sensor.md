# proximity_sensor

**Source code:** [proximity_sensor.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/proximity_sensor.py)

A test to check if the proximity sensor triggers events properly.

## Description

It captures the proximity events from the given sensor device
(usually `/dev/proximity-*`) and verifies if the `close/far` events are
triggered properly.

A typical use case of proximity sensor is controlling SAR.

Note that:

1. This test doesn’t support station-based remote test yet.
2. This test stops `powerd` service when it is capturing the events.

## Test Procedure

This test requires the operator to provide some actions.

1. The test shows instruction to ask the operator to remove the cover.
2. Wait until the sensor value is small enough.
3. The test shows instruction to ask the operator to cover the sensor.
4. The test starts to wait for proximity events.
5. If the first captured event is not a `close` event, the test ends with
   failure.
6. The test shows instruction to ask the operator to remove the cover.
7. The test starts to wait for proximity events.
8. If the first captured event is not a `far` event, the test ends with
   failure.
9. If timeout reaches before all the tasks done, the test also ends with
   failure.

## Dependency

## Examples

Let’s assume we want to test the sensor device `/dev/iio:device7`, which
`echo /sys/bus/iio/devices/iio:device7/name` outputs sx9310, just add a test
item in the test list:

```default
{
  "pytest_name": "proximity_sensor",
  "disable_services": [
    "powerd"
  ],
  "args": {
    "device_name": "sx9310"
  }
}
```

To provide the operator detail instructions, we can specify the messages to
show in the test list:

```default
{
  "pytest_name": "proximity_sensor",
  "disable_services": [
    "powerd"
  ],
  "args": {
    "device_name": "sx9310",
    "close_instruction": "i18n! Please cover the left edge by hand",
    "far_instruction": "i18n! Please remove the cover"
  }
}
```

To test the multiple sensor devices with the same device_name, add a test items
in the test list:

```default
{
  "pytest_name": "proximity_sensor",
  "disable_services": [
    "powerd"
  ],
  "args": {
    "device_name": "sx9324",
    "device_count": 2
  }
}
```

## Test Arguments

| Name                     | Type       | Description                                                                                                                                                            |
|--------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| device_name              | str, None  | (optional; default: `None`) If present, the device name specifying which sensor to test. Autodetect the device if not present                                          |
| device_count             | int        | (optional; default: `1`) How many devices with device_name to test                                                                                                     |
| calibrate_path           | str        | (optional; default: `'events/in_proximity0_thresh_either_en'`) The path to enable testing.  Must be relative to the iio device path.                                   |
| enable_sensor_sleep_secs | int, float | (optional; default: `1`) The seconds of sleep after enabling sensor.                                                                                                   |
| sensor_value_path        | str        | (optional; default: `'in_proximity0_raw'`) The path of the sensor value to show on the UI.  Must be relative to the iio device path.  If it is None then show nothing. |
| sensor_initial_max       | int        | (optional; default: `50`) The test will start after the sensor value lower than this value.  If it is None then do not wait.                                           |
| close_instruction        | str, dict  | (optional; default: `{'en-US': 'Please cover the sensor by hand'}`) Message for the action to trigger the `close` event.                                               |
| far_instruction          | str, dict  | (optional; default: `{'en-US': 'Please un-cover the sensor'}`) Message for the action to trigger the `far` event.                                                      |
| timeout                  | int        | (optional; default: `15`) Timeout of the test.                                                                                                                         |
