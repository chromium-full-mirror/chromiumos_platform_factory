# generic_fingerprint_examples

## Inherit

- [generic_fingerprint.test_list](generic_fingerprint.test_list.md)

## ElanFPSBaseTest

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
  1
  ```

## ElanFPSCompleteTest

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
  15
  ```

## ElanFPSResetTest

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
  4
  ```

## ElanFPSSensorTest

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
  2
  ```

## ElanFPSWOETest

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
  8
  ```

## FPCFPSTestPlusManualTest

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

`number_of_manual_captures`
: ```default
  10
  ```

## FPCFPSTestPlusPixelMedianTestForBloonchipper

### run_if

```default
device.component.has_fingerprint and device.component.fingerprint_board == 'bloonchipper'
```

### pytest_name

[fingerprint_sensor_fpc](../pytests/fingerprint_sensor_fpc.md)

### args

`fpframe_retry_count`
: ```default
  2
  ```

`max_dead_pixels`
: ```default
  10
  ```

`pixel_median`
: ```default
  {
    "cb_type1": [
      180,
      220
    ],
    "cb_type2": [
      80,
      120
    ],
    "icb_type1": [
      15,
      70
    ],
    "icb_type2": [
      155,
      210
    ]
  }
  ```

`detect_zones`
: ```default
  [
    [
      20,
      16,
      27,
      23
    ],
    [
      76,
      16,
      83,
      23
    ],
    [
      132,
      16,
      139,
      23
    ],
    [
      20,
      56,
      27,
      63
    ],
    [
      76,
      56,
      83,
      63
    ],
    [
      132,
      56,
      139,
      63
    ],
    [
      20,
      88,
      27,
      95
    ],
    [
      76,
      88,
      83,
      95
    ],
    [
      132,
      88,
      139,
      95
    ],
    [
      20,
      128,
      27,
      135
    ],
    [
      76,
      128,
      83,
      135
    ],
    [
      132,
      128,
      139,
      135
    ]
  ]
  ```

## FPCFPSTestPlusPixelMedianTestForDartmonkey

### run_if

```default
device.component.has_fingerprint and device.component.fingerprint_board == 'dartmonkey'
```

### pytest_name

[fingerprint_sensor_fpc](../pytests/fingerprint_sensor_fpc.md)

### args

`fpframe_retry_count`
: ```default
  2
  ```

`max_dead_pixels`
: ```default
  10
  ```

`pixel_median`
: ```default
  {
    "cb_type1": [
      180,
      220
    ],
    "cb_type2": [
      80,
      120
    ],
    "icb_type1": [
      15,
      70
    ],
    "icb_type2": [
      155,
      210
    ]
  }
  ```

`detect_zones`
: ```default
  [
    [
      8,
      16,
      15,
      23
    ],
    [
      24,
      16,
      31,
      23
    ],
    [
      40,
      16,
      47,
      23
    ],
    [
      8,
      66,
      15,
      73
    ],
    [
      24,
      66,
      31,
      73
    ],
    [
      40,
      66,
      47,
      73
    ],
    [
      8,
      118,
      15,
      125
    ],
    [
      24,
      118,
      31,
      125
    ],
    [
      40,
      118,
      47,
      125
    ],
    [
      8,
      168,
      15,
      175
    ],
    [
      24,
      168,
      31,
      175
    ],
    [
      40,
      168,
      47,
      175
    ]
  ]
  ```

## FPCFPSTestPlusRubberStamperTest

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

`rubber_finger_present`
: ```default
  true
  ```

## ProbeFingerprintSensor

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "fingerprint"
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
      "fingerprint",
      "==",
      1
    ]
  ]
  ```

## SetHasFingerprintForBloonchipper

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_fingerprint=1 && factory device-data component.fingerprint_board=bloonchipper"
  ```

## SetHasFingerprintForBuccaneer

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_fingerprint=1 && factory device-data component.fingerprint_board=buccaneer"
  ```

## SetHasFingerprintForDartmonkey

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_fingerprint=1 && factory device-data component.fingerprint_board=dartmonkey"
  ```

## UnsetHasFingerprint

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_fingerprint=0 && factory device-data component.fingerprint_board="
  ```

## UpdateFPFirmwareWithLocalBuildFirmware

### pytest_name

[update_fpmcu_firmware](../pytests/update_fpmcu_firmware.md)

### args

`method`
: ```default
  "UPDATE"
  ```

`firmware_file`
: ```default
  "/path/to/image.bin"
  ```

## ElanFPSTests

### Serial subtests

- [ElanFPSBaseTest]()
- [ElanFPSSensorTest]()
- [ElanFPSResetTest]()
- [ElanFPSWOETest]()
- ElanFPSNonInteractiveTest
- [ElanFPSCompleteTest]()

## FPCFPSTests

### Serial subtests

- FPCFPSTest
- [FPCFPSTestPlusManualTest]()
- [FPCFPSTestPlusPixelMedianTestForDartmonkey]()
- [FPCFPSTestPlusPixelMedianTestForBloonchipper]()
- [FPCFPSTestPlusRubberStamperTest]()

## FPSTestHelpers

### Serial subtests

- [SetHasFingerprintForBloonchipper]()
- [SetHasFingerprintForBuccaneer]()
- [SetHasFingerprintForDartmonkey]()
- [UnsetHasFingerprint]()
- [ProbeFingerprintSensor]()
- UpdateFPFirmware
- CheckFPFirmware
- [UpdateFPFirmwareWithLocalBuildFirmware]()
