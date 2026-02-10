# generic_smt

## Inherit

- [generic_audio.test_list](generic_audio.test_list.md)
- [generic_battery.test_list](generic_battery.test_list.md)
- [generic_dram.test_list](generic_dram.test_list.md)
- [generic_ethernet.test_list](generic_ethernet.test_list.md)
- [generic_tpm.test_list](generic_tpm.test_list.md)
- [generic_storage.test_list](generic_storage.test_list.md)
- [generic_wireless.test_list](generic_wireless.test_list.md)
- [generic_common.test_list](generic_common.test_list.md)

## CheckRMATestList

### run_if

```default
constants.factory_process == 'RMA'
```

### pytest_name

[check_test_list](../pytests/check_test_list.md)

### args

`test_list_id`
: ```default
  "eval! constants.smt.rma_test_list"
  ```

## SMTBatterySysfs

### run_if

```default
constants.has_battery
```

### pytest_name

[battery_sysfs](../pytests/battery_sysfs.md)

### args

`maximum_cycle_count`
: ```default
  -1
  ```

`percent_battery_wear_allowed`
: ```default
  -1
  ```

## SMTKeyboard

### pytest_name

[keyboard](../pytests/keyboard.md)

### args

`allow_multi_keys`
: ```default
  true
  ```

`has_numpad`
: ```default
  "eval! device.component.has_numeric_pad or False"
  ```

`layout`
: ```default
  "ANSI"
  ```

## SMTProbe

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`config_file`
: ```default
  "probe.json"
  ```

`component_list`
: ```default
  "eval! constants.smt.component_list"
  ```

## SMTScanMLB

### pytest_name

[scan](../pytests/scan.md)

### args

`device_data_key`
: ```default
  "serials.mlb_serial_number"
  ```

`event_log_key`
: ```default
  "mlb_serial_number"
  ```

`label`
: ```default
  "i18n! MLB Serial Number"
  ```

## SMTScanOperatorID

### pytest_name

[scan](../pytests/scan.md)

### args

`device_data_key`
: ```default
  "factory.smt_operator_id"
  ```

`event_log_key`
: ```default
  "smt_operator_id"
  ```

`label`
: ```default
  "i18n! Operator ID"
  ```

## SMTScanStationID

### pytest_name

[scan](../pytests/scan.md)

### args

`device_data_key`
: ```default
  "factory.smt_station_id"
  ```

`event_log_key`
: ```default
  "smt_station_id"
  ```

`label`
: ```default
  "i18n! Station ID"
  ```

## SMTStressAppTest

### pytest_name

[stressapptest](../pytests/stressapptest.md)

### args

`seconds`
: ```default
  "eval! constants.smt.stress_duration_secs"
  ```

## SMTStressCountdown

### pytest_name

[countdown](../pytests/countdown.md)

### args

`duration_secs`
: ```default
  "eval! constants.smt.stress_duration_secs"
  ```

## SMTThermalLoad

Must not be run together with StressAppTest

### pytest_name

[thermal_load](../pytests/thermal_load.md)

### args

`lower_threshold`
: ```default
  40
  ```

`temperature_limit`
: ```default
  100
  ```

`heat_up_timeout_secs`
: ```default
  12
  ```

`duration_secs`
: ```default
  15
  ```

## SMTWifiSSIDList

This test object cannot be run directly. Users have to inherit and modify it.

### pytest_name

[wifi_throughput](../pytests/wifi_throughput.md)

### args

`event_log_name`
: ```default
  "SMT_basic_ssid_list"
  ```

## SwitchToRMATestList

### run_if

```default
constants.factory_process == 'RMA'
```

### pytest_name

[switch_test_list](../pytests/switch_test_list.md)

### args

`test_list_id`
: ```default
  "eval! constants.smt.rma_test_list"
  ```

## ChromeboxSMTItems

### Serial subtests

- CheckSecdataVersion
- [SMTComponents]()
- [SMTStress]()
- [SMTThermalLoad]()
- AudioJack
- LED
- USBTypeATest
- USBTypeCTest
- HWButton
- Ethernet
- Buzzer

## SMT

The stage of tests performed after SMT and before FA.  This is also known as SA (System Assembly) testing.  After SMT, most factories will do System Assembly (SA) and then System Imaging then perform SA Testing.

### run_if

```default
is_engineering_mode or not device.factory.end_SMT
```

### Serial subtests

- [SMTStart]()
- [SMTItems]()
- CheckPoint
- [SMTEnd]()

## SMTComponents

### Parallel subtests

- [SMTProbe]()
- SpeakerDMic
- [SMTBatterySysfs]()
- [SMTWifiSSIDList]()
- ChargerTypeDetection
- ChargeDischargeCurrent
- PartitionTable
- VerifyRootPartition

## SMTEnd

### Serial subtests

- StationEnd
- FinalizeMLB
- [CheckRMATestList]()
- CheckPoint
- HaltStep
- [SwitchToRMATestList]()

## SMTItems

### Serial subtests

- CheckSecdataVersion
- [SMTComponents]()
- [SMTStress]()
- [SMTThermalLoad]()
- LidSwitch
- AudioJack
- LED
- USBTypeATest
- USBTypeCTest
- [SMTKeyboard]()
- HWButton

## SMTStart

### Serial subtests

- ReadDeviceDataFromVPD
- ReadDeviceDataFromCrosConfig
- SyncFactoryServer
- [SMTScanMLB]()
- [SMTScanOperatorID]()
- [SMTScanStationID]()
- StationStart

## SMTStress

### Parallel subtests

- [SMTStressCountdown]()
- [SMTStressAppTest]()

## SMTUpdateFirmware

### Serial subtests

- SyncFactoryServer
- UpdateFirmware
