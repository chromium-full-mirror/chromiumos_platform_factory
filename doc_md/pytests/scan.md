# scan

**Source code:** [scan.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/scan.py)

Prompts the operator to input a string of data.

## Description

This test asks the operator to scan or type a string, usually
for provisioning manufacturing info like device serial number
or operator’s ID.

## Test Procedure

1. A prompt message will be displayed on the UI.
2. Operator enters a string using a barcode scanner, or by
   typing on keyboard.

## Dependency

If bft_fixture is specified, the ScanBarcode and related functions
must be implemented to provide scanned data.

## Examples

To ask the operator to scan the MLB serial number, add this in test list:

```default
{
  "pytest_name": "scan",
  "args": {
    "device_data_key": "serials.mlb_serial_number",
    "label": "MLB Serial Number"
  }
}
```

A regular expression can also be specified to check the validity:

```default
{
  "pytest_name": "scan",
  "args": {
    "regexp": ".+",
    "device_data_key": "serials.mlb_serial_number",
    "label": "MLB Serial Number"
  }
}
```

## Test Arguments

| Name                       | Type       | Description                                                                                                                                                                                                                                                                                                                                                       |
|----------------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| label                      | str, dict  | Name of the ID or serial number being scanned, e.g., “MLB serial number”                                                                                                                                                                                                                                                                                          |
| event_log_key              | str, None  | (optional; default: `None`) Key to use for event log                                                                                                                                                                                                                                                                                                              |
| testlog_key                | str, None  | (optional; default: `None`) Parameter key to use for testlog                                                                                                                                                                                                                                                                                                      |
| shared_data_key            | str, None  | (optional; default: `None`) Key to use to store in scanned value in shared data                                                                                                                                                                                                                                                                                   |
| serial_number_key          | str, None  | (optional; default: `None`) Key to use to store in scanned value in serial numbers                                                                                                                                                                                                                                                                                |
| device_data_key            | str, None  | (optional; default: `None`) Key to use to store in scanned value in device data                                                                                                                                                                                                                                                                                   |
| dut_data_key               | str, None  | (optional; default: `None`) Key to use to store in scanned value in DUT.                                                                                                                                                                                                                                                                                          |
| ro_vpd_key                 | str, None  | (optional; default: `None`) Key to use to store in scanned value in RO VPD                                                                                                                                                                                                                                                                                        |
| rw_vpd_key                 | str, None  | (optional; default: `None`) Key to use to store in scanned value in RW VPD                                                                                                                                                                                                                                                                                        |
| save_path                  | str, None  | (optional; default: `None`) The file path of saving scanned value                                                                                                                                                                                                                                                                                                 |
| regexp                     | str, None  | (optional; default: `None`) Regexp that the scanned value must match                                                                                                                                                                                                                                                                                              |
| check_device_data_key      | str, None  | (optional; default: `None`) Checks that the given value in device data matches the scanned value                                                                                                                                                                                                                                                                  |
| bft_scan_fixture_id        | bool       | (optional; default: `False`) True to scan BFT fixture ID.                                                                                                                                                                                                                                                                                                         |
| bft_scan_barcode           | bool       | (optional; default: `False`) True to trigger BFT barcode scanner.                                                                                                                                                                                                                                                                                                 |
| bft_save_barcode           | bool       | (optional; default: `False`) True to trigger BFT barcode scanner and save in BFT.                                                                                                                                                                                                                                                                                 |
| bft_get_barcode            | bool, str  | (optional; default: `False`) True to get barcode from BFT. BFT stores barcode in advance so this obtains barcode immidiately. If a string is given, will override default path (nuc_dut_serial_path)                                                                                                                                                              |
| bft_fixture                | dict, None | (optional; default: `None`) A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| barcode_scan_interval_secs | int, float | (optional; default: `2.0`) Interval for repeatedly trigger BFT’s barcode scaner                                                                                                                                                                                                                                                                                   |
| match_the_last_few_chars   | int        | (optional; default: `0`) This is for OP to manually input last few SN chars based on the sticker on machine to make sure SN in VPD matches sticker SN.                                                                                                                                                                                                            |
| ignore_case                | bool       | (optional; default: `False`) True to ignore case from input.                                                                                                                                                                                                                                                                                                      |
| value_assigned             | str, None  | (optional; default: `None`) If not None, use the value to fill the key.                                                                                                                                                                                                                                                                                           |
