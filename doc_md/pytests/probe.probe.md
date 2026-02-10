# probe.probe

**Source code:** [probe/probe.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/probe/probe.py)

A factory test to check if the components can be probed successfully or not.

## Description

Uses probe module to probe the components, and verifies the component count of
each category. The default rule is the count should be equal to 1. If the
required count is not 1, we can set the expected count either in `device_data`
or in the argument overridden_rules in the test list.

If the component counts of some of the categories are not always same around
each SKUs, we can record the SKU’s specific rules in
`py/config/model_sku.json` and let the test `model_sku` be run before
this test.

The format of the config file:

```default
{
  <Component category> : {
    <Component name> : {
      "eval" : <Function expression>,
      "expect" : <Rule expression>
    }
  }
}
```

Please refer to `py/probe/probe_cmdline.py` for more details.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. Run the probe module to probe the components listed in config_file.
2. Mark the test result to passed only if for each component category,
   number of successfully probed components fits the category’s rule.
3. If show_ui is `False`, just end the test.  Otherwise continue below
   steps.
4. If show_ui is `True`, show the result and wait for OP to press the space
   key to continue.  Otherwise show the result only if the test is failed.

When this test is verifying if the number of probed components of each category
fits the requirement, the following conditions will be executed:

1. If overridden_rules specifies a rule to verify the number of the
   probed components of that category, use that rule.
2. If overridden_rules doesn’t specifies a rule for that category and
   `device_data.component.has_<category_name>` exists, take
   `int(device_data.component.has_<category_name>)` as the expected number
   of probed components.
3. If none of above conditions fit the case, the test will expect only one
   component of that category to be probed.

## Dependency

- Probe framework (`cros.factory.probe`).

## Examples

To do probe test on DUT, add a test item in the test list:

```default
{
  "pytest_name": "probe",
  "args": {
    "config_file": "probe.json",
    "overridden_rules": [
      ["camera", "==", 2]
    ]
  }
}
```

And list what components to probe in probe.json (Note that the comments
(`// ...`) below is not allowed in a real config file):

```default
{
  "audio": {
    "foo_audio": {  // Probe by checking if the content of /tmp/foo is "FOO".
      "eval": {"file": "/tmp/foo"},
      "expect": "FOO"
    },
    "bar_audio": {
      "eval": {"file": "/tmp/bar"},
      "expect": "BAR"
    }
  },
  "storage": {
    "foo_storage": {  // Probe by running the command "storage_probe" and
                      // checking if the stdout of the command is "FOO".
      "eval": {"shell": "storage_probe"},
      "expect": "FOO"
    }
  },
  "camera": {
    "camera_0": {
      "eval": "shell:grep -o -w CAM1 /sys/class/video4linux/video0/name",
      "expect": "CAM2"
    },
    "camera_1": {
      "eval": "shell:grep -o -w CAM2 /sys/class/video4linux/video1/name",
      "expect": "CAM2"
    }
  }
}
```

The overridden_rules argument above means that there should be two camera
components. So in the above example, the test would pass only if the probe
module successfully probed camera_0, camera_1, foo_sotrage, and one of
foo_audio or bar_audio.

Following example shows how to use `device_data` to specific the required
number of probed camera.  The test list should contain:

```default
{
  "pytest_name": "model_sku",
  "args": {
    "config_name": "my_model_sku"
  }
},
{
  "pytest": "probe"
  "args": {
    "config_file": "probe.json"
  }
}
```

And `my_model_sku.json` should contain:

```default
{
  "product_sku": {
    "Example": {
      "34": {
        "component.has_camera": False
      },
      "35": {
        "component.has_camera": 2
      }
    }
  }
}
```

In this example, we expect the probe module to find no any camera component on
a product_name Example SKU 34 device. And expect the probe module to find two
camera components on a product_name Example SKU 35 device.

## Test Arguments

| Name             | Type       | Description                                                                                                                                                                                          |
|------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| config_file      | str        | Path to probe config file. This is interpreted as a path relative to test/pytests/probe folder.                                                                                                      |
| component_list   | list, None | (optional; default: `None`) A list of components to be verified                                                                                                                                      |
| overridden_rules | list       | (optional; default: `[]`) List of [category, cmp_function, value].                                                                                                                                   |
| show_ui          | bool, None | (optional; default: `None`) Always show the result and prompt if set to True. Always not show the result and prompt if set to False. Otherwise, only show the result and prompt when the test fails. |
