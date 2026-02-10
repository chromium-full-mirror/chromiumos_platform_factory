# generic_fat

## Inherit

- [generic_display_panel.test_list](generic_display_panel.test_list.md)
- [generic_dram.test_list](generic_dram.test_list.md)
- [generic_fingerprint.test_list](generic_fingerprint.test_list.md)
- [generic_tpm.test_list](generic_tpm.test_list.md)
- [generic_storage.test_list](generic_storage.test_list.md)
- [generic_common.test_list](generic_common.test_list.md)

## FAT

### Serial subtests

- [FATStart]()
- Barrier
- [FATItems]()
- CheckPoint
- [FATEnd]()

## FATEnd

### Serial subtests

- StationEnd
- CheckPoint

## FATItems

Test plans for Final Assembly Test.  The FAT is the first stage of FATP after Final Assembly, before Run In or Final Functional Testing (FFT). We want to collect system information and quickly probe if peripherals are assembled correctly.

### Serial subtests

- CheckSecdataVersion
- ModelSKU
- ChargerTypeDetection
- MemorySize
- EDPPanelTiming
- Barrier
- ThermalSensors
- Barrier
- VerifyRootPartition
- Barrier
- BadBlocks
- Barrier
- FPSGroup
- CopyMiniOS

## FATStart

### Serial subtests

- StationStart
- ```default
  {
    "subtests": [
      "GetDeviceInfo",
      "WriteDeviceDataToVPD",
      "WriteHWID"
    ]
  }
  ```
