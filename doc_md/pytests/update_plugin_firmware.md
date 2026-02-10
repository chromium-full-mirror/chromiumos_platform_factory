# update_plugin_firmware

**Source code:** [update_plugin_firmware.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_plugin_firmware.py)

Update vendor plugin firmware using fwupdtool.

## Description

This test updates the vendor plugin firmware by calling fwupdtool. User has to
specify the path to firmware and also the name of the plugin to be updated.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. Firstly, this test will create a DUT link.
2. If the firmware image is from the station, the image would be sent to DUT.
3. If the firmware image is in release partition, the test mounts the release
   partition to get the image.
4. If the firmware image is in test partition, the test mounts the test
   partition to get the image.

## Dependency

- DUT link must be ready before running this test.
- fwupdtool on DUT.

## Examples

To update the nvme firmware with the image in DUT release partition,
add this in test list:

```default
{
  "pytest_name": "update_plugin_firmware",
  "args": {
    "firmware_file": "/path/to/firmware/file/image.cab",
    "plugin": "nvme"
  }
}
```

To update the nvme firmware with the image in DUT test partition,
and allow downgrading the firmware version, add this in test list:

```default
{
  "pytest_name": "update_plugin_firmware",
  "args": {
    "allow_older": true,
    "firmware_file": "/path/to/firmware/file/image.cab",
    "from_release": false,
    "plugin": "nvme"
  }
}
```

## Test Arguments

| Name          | Type   | Description                                                            |
|---------------|--------|------------------------------------------------------------------------|
| allow_older   | bool   | (optional; default: `False`) Allow downgrading the firmware.           |
| firmware_file | str    | Name of the firmware binary file (.cab).                               |
| from_release  | bool   | (optional; default: `True`) Get the firmware file from release rootfs. |
| plugin        | str    | Specify the name of the plugin.                                        |
