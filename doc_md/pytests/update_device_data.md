# update_device_data

**Source code:** [update_device_data.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_device_data.py)

Updates Device Data (manually or from predefined values in test list).

## Description

The Device Data (`cros.factory.test.device_data`) is a special data structure
for manipulating DUT information.  This test can determine Device Data
information (usually for VPD) without using shopfloor backend, usually
including:

- `serials.serial_number`: The device serial number.
- `vpd.ro.region`: Region data (RO region).
- `vpd.rw.ubind_attribute` and `vpd.rw.gbind_attribute`: User and group
  registration codes.
- Or other values specified in argument `fields` or `config_name`.

When argument manual_input is True, every values specified in `fields` will
be displayed on screen with an edit box before written into device data.
Note all the values will be written as string in manual mode.

The `fields` argument is a sequence in format
`(data_key, value, display_name, value_check)`:

| Name           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `data_key`     | The Device Data key name to write.                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `value`        | The value to be written, can be modified if `manual_input` is<br/>True.                                                                                                                                                                                                                                                                                                                                                                                                          |
| `display_name` | The label or name to be displayed on UI.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `value_check`  | To validate the input value. Can be a regular expression,<br/>list of strings, list of integers, boolean values, or<br/>None.<br/>When `value_check` is a list of strings / integers / bool, an<br/>“option label” can be added to each option.  So `value_check`<br/>becomes a list of tuples: `[ (string, string) ]` or `[ (int,<br/>string) ]` or `[ (bool, string) ]`.  The first element of<br/>tuple is the value, and the second element is a string to be<br/>displayed. |

If you want to manually configure without default values, the sequence can be
replaced by a simple string of key name.

The `config_name` refers to a JSON config file loaded by
`cros.factory.py.utils.config_utils` with single dictionary that the keys
and values will be directly sent to Device Data. This is helpful if you need to
define board-specific data.

`config_name` and `fields` are both optional, but you must specify at least
one.

If you want to set device data (especially VPD values) using shopfloor or
pre-defined values:

1. Use `shopfloor_service` test with method=GetDeviceInfo to retrieve
   `vpd.{ro,rw}.*`.
2. Use `update_device_data` test to write pre-defined or update values to
   `vpd.{ro,rw}.*`.
3. Use `write_device_data_to_vpd` to flush data into firmware VPD sections.

## Test Procedure

If argument `manual_input` is not True, this will be an automated test
without user interaction.

If argument `manual_input` is True, the test will go through all the fields:

1. Display the name and key of the value.
2. Display an input edit box for simple values, or a list of selection
   if the `value_check` is a sequence of strings or boolean values.
3. Wait for operator to select or input right value.
4. If operator presses ESC, abandon changes and keep original value.
5. If operator clicks Enter, validate the input by `value_check` argument.
   If failed, prompt and go back to 3.
   Otherwise, write into device data and move to next field.
6. Pass when all fields were processed.

## Dependency

None. This test only deals with the `device_data` module inside factory
software framework.

## Examples

To silently load device-specific data defined in board overlay
`py/config/default_device_data.json`, add this in test list:

```default
{
  "pytest_name": "update_device_data",
  "args": {
    "config_name": "default",
    "manual_input": false
  }
}
```

To silently set a device data ‘component.has_touchscreen’ to True:

```default
{
  "pytest_name": "update_device_data",
  "args": {
    "fields": [
      [
        "component.has_touchscreen",
        true,
        "Device has touch screen",
        null
      ]
    ],
    "manual_input": false
  }
}
```

For RMA process to set serial number, region, registration codes, and specify
if the device has peripherals like touchscreen:

```default
{
  "pytest_name": "update_device_data",
  "args": {
    "fields": [
      [
        "serials.serial_number",
        null,
        "Device Serial Number",
        "[A-Z0-9]+"
      ],
      ["vpd.ro.region", "us", "Region", null],
      ["vpd.rw.ubind_attribute", null, "User ECHO", null],
      ["vpd.rw.gbind_attribute", null, "Group ECHO", null],
      [
        "component.has_touchscreen",
        null,
        "Has touchscreen",
        [true, false]
      ]
    ]
  }
}
```

If you don’t need default values, there’s an alternative to list only key
names:

```default
{
  "pytest_name": "update_device_data",
  "args": {
    "fields": [
      "serials.serial_number",
      "vpd.ro.region",
      "vpd.rw.ubind_attribute",
      "vpd.rw.gbind_attribute"
    ]
  }
}
```

## Test Arguments

| Name         | Type       | Description                                                                                                                                                         |
|--------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| manual_input | bool       | (optional; default: `True`) Set to False to silently updating all values. Otherwise each value will be prompted before set into Device Data.                        |
| config_name  | str, None  | (optional; default: `None`) A JSON config name to load representing the device data to update.                                                                      |
| fields       | list, None | (optional; default: `None`) A list of [data_key, value, display_name, value_check] indicating the Device Data field by data_key must be updated to specified value. |
