# generic_rf_station

This is an example of RF station test list.

## Inherit

- [station_based.test_list](station_based.test_list.md)

## RFGraphyte

### pytest_name

[rf_graphyte.rf_graphyte](../pytests/rf_graphyte.rf_graphyte.md)

### args

`verbose`
: ```default
  true
  ```

`patch_dhcp_ssh_dut_ip`
: ```default
  true
  ```

`graphyte_config_file`
: ```default
  "eval! 'rf_%s_config.json' % locals.type"
  ```

## RFGraphyteConductive

### pytest_name

[rf_graphyte.rf_graphyte](../pytests/rf_graphyte.rf_graphyte.md)

### args

`verbose`
: ```default
  true
  ```

`patch_dhcp_ssh_dut_ip`
: ```default
  true
  ```

`graphyte_config_file`
: ```default
  "eval! 'rf_%s_config.json' % locals.type"
  ```

## StationLoopMain

These items will be run everytime after the device is connected.

### Serial subtests

- [RFGraphyteConductive]()
