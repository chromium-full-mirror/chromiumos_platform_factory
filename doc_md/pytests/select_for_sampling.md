# select_for_sampling

**Source code:** [select_for_sampling.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/select_for_sampling.py)

Decide if this device is selected for certain sampling tests.

## Description

For some sampling tests, the tests should only be run for a subset of
DUTs by a given sampling rate. This test uses a hash of the WLAN MAC
address (wlan0 or mlan0) to decide if we should sample this device or
not, and writes a “True” or “False” to the device data with the
(optionally) specified key.

## Test Procedure

This is an automated test without user interaction.

## Dependency

Need the device to have a WiFi interface with non-fixed MAC address.

## Examples

To select about 10% of the devices and mark devices selected as
‘selected_for_sampling’ in device data, add this in test list:

```default
{
  "pytest_name": "select_for_sampling",
  "args": {
    "rate": 0.1
  }
}
```

To select about 20% of the devices, and mark using ‘run_audio’ key:

```default
{
  "pytest_name": "select_for_sampling",
  "args": {
    "rate": 0.2,
    "device_data_key": "run_audio"
  }
}
```

## Test Arguments

| Name            | Type   | Description                                                                                        |
|-----------------|--------|----------------------------------------------------------------------------------------------------|
| rate            | float  | Sampling rate (0 to never select any devices, 1 to select all, 0.2 to select 20% of devices, etc.) |
| device_data_key | str    | (optional; default: `'selected_for_sampling'`) Key in the device data dictionary                   |
