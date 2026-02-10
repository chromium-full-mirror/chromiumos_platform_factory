# check_serial_number

**Source code:** [check_serial_number.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_serial_number.py)

Checks if serial number is set correctly on a device.

## Description

Some tests, for example, RF graphyte, assume DUTs have MLB serial number
available (in VPD and device data).  And the test will fail if a DUT
doesn’t have MLB SN (e.g. it skipped previous station).

This test gets serial number from different sources and check if they are equal.

## Test Procedure

This is an automated test.  It requires user interaction only if the test
failed, or if the “manual_check” flag is turned on.  This test will,

1. try to connect to device’s state server
2. the device must have device_id
3. get SN from state server
4. get SN from VPD
5. these two SN must match

## Dependency

1. SSH connection (if we are checking remote device)
2. DUT is running factory software

## Examples

This test is already defined as “CheckSerialNumber”
in generic_common.test_list.json and “StationCheckSerialNumber” in
station_based.test_list.json. This test is turned on by default in station
based test list. You can disable it by setting constants.check_serial_number
to false:

```default
{
  "constants": {
    "check_serial_number": false
  }
}
```

By default, this pytest checks mlb_serial_number. If you want to check serial
number instead:

```default
{
  "pytest_name": "check_serial_number",
  "args": {
    "sn_name": "serial_number"
  }
}
```

By default, this pytest passes if the serial numbers match. If you want
additional manual confirmation (e.g. also match the serial number printed on
the device):

```default
{
  "pytest_name": "check_serial_number",
  "args": {
    "manual_check": true
  }
}
```

## Test Arguments

| Name         | Type   | Description                                                                                                                |
|--------------|--------|----------------------------------------------------------------------------------------------------------------------------|
| sn_name      | str    | (optional; default: `'mlb_serial_number'`) name of the serial number, e.g. “serial_number” or “mlb_serial_number”          |
| manual_check | bool   | (optional; default: `False`) If set to true, this test needs operator to press ENTER or ESC to pass or fail the test case. |
