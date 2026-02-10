# ti50_ap_ro_verification

**Source code:** [ti50_ap_ro_verification.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/ti50_ap_ro_verification.py)

A test to ensure the AP RO verification works on Ti50.

## Description

The test is an end-to-end test that verify the functionality and firmware
with AP RO verification on Ti50.
It helps to carefully verify AP RO verification on Ti50 in the factory flow,
and make sure the verification can pass with any Google signed FW,
which prevent from Ti50 bricking the shipped device.
Before leaving the factory mode, the WPSR can be written for multiple times,
and the WPSR written in this test will be overwritten in finalize.

## Test Procedure

1. Enable software write protect (PVT/MP only).
2. Set board ID.
3. Set addressing mode and WPSR.
4. Reboot GSC by ‘gsctool -a –reboot’.
5. ‘gsctool -a -B’ should return ‘apro result (36)’. Otherwise fail the test.
6. Disable software write protect.

## Dependency

- gsctool >= 15287.0.0 to include ‘gsctool -a -reboot’.
- Ti50 >= 0.(24|23).20 (24 for prepvt and 23 for prod)
  to include ‘apro result (36)’.
- AP firmware is either preMP or MP signed.
  Will not work with test signed AP firmware.

## Examples

To test AP RO verification, add this to test list:

```default
{
  "inherit": "TestGroup",
  "label": "Ti50 AP RO Verification",
  "subtests": [
    {
      "pytest_name": "ti50_ap_ro_verification",
      "label": "Ti50 AP RO Verification (PVT)",
      "allow_reboot": true,
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT"
      ],
      "args": {
        "enable_swwp": true,
        "two_stages": "eval! constants.factory_process == 'TWOSTAGES'"
      }
    },
    {
      "pytest_name": "ti50_ap_ro_verification",
      "label": "Ti50 AP RO Verification (pre-PVT)",
      "run_if": "constants.phase != 'PVT'",
      "allow_reboot": true,
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT"
      ],
      "args": {
        "enable_swwp": false,
        "two_stages": "eval! constants.factory_process == 'TWOSTAGES'"
      }
    }
  ]
}
```

## Test Arguments

| Name        | Type   | Description                                                                     |
|-------------|--------|---------------------------------------------------------------------------------|
| enable_swwp | bool   | (optional; default: `False`) True for enabling SWWP (PVT/MP only).              |
| two_stages  | bool   | (optional; default: `False`) Whether the factory_process is “TWOSTAGES” or not. |
