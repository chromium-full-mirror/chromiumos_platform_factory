# update_firmware

**Source code:** [update_firmware.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_firmware.py)

Runs chromeos-firmwareupdate to force update Main(AP)/EC/PD firmwares.

## Description

This test runs firmware updater from local storage or downloaded from remote
factory server to update Main(AP)/EC/PD firmware contents.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. If argument `download_from_server` is set to True, this test will try to
   download firmware updater from factory server and ignore argument
   `firmware_updater`. If firmware update is not available, this test will
   just pass and exit. If argument `download_from_server` is set to False and
   the path indicated by argument `firmware_updater` doesn’t exist, this test
   will abort.
2. This test will fail if there is another firmware updater running in the same
   time. Else, start running firmware updater.
3. If firmware updater finished successfully, this test will pass.
   Otherwise, fail.

## Dependency

- If argument `download_from_server` is set to True, firmware updater needs to
  be available on factory server. If `download_from_server` is set to False,
  firmware updater must be prepared in the path that argument
  `firmware_updater` indicated.

## Examples

To update all firmwares using local firmware updater, which is located in
‘/usr/local/factory/board/chromeos-firmwareupdate’:

```default
{
  "pytest_name": "update_firmware"
}
```

To update only RW Main(AP) firmware using remote firmware updater:

```default
{
  "pytest_name": "update_firmware",
  "args": {
    "download_from_server": true,
    "rw_only": true,
    "host_only": true
  }
}
```

Not to update firmware if the version is the same with current one
in the DUT:

```default
{
  "pytest_name": "update_firmware",
  "args": {
    "force_update": false
  }
}
```

## Test Arguments

| Name                 | Type   | Description                                                                                                                                                                       |
|----------------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| firmware_updater     | str    | (optional; default: `'/usr/local/google/home/chungsheng/chromiumos/src/platform/factory/board/chromeos-firmwareupdate'`) Full path of chromeos-firmwareupdate.                    |
| rw_only              | bool   | (optional; default: `False`) Update only RW firmware                                                                                                                              |
| host_only            | bool   | (optional; default: `False`) Update only host (AP, BIOS) firmware.                                                                                                                |
| download_from_server | bool   | (optional; default: `False`) Download firmware updater from server                                                                                                                |
| from_release         | bool   | (optional; default: `False`) Find the firmware from release rootfs.                                                                                                               |
| force_update         | bool   | (optional; default: `True`) force to update firmware even if the version is the same.                                                                                             |
| unlock_csme          | bool   | (optional; default: `True`) Unlock the Intel CSME from the updater before flashing. Please read the comments in UpdateFirmwareForIntelTi50Device for the expected update results. |
