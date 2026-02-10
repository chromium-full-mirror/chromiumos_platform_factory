# read_device_data_from_vpd

**Source code:** [read_device_data_from_vpd.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/read_device_data_from_vpd.py)

Setup device data from VPD (Vital Product Data).

## Description

Device Data (`cros.factory.test.device_data`) maintains the data during
manufacturing flow, and will be wiped when device goes to shipping mode (or
re-flashed for re-run of manufacturing flow).

To rebuild device data, we may want to schedule few `write_device_data_to_vpd`
invocations in manufacturing flow, and one `read_device_data_from_vpd` in
beginning of test list to get the data back when a device has been wiped for
re-run.

This test reads VPD values from specified argument `ro_key_map` and
`rw_key_map`, which are mappings from VPD names to device data keys. For
example:

```default
{'foo': 'bar.baz'}
```

This map indicates we have to read `foo` from VPD and write to device data
using key `bar.baz`. If VPD name ends with “\*”, then all keys with the prefix
will be added to device data. For example:

```default
{'foo.*': 'bar'}
```

This map indicates we will read all VPD values starting with `foo.` and store
in VPD as `bar.*`. In other words, VPD entry `foo.region` will become
`bar.region` in device data.

`rw_key_map` works in similar way, except it’s reading values from RW VPD.

If the specified VPD keys don’t exist, the test will still pass without
warnings.

The default is to read only `{'factory.*': 'factory'}` in `rw_key_map`,
device serial number (serial_number) and mainboard serial number
(mlb_serial_number).

## Test Procedure

This is an automated test without user interaction.

Start the test and the specified device data values will be fetched from VPD
and then written to device data.

## Dependency

This test relies on `vpd` component in Device API to access VPD.

## Examples

To read standard manufacturing information from VPD, add this in test list:

```default
{
  "pytest_name": "read_device_data_from_vpd"
}
```

To write and read back component data into VPD, add this in test list:

```default
{
  "pytest_name": "write_device_data_to_vpd",
  "args": {
    "rw_key_map": {
      "component.*": "component"
    }
  }
}

... (reboot) ...

{
  "pytest_name": "read_device_data_from_vpd",
  "args": {
    "rw_key_map": {
      "component.*": "component"
    }
  }
}
```

## Test Arguments

| Name       | Type       | Description                                                                             |
|------------|------------|-----------------------------------------------------------------------------------------|
| ro_key_map | dict, None | (optional; default: `None`) Mapping of (VPD_NAME, DEVICE_DATA_KEY) to read from RO VPD. |
| rw_key_map | dict, None | (optional; default: `None`) Mapping of (VPD_NAME, DEVICE_DATA_KEY) to read from RW VPD. |
