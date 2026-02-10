# intel_common

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## GetIntelDescriptorStatus

Get the status of Intel Descriptor (locked/unlocked). This test item should be run before LockIntelDescriptor and PSR test groups.

### pytest_name

[get_intel_desc_status](../pytests/get_intel_desc_status.md)

## SetEOMNVAR

### pytest_name

[setup_psr_feature](../pytests/setup_psr_feature.md)

### args

`action`
: ```default
  "set"
  ```

## StartPSRLog

### pytest_name

[setup_psr_feature](../pytests/setup_psr_feature.md)

### args

`action`
: ```default
  "start"
  ```

## UpdatePSROEMData

### run_if

```default
not device.factory.intel_desc_locked
```

### pytest_name

[update_psr_oem_data](../pytests/update_psr_oem_data.md)

### args

`update_from_config`
: ```default
  false
  ```

`oem_data_value`
: ```default
  {
    "Country of Manufacturer": "TW",
    "OEM Make": "ChromeOS",
    "OEM Model": "MTL vPro",
    "OEM Name": "Google"
  }
  ```

## LockIntelDescriptor

### run_if

```default
(constants.grt.force_write_protect or constants.phase == 'PVT') and not device.factory.intel_desc_locked
```

### Serial subtests

- ```default
  {
    "args": {
      "unlock_csme": false
    },
    "pytest_name": "update_firmware"
  }
  ```
- Barrier
- FullRebootStep

## StartPSRLogGroup

Put this test right before GRTFinalize to minimize logging

### run_if

```default
not device.factory.intel_desc_locked
```

### Serial subtests

- [SetEOMNVAR]()
- ```default
  {
    "inherit": "FullRebootStep",
    "run_if": "device.factory.psr_update_need_reboot"
  }
  ```
- ```default
  {
    "inherit": "SyncFactoryServer",
    "run_if": "device.factory.psr_update_need_reboot"
  }
  ```
- [StartPSRLog]()

## UpdateIntelFirmware

Depending on the current descriptor status, DUT will be updated with lock/unlocked FW.

### Serial subtests

- [GetIntelDescriptorStatus]()
- ```default
  {
    "args": {
      "unlock_csme": "eval! not device.factory.intel_desc_locked"
    },
    "pytest_name": "update_firmware"
  }
  ```
- Barrier
- FullRebootStep
