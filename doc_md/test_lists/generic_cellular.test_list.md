# generic_cellular

Predefined cellular tests. wireless is called “WWAN” in AVL.

## Inherit

- [base.test_list](base.test_list.md)

## ModemSecurity

### pytest_name

[modem_security](../pytests/modem_security.md)

## ProbeCellular

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "cellular"
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
      "cellular",
      "==",
      1
    ]
  ]
  ```

## ProbeImei

### pytest_name

[probe_cellular_info](../pytests/probe_cellular_info.md)

### args

`probe_imei`
: ```default
  true
  ```

`probe_meid`
: ```default
  false
  ```

`probe_lte_imei`
: ```default
  false
  ```

`probe_lte_iccid`
: ```default
  false
  ```

`fields`
: ```default
  {
    "imei": "EquipmentIdentifier"
  }
  ```

## ProbeSim

### pytest_name

[probe_sim](../pytests/probe_sim.md)

### args

`enable_modem_reset`
: ```default
  false
  ```
