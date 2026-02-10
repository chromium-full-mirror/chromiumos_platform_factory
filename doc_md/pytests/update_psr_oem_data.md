# update_psr_oem_data

**Source code:** [update_psr_oem_data.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_psr_oem_data.py)

A test to update and verify PSR OEM Data.

## Description

This pytest updates, commits and verifies PSR OEM Data. PSR OEM Data consists of
four NVARs: OEM Name, OEM Make, OEM Model, Country of Manufacturer.

## Test Procedure

This is an automated test without user interaction. There are two ways to update
PSR OEM Data. First is to update from the dictionary args.oem_data_value. All
four NVARs have to be in the dictionary and assigned a value. Second is to
update from a config file /usr/local/factory/py/config/oem_data.cfg.

## Dependency

- intel-psrtool

## Examples

To update PSR OEM Data, add this to the test list:

```default
{
  "pytest_name": "update_psr_oem_data",
  "args": {
    "update_from_config": false,
    "oem_data_value": {
      "OEM Name": "Intel",
      "OEM Make": "CCG",
      "OEM Model": "MMS-SMMS",
      "Country of Manufacturer": "TW"
    }
  }
}
```

To update PSR OEM Data from /usr/local/factory/py/config/oem_data.cfg, add this
to the test list:

```default
{
  "pytest_name": "update_psr_oem_data",
  "args": {
    "update_from_config": true
  }
}
```

## Test Arguments

| Name                 | Type   | Description                                                                                             |
|----------------------|--------|---------------------------------------------------------------------------------------------------------|
| oem_data_value       | dict   | (optional; default: `{}`) The value for each NVAR to update.                                            |
| update_from_config   | bool   | (optional; default: `True`) To update from config at /usr/local/factory/py/config/oem_data.cfg          |
| oem_data_config_path | str    | (optional; default: `'/usr/local/factory/py/config/oem_data.cfg'`) The file to update PSR OEM Data with |
