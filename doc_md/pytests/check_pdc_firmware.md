# check_pdc_firmware

**Source code:** [check_pdc_firmware.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_pdc_firmware.py)

A test to check PDC firmware information.

## Description

This test checks the PDC firmware version, name, and driver against expected
values or minimum versions.

## Test Procedure

This is an automated test without user interaction.

1. Retrieve the PDC firmware information using ectool pdchipinfo usbpdid.
2. Compare the retrieved information with the expected values (if provided).
3. Compare the retrieved version information with the minimum versions (if
   provided).

## Dependency

- `ectool`

## Examples

To check if the PDC firmware version is “0.0.0.0.0.0.27.1”:

```default
{
  "pytest_name": "check_pdc_firmware",
  "args": {
    "expected_fw_version_dec": "0.0.0.0.0.0.27.1",
    "expected_fw_name_str": "GOOG0000",
    "expected_driver_name": "realtek_rts54_pdc",
    "usb_pd_id": 0
  }
}
```

To check if the PDC firmware version is at least “0.0.0.0.0.0.27.0”:

```default
{
  "pytest_name": "check_pdc_firmware",
  "args": {
    "min_fw_version_dec": "0.0.0.0.0.0.27.0",
    "usb_pd_id": 0
  }
}
```

## Test Arguments

| Name                    | Type      | Description                                                    |
|-------------------------|-----------|----------------------------------------------------------------|
| expected_fw_version_dec | str, None | (optional; default: `None`) Expected PDC firmware version.     |
| min_fw_version_dec      | str, None | (optional; default: `None`) Minimum PDC firmware version.      |
| expected_fw_name_str    | str, None | (optional; default: `None`) Expected PDC firmware name string. |
| expected_driver_name    | str, None | (optional; default: `None`) Expected PDC driver name.          |
| usb_pd_id               | int       | (optional; default: `0`) USB PD ID of the PDC chip.            |
