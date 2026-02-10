# generic_fingerprint

## Inherit

- [base.test_list](base.test_list.md)

## CheckFPFirmware

### run_if

```default
device.component.has_fingerprint
```

### pytest_name

[update_fpmcu_firmware](../pytests/update_fpmcu_firmware.md)

### args

`method`
: ```default
  "CHECK_VERSION"
  ```

## ElanFPSNonInteractiveTest

### run_if

```default
device.component.has_fingerprint and device.component.fingerprint_board == 'buccaneer'
```

### pytest_name

[fingerprint_sensor_elan](../pytests/fingerprint_sensor_elan.md)

### args

`fpmode_retry_count`
: ```default
  2
  ```

`test_case`
: ```default
  7
  ```

## ElanFPSTest

### run_if

```default
device.component.has_fingerprint and device.component.fingerprint_board == 'buccaneer'
```

### pytest_name

[fingerprint_sensor_elan](../pytests/fingerprint_sensor_elan.md)

### args

`fpmode_retry_count`
: ```default
  2
  ```

## FPCFPSTest

### run_if

```default
device.component.has_fingerprint and (device.component.fingerprint_board == 'bloonchipper' or device.component.fingerprint_board == 'helipilot')
```

### pytest_name

[fingerprint_sensor_fpc](../pytests/fingerprint_sensor_fpc.md)

### args

`fpframe_retry_count`
: ```default
  2
  ```

## UpdateFPFirmware

### run_if

```default
device.component.has_fingerprint
```

### pytest_name

[update_fpmcu_firmware](../pytests/update_fpmcu_firmware.md)

## FPSGroup

### run_if

```default
device.component.has_fingerprint
```

### Serial subtests

- [UpdateFPFirmware]()
- RebootStep
- [CheckFPFirmware]()
- [ElanFPSTest]()
- [FPCFPSTest]()
