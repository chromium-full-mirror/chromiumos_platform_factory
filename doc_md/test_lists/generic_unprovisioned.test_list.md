# generic_unprovisioned

## Inherit

- [generic_smt.test_list](generic_smt.test_list.md)

## Provision

### Serial subtests

- [ProvisionStart]()
- UpdateCr50Firmware
- UpdateSKUID
- CheckPoint
- [ProvisionEnd]()

## ProvisionEnd

### Serial subtests

- StationEnd
- CheckPoint
- FullRebootStep

## ProvisionStart

### Serial subtests

- ReadDeviceDataFromVPD
- SyncFactoryServer
- SMTScanMLB
- SMTScanOperatorID
- SMTScanStationID
- StationStart
