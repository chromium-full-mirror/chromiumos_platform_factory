# update_fpmcu_firmware

**Source code:** [update_fpmcu_firmware.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_fpmcu_firmware.py)

Update Fingerprint MCU firmware.

## Description

This test provides two modes, update mode and check mode. Mode is
specified by the test argument `method`.

1. In update mode, the test runs flash_fp_mcu to update the current
   fingerprint firmware.
2. In check mode, the test checks if the fingerprint firmware version
   of the DUT is equal to the given version.

The FPMCU firmware image updates/checks either from a given path in the
station or on the DUT, or from the release partition on the DUT.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. Firstly, this test will create a DUT link.
2. If the FPMCU firmware image is from the station, the image would be sent
   to DUT.
3. If the FPMCU firmware image is not specified, the test mounts the release
   partition and gets the FPMCU firmware image from there.
4. If method is set to UPDATE, DUT runs flash_fp_mcu to update the
   fingerprint firmware using the specified image.
5. If method is set to CHECK_VERSION, DUT compares the version of the
   current fingerprint firmware and the version of the specified image.

## Dependency

- DUT link must be ready before running this test.
- flash_fp_mcu (from ec-utils-test package) on DUT.
- futility, crossystem, and cros_config on DUT.
- FPMCU firmware image must be prepared.
- Hardware write-protection must be disabled (crossystem wpsw_cur returns 0).

## Examples

To update the fingerprint firmware with the image in DUT release partition,
add this in test list:

```default
{
  "pytest_name": "update_fpmcu_firmware",
  "label": "Update Fingerprint Firmware",
  "run_if": "device.component.has_fingerprint",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ]
}
```

To update the fingerprint firmware with a specified image in the station/DUT
(only recommended in pre-PVT stages):

```default
{
  "pytest_name": "update_fpmcu_firmware",
  "label": "Update Fingerprint Firmware with Local Build Firmware",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "method": "UPDATE",
    "firmware_file": "/path/to/image.bin"
  }
}
```

To check if the fingerprint firmware version is equal to the version in the
release image:

```default
{
  "pytest_name": "update_fpmcu_firmware",
  "label": "Check Fingerprint Firmware",
  "run_if": "device.component.has_fingerprint",
  "related_components": [
    "test_tags.TestCategory.FINGERPRINT_SENSOR"
  ],
  "args": {
    "method": "CHECK_VERSION"
  }
}
```

## Test Arguments

| Name          | Type                        | Description                                                                                                                                            |
|---------------|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| firmware_file | str, None                   | (optional; default: `None`) The full path of the firmware binary file.                                                                                 |
| method        | [‘CHECK_VERSION’, ‘UPDATE’] | (optional; default: `<_MethodType.UPDATE: 'UPDATE'>`) Specify whether to update the fingerprint firmware or to check the fingerprint firmware version. |
