# check_retimer_firmware

**Source code:** [check_retimer_firmware.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_retimer_firmware.py)

Check the retimer firmware version.

## Description

Verifies the retimer firmware version.

Retimer device gets enumerated if the port connect to nothing when booting and
it offlines itself if there is no updates to perform. We need to poke registers
to enumerate the retimer. See b/299950312#comment2 for more information.

## Test Procedure

1. Operator to remove all devices from usb type c ports.
2. The device enumerates retimers.
3. The test compares the actual version and the expected version.
4. The device offlines retimers.

## Dependency

- The retimer device node must support nvm_version.

## Examples

The minimal working example:

```default
{
  "CheckRetimerFirmware": {
    "pytest_name": "check_retimer_firmware",
    "args": {
      "controller_ports": [
        "0-0:1.1",
        "0-0:3.1"
      ],
      "usb_ports": [
        0,
        1
      ],
      "min_retimer_version": "21.0"
    }
  }
}
```

## Test Arguments

| Name                     | Type       | Description                                                                                                                                 |
|--------------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| wait_all_ports_unplugged | bool, None | (optional; default: `None`) Deprecated                                                                                                      |
| controller_ports         | list, None | (optional; default: `None`) All the controller ports that we want ot test. Must be a subset of (‘0-0:1.1’, ‘0-0:3.1’, ‘1-0:1.1’, ‘1-0:3.1’) |
| usb_ports                | list, None | (optional; default: `None`) All the usb ports that we want ot test.                                                                         |
| min_retimer_version      | str, None  | (optional; default: `None`) The minimum Retimer firmware version. Set to None to disable the check.                                         |
| max_retimer_version      | str, None  | (optional; default: `None`) The maximum Retimer firmware version. Set to None to disable the check.                                         |
| timeout_secs             | int        | (optional; default: `30`) Timeout in seconds when we ask operator to complete the challenge. None means no timeout.                         |
