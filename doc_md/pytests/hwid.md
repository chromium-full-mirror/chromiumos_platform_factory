# hwid

**Source code:** [hwid.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/hwid.py)

Uses HWID v3 to generate, encode, and verify the device’s HWID.

## Description

This test generates and verifies HWID of device under testing.

## Test Procedure

This test does not require operator interaction.
When `generate` is `True`, this test will do the following:

1. If `enable_factory_server` is `True`, it downloads latest HWID database
   from Google Factory Server.
2. Collect materials (including probed results, device data, and optionally
   the vpd data) from DUT for generating the HWID string.  This step is
   equivalent to executing `hwid collect-material` in shell.
3. Generate HWID by command `hwid generate --probed-results-file
   <probed-results> --material-file <hwid-material-file> --json-output`.
4. Verify generated HWID by `hwid verify --material-file <hwid-material-file>
   --phase <phase>`.
5. Write HWID to GBB by `hwid write <generated-hwid>`.

If `generate` is `False`, then instead of running `hwid generate` in step
3, it will just use `hwid read` to read saved HWID from the device.  And step
5 will be skipped.

If `vpd_data_file` is set to a string of `<path>`, the vpd-related
arguments for `hwid` tool will be `--vpd-data-file <path>`; otherwise if
`run_vpd` is `True`, the vpd-related arguments for `hwid` tool will be
`--run-vpd`.  Note that `run_vpd=True` has no effect if `vpd_data_file`
is set.

## Dependency

Various of system utilities like `vpd` and `flashrom` will be invoked to
grab materials from DUT.

## Examples

To generate and verify HWID, add this to your test list:

```default
{
  "pytest_name": "hwid",
  "label": "Write HWID"
}
```

If you are doing RMA, to allow `deprecated` components, you need to enable RMA
mode:

```default
{
  "pytest_name": "hwid",
  "label": "Write HWID",
  "args": {
    "rma_mode": true
  }
}
```

New HWID with ‘configless’ format is still under testing.  To enable this
feature, set argument like this:

```default
{
  "pytest_name": "hwid",
  "label": "Write HWID",
  "args": {
    "enable_configless_fields": true
  }
}
```

To override the default project name, use `project` arguments:

```default
{
  "pytest_name": "hwid",
  "label": "Write HWID",
  "args": {
    "project": "nirwen"
  }
}
```

## Test Arguments

| Name                                 | Type      | Description                                                                           |
|--------------------------------------|-----------|---------------------------------------------------------------------------------------|
| generate                             | bool      | (optional; default: `True`) Generate and write the HWID (if False, only verify it).   |
| enable_factory_server                | bool      | (optional; default: `True`) Update hwid data from factory server.                     |
| run_vpd                              | bool      | (optional; default: `False`) Run the vpd commandline tool to get the vpd data.        |
| vpd_data_file                        | str, None | (optional; default: `None`) Read the specified file to get the vpd data.              |
| rma_mode                             | bool      | (optional; default: `False`) Enable rma_mode, do not check for deprecated components. |
| verify_checksum                      | bool      | (optional; default: `True`) Enable database checksum verification.                    |
| enable_configless_fields             | bool      | (optional; default: `False`) Include the configless fields                            |
| enable_component_status_check_on_pvt | bool      | (optional; default: `True`) Enable component status check if the phase is PVT.        |
| include_brand_code                   | bool      | (optional; default: `True`) Include RLZ brand code                                    |
| project                              | str, None | (optional; default: `None`) Project name of the HWID.                                 |
