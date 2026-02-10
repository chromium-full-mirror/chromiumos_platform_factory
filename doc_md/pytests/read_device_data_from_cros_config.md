# read_device_data_from_cros_config

**Source code:** [read_device_data_from_cros_config.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/read_device_data_from_cros_config.py)

Setup device data from ChromeOS Config.

## Description

This test reads data from ChromeOS Config and sets it up in the device data. If
we want to add more field to add to device data, we can expand the
`fields_to_read` variable in the test class.

## Test Procedure

This test is an automated test that does not require any operator interaction.

## Dependency

The device running this test must have a matching crosid so that `cros_config`
knows which config record to refer to. Run `crosid -v` on DUT for details.
All the fields adding to device data from Cros Config via this test should be
consistent across different SKUs since the SKU might change during factory flow.

## Examples

Currently, there are no arguments that need to be set for this test. To run the
test, simply run:

```default
{
  "pytest_name": "read_device_data_from_cros_config"
}
```

## Test Arguments

This test does not have any arguments.
