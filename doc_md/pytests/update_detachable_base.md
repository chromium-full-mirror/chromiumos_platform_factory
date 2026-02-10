# update_detachable_base

**Source code:** [update_detachable_base.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_detachable_base.py)

Detachable base update test

## Description

For detachable projects, the detachable base (as a USB device) may need to be
updated with its standalone EC and touchpad firmware.
This test leverages `hammerd`, which is the dedicated daemon for updating
detachable base firmware, to help factory automize firmware update and basic
verification.

## Test Procedure

1. Test will try to locate detachable base with the given USB device info.
   If the info is not provided from test lists, the test will try to get it
   from `cros_config`.
2. Hammerd is invoked to update base’s EC and touch firmware. If the path to EC
   or touch firmware is not specified, the test will extract the firmware from
   the release or test rootfs depending on `from_release`.
3. Verify base is properly updated by probing base info and doing some
   preliminary checkings.

Note that one might want to disable hammerd being inited on boot by configuring
upstart. See [here](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/init/preinit.d/inhibit_jobs/README.md)
for detail.

In addition, it’s recommended to configure detachable base info in
chromeos-config (instead of test lists) with following properties provided:

- ec-image-name
- touch-image-name
- vendor-id
- product-id
- usb-path

So that the it can be maintained in the standalone config and be easily shared
across the system.

## Dependency

- chromeos_config (cros_config)
- hammerd
- usb_updater2
- hammer_info.py

## Examples

If detachable base information is ready in cros_config and user would like to
update using the images extracted from release rootfs:

```default
{
  "pytest_name": "update_detachable_base"
}
```

If explicitly supplying detachable base info (Krane for example):

```default
{
  "pytest_name": "update_detachable_base",
  "args": {
    "from_release": false,
    "usb_path": "1-1.1",
    "product_id": 20540,
    "vendor_id": 6353,
    "ec_image_path": "/lib/firmware/masterball.fw",
    "touchpad_image_path": "/lib/firmware/masterball-touch.fw"
  }
}
```

## Test Arguments

| Name                | Type      | Description                                                                            |
|---------------------|-----------|----------------------------------------------------------------------------------------|
| from_release        | bool      | (optional; default: `True`) Find the firmwares from release rootfs.                    |
| usb_path            | str, None | (optional; default: `None`) USB path for searching the detachable base.                |
| i2c_path            | str, None | (optional; default: `None`) I2C path for searching the detachable base.                |
| product_id          | int, None | (optional; default: `None`) Product ID of the USB device.                              |
| vendor_id           | int, None | (optional; default: `None`) Vendor ID of the USB device.                               |
| ec_image_path       | str, None | (optional; default: `None`) Path to the EC firmware image file under /lib/firmware.    |
| touchpad_image_path | str, None | (optional; default: `None`) Path to the touchpad image file under /lib/firmware.       |
| update              | bool      | (optional; default: `True`) Update detachable base FW (hammerd is needed)              |
| verify              | bool      | (optional; default: `True`) Verify base info after FW update. (usb_updater2 is needed) |
