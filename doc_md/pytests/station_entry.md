# station_entry

**Source code:** [station_entry.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/station_entry.py)

Starts or ends a station-based test.

## Description

This pytest initializes (or terminates) the DUT connection in a
station-based test, and validates (or invalidates) related device
info. This pytest is mainly used as the first and last pytest to
wrap around a sequence of station-based tests.

In more detail, if the argument start_station_tests is set to True,
this pytest performs following initialization steps:
1. Clear DUT info.
2. Clear serial numbers from device data.
3. Wait for DUT being connected.

On the other hand, if the argument start_station_tests is set to
False, this pytest performs following cleanup steps:
1. Wait for DUT being disconnected.
2. Clear DUT info.
3. Clear serial numbers from device data.

## Test Procedure

If argument start_station_tests is set to True, it waits until the
DUT is connected.

Otherwise, if argument start_station_tests is set to False, it waits
until the DUT is disconnected.

## Dependency

Depend on Device API (`cros.factory.device.device_utils`) to create
a DUT interface, and monitor if DUT is connected.

## Examples

To start a sequence of station-based tests, this pytest can be used as
the first pytest, add this in test list:

```default
{
  "pytest_name": "station_entry"
}
```

If the following pytests should be started until spacebar is hit:

```default
{
  "pytest_name": "station_entry",
  "args": {
    "prompt_start": true
  }
}
```

To gracefully terminate a sequence of station-based tests:

```default
{
  "pytest_name": "station_entry",
  "args": {
    "start_station_tests": false
  }
}
```

Please refer to station_based.test_list.json and STATION_BASED.md about how to
do station based testing.

## Test Arguments

| Name                 | Type      | Description                                                                                  |
|----------------------|-----------|----------------------------------------------------------------------------------------------|
| start_station_tests  | bool      | (optional; default: `True`) To start or stop the factory station tests.                      |
| prompt_start         | bool      | (optional; default: `False`) Prompt for spacebar before starting test.                       |
| timeout_secs         | int, None | (optional; default: `None`) Timeout for waiting the device. Set to None for waiting forever. |
| disconnect_dut       | bool      | (optional; default: `True`) Ask operator to disconnect DUT or not                            |
| load_dut_storage     | bool      | (optional; default: `True`) To load DUT storage into station session (DeviceData).           |
| invalidate_dut_info  | bool      | (optional; default: `True`) To invoke dut.info.Invalidate() or not                           |
| clear_serial_numbers | bool      | (optional; default: `True`) To invoke device_data.ClearAllSerialNumbers() or not             |
| wait_goofy           | bool      | (optional; default: `True`) wait until we can connect to goofy                               |
