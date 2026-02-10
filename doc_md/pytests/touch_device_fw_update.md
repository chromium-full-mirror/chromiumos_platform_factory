# touch_device_fw_update

**Source code:** [touch_device_fw_update.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/touch_device_fw_update.py)

Checks and updates touch device firmware.

## Description

This test only works for legacy devices. The name and usage of the
scripts under /opt/google/touch/scripts/\* were changed.

The current touch firmware in factory is updated at boot time by
[boot-update-firmware.conf](https://chromium.googlesource.com/chromiumos/platform2/+/main/init/upstart/boot-update-firmware.conf). If the fw version on factory branch test image and
FSI image are different then the fw is updated again on the first boot out of
factory.

## Test Procedure

The test runs automatically.

## Dependency

- /opt/google/touch/scripts/\*

## Examples

To check touchpad hover with default parameters without calibration, add this
in test list:

```default
{
  "pytest_name": "touch_device_fw_update",
  "label": "Touch Device FW Update",
  "related_components": [
    "test_tags.TestCategory.EMR_IC",
    "test_tags.TestCategory.TOUCHCONTROLLER",
    "test_tags.TestCategory.TRACKPAD",
    "test_tags.TestCategory.USI_CONTROLLER"
  ],
  "args": {
    "device_name": "MyTouchDevice",
    "fw_name": "xxx.bin",
    "fw_version": "160.0"
  }
}
```

## Test Arguments

| Name        | Type   | Description                                                 |
|-------------|--------|-------------------------------------------------------------|
| device_name | str    | Name of the touch device as in/sys/bus/i2c/devices/\*/name) |
| fw_name     | str    | Expected firmware file name (in /lib/firmware)              |
| fw_version  | str    | Expected firmware version                                   |
