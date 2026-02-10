# station_setup

**Source code:** [station_setup.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/station_setup.py)

Setup a station for station-based test.

## Description

This factory test checks whether properties for a station (Station name, Line
number, Station number) is set, and ask the operator to set the properties if
it’s not.

The test relies on the station_setup Goofy plugin to work. See the docstring of
the station_setup Goofy plugin on the configurable options for the test.

## Test Procedure

If all required properties is already filled, and no duplicate station is found
on Overlord, the test passes without any user interaction.

Otherwise, the operator is prompted with a form to fill in the required
properties. After the input, checks would be performed again, and operator
would be prompted again if check fails.

## Dependency

The pytest needs to be run in Goofy, and needs the station_setup Goofy plugin
to be enabled.

See [README for Goofy plugin](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/goofy/plugins/README.md#Use-a-Plugin)
on how to enable a plugin.

This test depends on the plugin named `"station_setup.station_setup"`.

## Examples

To ask the operator to fill the properties of the station when needed, add this
in test list:

```default
{
  "pytest_name": "station_setup"
}
```

## Test Arguments

This test does not have any arguments.
