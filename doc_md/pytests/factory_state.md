# factory_state

**Source code:** [factory_state.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/factory_state.py)

A pytest helps you control FactoryStateLayer

## Description

This pytest helps you control FactoryStateLayer\`s.  The factory state server
(an instance of \`cros.factory.test.state.FactoryState) could have multiple
layers.  The first layer (layer 0) is the default layer which uses python shelve
module and will be saved under /var/factory/state/ by default.  You can create
levels on top of layer 0, but all additional layers only exists in memory, the
data will be destroyed when the layer is removed.  Unless the layer is merged to
first layer.  For example:

```default
Layer 1  # only exists in memory
Layer 0  # saved in /var/factory/state/
```

If you try to read value from data shelf (e.g.
state_proxy.data_shelf.Get(‘foo.bar’)), layer 1 will be checked first, and
then is layer 0.  For writing data (state_proxy.data_shelf.Set(‘foo.bar’, 5)),
layer 1 will be modified, and layer 0 will not, no matter ‘foo.bar’ exists in
layer 0 or not.

This mechanism is designed for station based testing, so you can temporary copy
DUT state to test station, and remove it after the test is done.  Currently this
test only supports DUT using SSHLink, see examples for how it could be used.

## Test Procedure

This pytest does not require operator interaction.

## Dependency

Depends on SSH to interact with remote DUT.

## Examples

Here is an example of station based test list:

```default
{
  "options": {
    "dut_options": {
      "link_class": "SSHLink",
      "host": "1.2.3.4"
    }
  },
  "tests": [
    {
      "inherit": "TestGroup",
      "label": "i18n! Main Loop",
      "iterations": -1,
      "retries": -1,
      "subtests": [
        {
          "pytest_name": "station_entry"
        },
        {
          "pytest_name": "factory_state",
          "args": {
            "action": "COPY",
            "device": "DUT"
          }
        },
        # Do the test ...
        {
          "pytest_name": "summary"
        },
        {
          "pytest_name": "factory_stateer",
          "args": {
            "action": "COPY",
            "device": "STATION"
          }
        },
        {
          "pytest_name": "factory_state",
          "args": {
            "action": "MERGE",
            "device": "DUT"
          }
        },
        {
          "pytest_name": "factory_state",
          "args": {
            "action": "POP",
            "device": "STATION"
          }
        },
        {
          "pytest_name": "station_entry",
          "args": {
            "start_station_tests": false
          }
        }
      ]
    }
  ]
}
```

## Test Arguments

| Name                      | Type                               | Description                                                                                                                                                                                                                         |
|---------------------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| action                    | [‘APPEND’, ‘COPY’, ‘MERGE’, ‘POP’] | What kind of action to do?                                                                                                                                                                                                          |
| dut_options               | dict                               | (optional; default: `{}`) DUT options to create remote dut instnace.                                                                                                                                                                |
| device                    | [‘DUT’, ‘STATION’]                 | (optional; default: `<EnumRole.STATION: 'STATION'>`) Device to do the action.  If the action is COPY, it requires two devices (copy from source to destination), the device will be source, and destination will be the other role. |
| exclude_current_test_list | bool                               | (optional; default: `True`) For COPY command, don’t copy test states of current test list.                                                                                                                                          |
| include_tests             | bool                               | (optional; default: `False`) For COPY command, include tests_shelf.                                                                                                                                                                 |
