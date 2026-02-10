# bcic

**Source code:** [bcic.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/bcic.py)

A test to set and check BC(battery config) in CBI(ChromeOS Board Info).

## Description

This test updates the battery config into CBI(BCIC).

## Test Procedure

This is an automated test without user interaction.

1. Retrieve the OEM name and model number of battery from ectool.
2. (Optional) Connect to the factory server to update the HWID bundle.
3. Retrieve the required information from the battery configuration in the
   HWID bundle.
4. Search for the specific battery config in the JSON file:

- If found, clear and write the information to the CBI.
- If not found, check if the active battery config is valid or not. Pass the
  test if it’s valid else fail the test.

  Note that since the JSON file might contain an updated config for a battery,
  we try to update from the JSON file whenever possible, even if the active
  battery config is already valid.

1. Check the information in the CBI to ensure that battery config saved in CBI
   is identical to the active battery config.

## Dependency

- `ectool`

## Examples

To update BCIC from the latest hwid bundle:

```default
{
  "pytest_name": "bcic",
  "args": {
    "action": "SET",
    "use_latest_hwid_bundle": true
  }
}
```

To update BCIC from the local hwid bundle:

```default
{
  "pytest_name": "bcic",
  "args": {
    "action": "SET",
    "use_latest_hwid_bundle": false
  }
}
```

To update BCIC from a local battert config:

```default
{
  "pytest_name": "bcic",
  "args": {
    "action": "SET",
    "use_latest_hwid_bundle": false
    "file_path": "/usr/share/bcic/rex.battery_config.json"
  }
}
```

To check BCIC:

```default
{
  "pytest_name": "bcic",
  "args": {
    "action": "CHECK",
    "use_latest_hwid_bundle": false
  }
}
```

## Test Arguments

| Name                   | Type             | Description                                                                 |
|------------------------|------------------|-----------------------------------------------------------------------------|
| action                 | [‘CHECK’, ‘SET’] | Which action to do.                                                         |
| use_latest_hwid_bundle | bool             | Whether to update the HWID bundle first and load the battery configfrom it. |
| file_path              | str              | (optional; default: `''`) The path to the battery config file.              |
