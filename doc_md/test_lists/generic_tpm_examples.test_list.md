# generic_tpm_examples

Examples for testing TPM. TPM is called “TPM”, or “Secure Element” in AVL.

## Inherit

- [generic_tpm.test_list](generic_tpm.test_list.md)

## AssertGSCBoardIDIsPrePVT

### pytest_name

[check_cr50_board_id](../pytests/check_cr50_board_id.md)

### args

`board_id_flags`
: ```default
  "PHASE_PREPVT"
  ```

## Cr50APROVerificationManual

### pytest_name

[cr50_ap_ro_verification](../pytests/cr50_ap_ro_verification.md)

### args

`timeout_secs`
: ```default
  5
  ```

`manual_test`
: ```default
  true
  ```

## ProbeTPM

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "tpm"
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
      "tpm",
      "==",
      1
    ]
  ]
  ```

## UpdateGSCFirmwareWithoutUpstart

### pytest_name

[update_cr50_firmware](../pytests/update_cr50_firmware.md)

### args

`upstart_mode`
: ```default
  false
  ```

## UpdateTi50From0o0o15To0o0o16

### pytest_name

[update_cr50_firmware](../pytests/update_cr50_firmware.md)

### args

`upstart_mode`
: ```default
  false
  ```

`firmware_file`
: ```default
  "/path/to/ti50.bin.prepvt"
  ```

`skip_prepvt_flag_check`
: ```default
  "eval! constants.phase != 'PVT'"
  ```

`force_ro_mode`
: ```default
  true
  ```

## CommonTests

### Serial subtests

- [ProbeTPM]()
- CheckSecdataVersion
- AssertGSCBoardIDIsUnset
- [AssertGSCBoardIDIsPrePVT]()
- [UpdateGSCFirmwareWithoutUpstart]()
- ClearTPMOwnerRequestGroup
- TPMState
- TPMVerifyEKGroup

## Cr50Tests

### Serial subtests

- UpdateCr50Firmware

## TPMTests

### Serial subtests

- [CommonTests]()
- [Cr50Tests]()
- [Ti50Tests]()

## Ti50Tests

### Serial subtests

- UpdateTi50Firmware
- [UpdateTi50From0o0o15To0o0o16]()
- Ti50APROVerification
