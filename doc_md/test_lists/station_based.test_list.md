# station_based

We assume the DUT is also running Goofy, so FactoryState APIs are used.

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## ConnectDevice

### pytest_name

[station_entry](../pytests/station_entry.md)

### args

`prompt_start`
: ```default
  true
  ```

`load_dut_storage`
: ```default
  "eval! constants.load_dut_storage"
  ```

## DisconnectDevice

### pytest_name

[station_entry](../pytests/station_entry.md)

### args

`start_station_tests`
: ```default
  false
  ```

`disconnect_dut`
: ```default
  true
  ```

## FactoryState

### pytest_name

[factory_state](../pytests/factory_state.md)

## FactoryStateCopyFromDUT

### pytest_name

[factory_state](../pytests/factory_state.md)

### args

`action`
: ```default
  "COPY"
  ```

`device`
: ```default
  "DUT"
  ```

## FactoryStateCopyToDUT

### pytest_name

[factory_state](../pytests/factory_state.md)

### args

`action`
: ```default
  "COPY"
  ```

`device`
: ```default
  "STATION"
  ```

## FactoryStateMergeOnDUT

### pytest_name

[factory_state](../pytests/factory_state.md)

### args

`action`
: ```default
  "MERGE"
  ```

`device`
: ```default
  "DUT"
  ```

## FactoryStatePopOnStation

### pytest_name

[factory_state](../pytests/factory_state.md)

### args

`action`
: ```default
  "POP"
  ```

`device`
: ```default
  "STATION"
  ```

## StationCheckSerialNumber

### run_if

```default
constants.check_serial_number
```

### pytest_name

[check_serial_number](../pytests/check_serial_number.md)

## FactoryStateCleanUp

### Serial subtests

- [FactoryStateCopyToDUT]()
- [FactoryStateMergeOnDUT]()
- [FactoryStatePopOnStation]()

## FactoryStateSetup

### Serial subtests

- [FactoryStateCopyFromDUT]()

## StationLoop

This will be run forever

### Serial subtests

- [StationLoopStart]()
- [StationLoopMain]()
- CheckPoint
- [StationLoopEnd]()

## StationLoopEnd

### Serial subtests

- FlushTestlog
- [FactoryStateCleanUp]()
- [DisconnectDevice]()
- [StationLoopItemsAfterDisconnection]()

## StationLoopItemsAfterDisconnection

These items will be run everytime after the device is disconnected.

### Serial subtests

- ```default
  {
    "inherit": "Placeholder",
    "label": "Placeholder: AfterDisconnection"
  }
  ```

## StationLoopItemsBeforeConnection

These items will be run everytime before the device is connected.

### Serial subtests

- ```default
  {
    "inherit": "Placeholder",
    "label": "Placeholder: BeforeConnection"
  }
  ```

## StationLoopMain

These items will be run everytime after the device is connected.

### Serial subtests

- ```default
  {
    "inherit": "Placeholder",
    "label": "Placeholder: Main"
  }
  ```

## StationLoopStart

### Serial subtests

- SyncFactoryServer
- [StationLoopItemsBeforeConnection]()
- [ConnectDevice]()
- [StationCheckSerialNumber]()
- [FactoryStateSetup]()

## StationSetupItems

One time setup items when station is up.
