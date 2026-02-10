# check_image_version

**Source code:** [check_image_version.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_image_version.py)

Check release or test OS image version on internal storage.

## Description

This test checks if Chrome OS test image or release image version in
‘/etc/lsb-release’ are greater than or equal to the value of argument
`min_version`, and/or checks if the version are smaller or equal to
`max_version`. If the version is too old or too new and argument
`reimage` is set to True, download and apply either remote netboot
firmware or cros_payload components from factory server.

Note when use_netboot is specified, the DUT will reboot into netboot firmware
and start network image installation process to re-image.

## Test Procedure

1. This test will first check if test image (when `check_release_image` is
   False) or release image (when `check_release_image` is True) version >=
   `min_version`, and/or version <= `max_version` If so, this test will
   pass.
2. If `reimage` is set to False, this test will fail.
3. If `require_space` is set to True, this test will wait for the user presses
   spacebar.
4. If `use_netboot` is set to True, this test will try to download
   netboot firmware from factory server and flash into AP firmware. Otherwise,
   download and install the selected component using `cros_payload` command.
   If the needed components are not available on factory server, this test will
   fail.
5. If `use_netboot` is set to True, The DUT will then reboot into netboot
   firmware and start network image installation process to reimage.

## Dependency

- If argument `reimage` is set to True, factory server must be set up and be
  ready for network image installation.
- If argument `use_netboot` is set to True, netboot firmware must be
  available on factory server.

## Examples

To check test image version is greater than or equal to 9876.5.4, add this in
test list:

```default
{
  "pytest_name": "check_image_version",
  "args": {
    "min_version": "9876.5.4",
    "reimage": false
  }
}
```

To check test image version is exact the same as 9876.5.4, add this in test
list:

```default
{
  "pytest_name": "check_image_version",
  "args": {
    "min_version": "9876.5.4",
    "max_version": "9876.5.4",
    "reimage": false
  }
}
```

Reimage if release image version is older than 9876.5.4 by flashing netboot
firmware and make pressing spacebar not needed:

```default
{
  "pytest_name": "check_image_version",
  "args": {
    "min_version": "9876.5.4",
    "check_release_image": true,
    "require_space": false
  }
}
```

Reimage if test image version is greater than or equal to 9876.5.2012_12_21_2359
(loose format version) by flashing netboot firmware image on factory server:

```default
{
  "pytest_name": "check_image_version",
  "args": {
    "min_version": "9876.5.2012_12_21_2359",
    "loose_version": true
  }
}
```

Reimage if release image is older than the release_image version on factory
server using cros_payload:

```default
{
  "pytest_name": "check_image_version",
  "args": {
    "check_release_image": true,
    "use_netboot": false
  }
}
```

To re-install the DLCs extracted from a release image:

```default
{
  "pytest_name": "check_image_version",
  "args": {
    "check_release_image": true,
    "use_netboot": false,
    "reinstall_only_dlc": true
  }
}
```

## Test Arguments

| Name                | Type      | Description                                                                                                                                                                                                |
|---------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| min_version         | str, None | (optional; default: `None`) Minimum allowed test or release image version.None to skip the check. If both min_version and max_version are setto None, the check will follow the version on factory server. |
| max_version         | str, None | (optional; default: `None`) Maximum allowed test or release image version.None to skip the check. If both min_version and max_version are setto None, the check will follow the version on factory server. |
| loose_version       | bool      | (optional; default: `False`) Allow any version number representation.                                                                                                                                      |
| reimage             | bool      | (optional; default: `True`) True to re-image when image version mismatch.                                                                                                                                  |
| require_space       | bool      | (optional; default: `True`) True to require a space key press before re-imaging.                                                                                                                           |
| check_release_image | bool      | (optional; default: `False`) True to check release image instead of test image.                                                                                                                            |
| verify_rootfs       | bool      | (optional; default: `True`) True to verify rootfs before install image.                                                                                                                                    |
| use_netboot         | bool      | (optional; default: `True`) True to image with netboot, otherwise cros_payload.                                                                                                                            |
| reinstall_only_dlc  | bool      | (optional; default: `False`) True to reinstall only DLCs from the release image on factory server. The release image version on factory server must match with the release image version on DUT.           |
