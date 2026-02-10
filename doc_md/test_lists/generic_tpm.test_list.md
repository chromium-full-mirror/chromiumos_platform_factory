# generic_tpm

Predefined TPM tests. TPM is called “TPM”, or “Secure Element” in AVL.

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## APROVerification

Make old definition as an alias of the new definition for backward compatibility

### pytest_name

[cr50_ap_ro_verification](../pytests/cr50_ap_ro_verification.md)

## AssertGSCBoardIDIsUnset

### pytest_name

[check_cr50_board_id](../pytests/check_cr50_board_id.md)

### args

`board_id_type`
: ```default
  "ffffffff"
  ```

`board_id_flags`
: ```default
  "ffffffff"
  ```

## CheckCr50BoardIDNotSet

Make old definition as an alias of the new definition for backward compatibility

### pytest_name

[check_cr50_board_id](../pytests/check_cr50_board_id.md)

### args

`board_id_type`
: ```default
  "ffffffff"
  ```

`board_id_flags`
: ```default
  "ffffffff"
  ```

## CheckCr50FirmwareVersion

### pytest_name

[update_cr50_firmware](../pytests/update_cr50_firmware.md)

### args

`method`
: ```default
  "CHECK_VERSION"
  ```

## CheckSecdataVersion

### pytest_name

[check_secdata_version](../pytests/check_secdata_version.md)

### args

`major_version`
: ```default
  1
  ```

`minor_version`
: ```default
  0
  ```

## CheckTi50FirmwareVersion

### pytest_name

[update_cr50_firmware](../pytests/update_cr50_firmware.md)

### args

`method`
: ```default
  "CHECK_VERSION"
  ```

## ClearAPROHash

Make old definition as an alias of the new definition for backward compatibility

### pytest_name

[cr50_ap_ro_hash](../pytests/cr50_ap_ro_hash.md)

### args

`action`
: ```default
  "clear"
  ```

## ClearCr50APROHash

### pytest_name

[cr50_ap_ro_hash](../pytests/cr50_ap_ro_hash.md)

### args

`action`
: ```default
  "clear"
  ```

## ClearInactiveTi50Slot

### pytest_name

[clear_inactive_gsc_slot](../pytests/clear_inactive_gsc_slot.md)

## ClearTPMOwnerRequest

### pytest_name

[tpm_clear_owner](../pytests/tpm_clear_owner.md)

## Cr50APROVerification

### pytest_name

[cr50_ap_ro_verification](../pytests/cr50_ap_ro_verification.md)

## SetAPROHash

Make old definition as an alias of the new definition for backward compatibility

### pytest_name

[cr50_ap_ro_hash](../pytests/cr50_ap_ro_hash.md)

### args

`action`
: ```default
  "set"
  ```

## SetCr50APROHash

### pytest_name

[cr50_ap_ro_hash](../pytests/cr50_ap_ro_hash.md)

### args

`action`
: ```default
  "set"
  ```

## TPMState

Only needed and applicable for certain projects. b/198711349

### pytest_name

[tpm_state](../pytests/tpm_state.md)

## TPMVerifyEK

### pytest_name

[tpm_verify_ek](../pytests/tpm_verify_ek.md)

## APROVerificationGroup

Make old definition as an alias of the new definition for backward compatibility

### Serial subtests

- [SetCr50APROHash]()
- [Cr50APROVerification]()
- [ClearCr50APROHash]()

## ClearTPMOwnerRequestGroup

### Serial subtests

- [ClearTPMOwnerRequest]()
- RebootStep

## Cr50APROVerificationGroup

### Serial subtests

- [SetCr50APROHash]()
- [Cr50APROVerification]()
- [ClearCr50APROHash]()

## TPMVerifyEKGroup

### Serial subtests

- [TPMVerifyEK]()
- RebootStep

## Ti50APROVerification

### Serial subtests

- ```default
  {
    "allow_reboot": true,
    "args": {
      "enable_swwp": true,
      "two_stages": "eval! constants.factory_process == 'TWOSTAGES'"
    },
    "label": "Ti50 AP RO Verification (PVT)",
    "pytest_name": "ti50_ap_ro_verification"
  }
  ```
- ```default
  {
    "allow_reboot": true,
    "args": {
      "enable_swwp": false,
      "two_stages": "eval! constants.factory_process == 'TWOSTAGES'"
    },
    "label": "Ti50 AP RO Verification (pre-PVT)",
    "pytest_name": "ti50_ap_ro_verification",
    "run_if": "constants.phase != 'PVT'"
  }
  ```

## UpdateCr50Firmware

### Serial subtests

- ```default
  {
    "pytest_name": "update_cr50_firmware"
  }
  ```
- ```default
  {
    "inherit": "RebootStep",
    "run_if": "device.factory.cr50_update_need_reboot"
  }
  ```
- [CheckCr50FirmwareVersion]()

## UpdateTi50Firmware

### Serial subtests

- ```default
  {
    "label": "Update Ti50 Firmware",
    "pytest_name": "update_cr50_firmware"
  }
  ```
- ```default
  {
    "inherit": "RebootStep",
    "run_if": "device.factory.cr50_update_need_reboot"
  }
  ```
- [CheckTi50FirmwareVersion]()
- [ClearInactiveTi50Slot]()
