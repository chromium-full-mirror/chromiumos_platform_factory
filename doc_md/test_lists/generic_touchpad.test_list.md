# generic_touchpad

Predefined touchpad tests. Touchpad is called “Touchpad Controller” in AVL.

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## ProbeTouchpad

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "touchpad"
  ]
  ```

`config_file`
: ```default
  "/usr/local/factory/py/hwid/v3/default_probe_statement.json"
  ```

`overridden_rules`
: ```default
  [
    [
      "touchpad",
      "==",
      1
    ]
  ]
  ```

## Touchpad

### pytest_name

[touchpad](../pytests/touchpad.md)
