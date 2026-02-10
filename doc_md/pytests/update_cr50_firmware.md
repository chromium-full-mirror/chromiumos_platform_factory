# update_cr50_firmware

**Source code:** [update_cr50_firmware.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_cr50_firmware.py)

Update Cr50 firmware.

## Description

This test provides two functionalities, toggled by the test argument `method`.

1. This test calls gsctool on DUT to update Cr50 firmware.
   By default, the update of RO happens if the version of the given firmware is
   newer than the version on the chip. The update of RW happens if the version
   of the given firmware is newer or the same as the version on the chip.
   In force RO mode (-q), it forces to update the RO even if the version of the
   given firmware is the same as the version on the chip. The chip will reboot
   automatically after the update.
   In upstart mode (-u), it prevents RW update if the version of the given
   firmware is the same as version on the chip. It also prevents the immediate
   reboot after the update.
2. In check mode, this test calls gsctool on DUT to check if the cr50
   firmware version is up-to-date.

The Cr50 firmware image to update or compare is either from a given path in
station or DUT, or from the release partition on DUT.

To prepare Cr50 firmware image on station, download the release image with
desired Cr50 firmware image and find the image in DEFAULT_FIRMWARE_PATH below.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. Firstly, this test will create a DUT link.
2. If Cr50 firmware image source is from station, the image would be sent to
   DUT.
3. If the Cr50 image is in release partition, the test mounts the release
   partition to get the Cr50 image.
4. If method is set to UPDATE, DUT runs gsctool to update
   Cr50 firmware using the specified Cr50 image.
5. If method is set to CHECK_VERSION, DUT runs gsctool to check
   whether the Cr50 firmware version is greater than or equals to the
   specified Cr50 image.

## Dependency

- DUT link must be ready before running this test.
- gsctool on DUT.
- Cr50 firmware image must be prepared.

## Examples

The standard way to update GSC firmware on the factory line is adding a
“UpdateCr50Firmware” test group or a “UpdateTi50Firmware” test group.

These test groups contain four steps:

1. Update the firmware (pytest: update_cr50_firmware)
2. Reboot (pytest: shutdown)
3. Check firmware version (pytest: update_cr50_firmware)
4. Clear inactivate slot. (for Ti50 only)

Step 1 (update firmware) checks the current firmware version, and decides
: whether to update the firmware or not. If the test updates the firmware,
  device data device.factory.cr50_update_need_reboot will be set to
  True. Otherwise, it will be set to False.

Step 2 (reboot) will be skipped if the device data is set to False while
: checking run-if.

Step 3 (check firmware) deletes the device data to clean up the state after
: the version is validated as up-to-date.

Step 4 (clear inactivate slot)
: Clear inactivate slot.

“UpdateCr50Firmware”

```default
{
  "inherit": "TestGroup",
  "label": "Update Cr50 Firmware",
  "subtests": [
    {
      "pytest_name": "update_cr50_firmware",
      "label": "Update CR50 Firmware",
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT"
      ]
    },
    {
      "inherit": "ShutdownStep",
      "pytest_name": "shutdown",
      "label": "Reboot",
      "run_if": "device.factory.cr50_update_need_reboot",
      "allow_reboot": true,
      "args": {
        "operation": "reboot"
      }
    },
    {
      "pytest_name": "update_cr50_firmware",
      "label": "Check Cr50 Firmware Version",
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT"
      ],
      "args": {
        "method": "CHECK_VERSION"
      }
    }
  ]
}
```

“UpdateTi50Firmware”

```default
{
  "inherit": "TestGroup",
  "label": "Update Ti50 Firmware",
  "subtests": [
    {
      "pytest_name": "update_cr50_firmware",
      "label": "Update Ti50 Firmware",
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT"
      ]
    },
    {
      "inherit": "ShutdownStep",
      "pytest_name": "shutdown",
      "label": "Reboot",
      "run_if": "device.factory.cr50_update_need_reboot",
      "allow_reboot": true,
      "args": {
        "operation": "reboot"
      }
    },
    {
      "pytest_name": "update_cr50_firmware",
      "label": "Check Ti50 Firmware Version",
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT"
      ],
      "args": {
        "method": "CHECK_VERSION"
      }
    },
    {
      "pytest_name": "clear_inactive_gsc_slot",
      "label": "Clear Inactive Ti50 Slot",
      "related_components": [
        "test_tags.TestCategory.SECURE_ELEMENT"
      ]
    }
  ]
}
```

Sometimes, e.g. b/145973336, it’s required to update GSC firmware without
upstart mode.

To update GSC firmware without upstart mode, unset upstart_mode argument and
set the pytest as allow_reboot. After updated and reboot, the test will be run
again and succeeds in the second run:

```default
{
  "pytest_name": "update_cr50_firmware",
  "label": "Update GSC Firmware without upstart",
  "allow_reboot": true,
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT"
  ],
  "args": {
    "upstart_mode": false
  }
}
```

To update Cr50 firmware with the Cr50 firmware image in station:

```default
{
  "pytest_name": "update_cr50_firmware",
  "args": {
    "firmware_file": "/path/on/station/to/cr50.bin.prod",
    "from_release": false
  }
}
```

To check if Cr50 firmware version is greater than or equals to the Cr50 image
in the release image:

```default
{
  "pytest_name": "update_cr50_firmware",
  "label": "Check Cr50 Firmware Version",
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT"
  ],
  "args": {
    "method": "CHECK_VERSION"
  }
}
```

To update the Ti50 firmware version from 0.0.15 (or earlier) to 0.0.16 (or
later) with prepvt firmware. See b/236793753 for more detail:

```default
{
  "pytest_name": "update_cr50_firmware",
  "label": "Update Ti50 Firmware from 0.0.15- to 0.0.16+",
  "allow_reboot": true,
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT"
  ],
  "args": {
    "upstart_mode": false,
    "firmware_file": "/path/to/ti50.bin.prepvt",
    "skip_prepvt_flag_check": "eval! constants.phase != 'PVT'",
    "force_ro_mode": true
  }
}
```

## Test Arguments

| Name                                  | Type                        | Description                                                                                                                                                                                                                                                                                                                                                      |
|---------------------------------------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| firmware_file                         | str, None                   | (optional; default: `None`) The full path of the firmware. If not set, the test will use the default prod firmware path to update the firmware.                                                                                                                                                                                                                  |
| from_release                          | bool                        | (optional; default: `True`) Find the firmware from release rootfs.                                                                                                                                                                                                                                                                                               |
| skip_prepvt_flag_check                | bool                        | (optional; default: `False`) (deprecated) This flag is deprecated and the firmware will only be check in finalize.                                                                                                                                                                                                                                               |
| method                                | [‘CHECK_VERSION’, ‘UPDATE’] | (optional; default: `<_MethodType.UPDATE: 'UPDATE'>`) Specify whether to update the Cr50 firmware or to check the firmware version.                                                                                                                                                                                                                              |
| upstart_mode                          | bool                        | (optional; default: `True`) Use upstart mode to update Cr50 firmware. The DUT will not reboot automatically after the update.                                                                                                                                                                                                                                    |
| force_ro_mode                         | bool                        | (optional; default: `False`) Force to update the inactive RO even if the RO version on DUT is the same as given firmware. The DUT will reboot automatically after the update                                                                                                                                                                                     |
| set_recovery_request_train_and_reboot | bool                        | (optional; default: `False`) Set recovery request to VB2_RECOVERY_TRAIN_AND_REBOOT. For some boards, the device will reboot into recovery mode with default (v0.0.22) cr50 firmware. Setting this will make the device update the cr50 firmware and then automatically reboot back to normal mode after updating cr50 firmware. See b/154071064 for more details |
| check_version_retry_timeout           | int                         | (optional; default: `10`) If the version is not matched, retry the check after the specific seconds.  Set to 0 to disable the retry.                                                                                                                                                                                                                             |
