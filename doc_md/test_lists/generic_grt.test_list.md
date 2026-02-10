# generic_grt

## Inherit

- [generic_fingerprint.test_list](generic_fingerprint.test_list.md)
- [generic_tpm.test_list](generic_tpm.test_list.md)
- [generic_wireless.test_list](generic_wireless.test_list.md)
- [generic_common.test_list](generic_common.test_list.md)

## GRTFinalize

### pytest_name

[finalize](../pytests/finalize.md)

### args

`enable_factory_server`
: ```default
  "eval! constants.enable_factory_server"
  ```

`enforced_release_channels`
: ```default
  "eval! ['stable'] if options.phase == 'PVT' else None"
  ```

`enable_zero_touch`
: ```default
  "eval! constants.grt.enable_zero_touch"
  ```

`ec_pubkey_path`
: ```default
  "eval! constants.grt.ec_pubkey_path"
  ```

`ec_pubkey_hash`
: ```default
  "eval! constants.grt.ec_pubkey_hash"
  ```

`gooftool_skip_list`
: ```default
  "eval! constants.grt.gooftool_skip_list"
  ```

`gooftool_waive_list`
: ```default
  "eval! constants.grt.gooftool_waive_list"
  ```

`hwid_need_vpd`
: ```default
  "eval! constants.hwid_need_vpd"
  ```

`has_ec_pubkey`
: ```default
  "eval! constants.has_ec_pubkey"
  ```

`factory_process`
: ```default
  "eval! constants.factory_process"
  ```

`secure_wipe`
: ```default
  "eval! constants.grt.secure_wipe"
  ```

`upload_method`
: ```default
  "eval! 'factory_server' if constants.enable_factory_server else 'none'"
  ```

`write_protection`
: ```default
  "eval! constants.grt.force_write_protect or options.phase == 'PVT'"
  ```

`cbi_eeprom_wp_status`
: ```default
  "eval! constants.grt.cbi_eeprom_wp_status"
  ```

`is_reference_board`
: ```default
  "eval! constants.grt.is_reference_board"
  ```

`project`
: ```default
  "eval! constants.grt.project"
  ```

`mode`
: ```default
  "ASSEMBLED"
  ```

`skip_feature_tiering_steps`
: ```default
  "eval! constants.grt.skip_feature_tiering_steps"
  ```

`block_dev_mode`
: ```default
  "eval! constants.grt.block_dev_mode"
  ```

## GRT

### Serial subtests

- [GRTStart]()
- [GRTItems]()
- CheckPoint
- [GRTEnd]()
- AllCheckPoint
- [GRTFinalize]()

## GRTEnd

### Serial subtests

- StationEnd

## GRTItems

### Serial subtests

- ElanFPSNonInteractiveTest
- CheckSecdataVersion
- ReSignReleaseKernel
- UploadRegCodes
- UploadSerialNumberForAuditing
- UploadZeroTouchIds
- VerifyWidevineKeybox
- Ti50APROVerification

## GRTStart

### Serial subtests

- ProbeDeviceInfo
- AllCheckPoint
- StationStart
