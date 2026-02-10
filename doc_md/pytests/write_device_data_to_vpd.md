# write_device_data_to_vpd

**Source code:** [write_device_data_to_vpd.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/write_device_data_to_vpd.py)

Writes device data to VPD (Vital Product Data).

## Description

Device Data (`cros.factory.test.device_data`) maintains the data during
manufacturing flow, and will be wiped when device goes to shipping mode (or
re-flashed for re-run of manufacturing flow).

To keep device data persistent, we may copy the values to VPD area, which is
inside the SPI flashrom where firmware lives on Chromebooks (other platforms
may implement VPD in other locations, for example Android may prefer to use
/persist partition).

By default, this test writes all device data under `vpd` category (for
example, `vpd.ro.region` to `ro.region`), all device data under `serial`
category (for example, `serials.serial_number` to `serial_number`) and all
device data under `factory` category (for example, `factory.end_SMT` to
`factory.end_SMT`).
To write different values, specify the mapping in `ro_key_map` or
`rw_key_map`.

The `ro_key_map` is a mapping from RO VPD keys to device data keys. For
example:

```default
{'foo': 'bar.baz'}
```

This map indicates we have to read `bar.baz` from device data and write to
RO VPD by name `foo`.

`rw_key_map` works in similar way, except it’s writing values to RW VPD.

## Test Procedure

This is an automated test without user interaction.

Start the test and the specified device data values (or all under `vpd.*`)
will be written to VPD using Device API.

## Dependency

This test relies on `vpd` component in Device API to access VPD.

## Examples

To write all VPD values from device data to VPD, add this in test list:

```default
{
  "pytest_name": "write_device_data_to_vpd"
}
```

To write a calibration data value to RO VPD:

```default
{
  "pytest_name": "write_device_data_to_vpd",
  "args": {
    "ro_key_map": {
      "modem_calibration": "component.cellular.calibration_data"
    }
  }
}
```

## Test Arguments

| Name       | Type       | Description                                                                              |
|------------|------------|------------------------------------------------------------------------------------------|
| ro_key_map | dict, None | (optional; default: `None`) Mapping of (VPD_NAME, DEVICE_DATA_KEY) to write into RO VPD. |
| rw_key_map | dict, None | (optional; default: `None`) Mapping of (VPD_NAME, DEVICE_DATA_KEY) to write into RW VPD. |
