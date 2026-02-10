# generic_battery

Predefined battery tests. It’s called “Battery” in AVL.

## Inherit

- [base.test_list](base.test_list.md)

## BCIC

### pytest_name

[bcic](../pytests/bcic.md)

## Battery

### run_if

```default
constants.has_battery
```

### pytest_name

[battery](../pytests/battery.md)

## BatterySysfs

### run_if

```default
constants.has_battery
```

### pytest_name

[battery_sysfs](../pytests/battery_sysfs.md)

### args

`maximum_cycle_count`
: ```default
  10
  ```

`percent_battery_wear_allowed`
: ```default
  5
  ```

## BlockingCharge

### pytest_name

[blocking_charge](../pytests/blocking_charge.md)

## ProbeBattery

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "battery"
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
      "battery",
      "==",
      1
    ]
  ]
  ```

## BCICGroup

### Serial subtests

- ```default
  {
    "action_on_failure": "PARENT",
    "args": {
      "action": "SET",
      "use_latest_hwid_bundle": true
    },
    "inherit": "BCIC",
    "label": "BCIC Set"
  }
  ```
- ```default
  {
    "inherit": "FullRebootStep",
    "run_if": "device.factory.bcic_update_need_reboot"
  }
  ```
- ```default
  {
    "args": {
      "action": "CHECK",
      "use_latest_hwid_bundle": false
    },
    "inherit": "BCIC",
    "label": "BCIC Check",
    "run_if": "device.factory.bcic_update_need_reboot"
  }
  ```
