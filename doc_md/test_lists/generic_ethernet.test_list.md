# generic_ethernet

Predefined Ethernet tests. Ethernet is called “Ethernet controller” in AVL.

## Inherit

- [base.test_list](base.test_list.md)

## Ethernet

### pytest_name

[ethernet](../pytests/ethernet.md)

### args

`auto_start`
: ```default
  true
  ```

`link_only`
: ```default
  true
  ```

`iface`
: ```default
  "eth0"
  ```

## ProbeEthernet

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "ethernet"
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
      "ethernet",
      ">",
      0
    ]
  ]
  ```
