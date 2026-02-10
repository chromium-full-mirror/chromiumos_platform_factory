# pd_fw_min_version

**Source code:** [pd_fw_min_version.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/pd_fw_min_version.py)

Check firmware version of PD (TCPC) chip equal to or larger than minimum
version noted in corresponding EC driver.

## Description

Some PD chip might have issues which need to be solved by the cooperation
between firmware of PD chip and corresponding EC driver. In order to make sure
PD chips are shipped with correct firmware version, this test asks two info from
EC via ectool; one is current firmware version and the other is the minimum
required firmware version. Then these two versions would be compared to confirm
firmware version in the PD chip is greater then or equal to minimum required
version.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- DUT link must be ready before running this test.
- `ectool` utility.

## Examples

To verify PD chip in the port 0, add this in test list:

```default
{
  "pytest_name": "pd_fw_min_version"
}
```

To verify multiple PD chips (ex: port 0 and 1), add this in test list:

```default
{
  "pytest_name": "pd_fw_min_version",
  "args": {
    "ports": [0, 1]
  }
}
```

## Test Arguments

| Name   | Type      | Description                                                  |
|--------|-----------|--------------------------------------------------------------|
| ports  | int, list | (optional; default: `0`) Specify which PD ports are checked. |
