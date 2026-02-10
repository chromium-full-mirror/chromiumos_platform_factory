# cec

**Source code:** [cec.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/cec.py)

Test and check cec power control feature on Chrome OS device.

## Description

This test checks cec power control feature by turning off and turning on the
display power. Cec power control consists of following functions:
(1) Wake up a monitor.
(2) Put a monitor on standby.
(3) Get the display status of a monitor.

To check if a ChromeOS device support this feature or not:
(1) It depends on the HW design. There is an HDMI CEC pin in the HDMI connector.
(2) CEC function(i.e. `cec-ctl`) has to be implemented to support it.

In case when a monitor cannot return the power status, we can set
`manual_mode` to check the power status manually.

## Test Procedure

This is an automated test without user interaction. The HDMI port should be
connected to a CEC-enabled TV.

If `manual_mode` is set, the operator has to press the key to indicate the
display status is on. Else the display status is off.

## Dependency

- HDMI-CEC support for display control in ChromeOS(cec-ctl)
- The driver of specified button source: GPIO.

## Examples

Read system information and power status for the monitor in /dev/cec1 and
verify that it is on:

```default
{
  "pytest_name": "cec",
  "args": {
    "index": 1,
    "power_on": true
  }
}
```

Read system information for the monitor in /dev/cec0 and check power status
manually. Verify that display can be turned on/off via CEC:

```default
{
  "pytest_name": "cec",
  "args": {
    "manual_mode": true,
    "power_on": true,
    "power_off": true
  }
}
```

## Test Arguments

| Name                    | Type   | Description                                                                                                                                                    |
|-------------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| standby_wait_time       | float  | (optional; default: `5.0`) Waiting time after standby test to make sure status request could return correct value. Increase it if needed.                      |
| image_view_on_wait_time | float  | (optional; default: `10.0`) Waiting time after image view on test to make sure status request could get correct value. Adjust it according to testing machine. |
| description_wait_time   | float  | (optional; default: `2.0`) Waiting time for tester to read description.                                                                                        |
| initial_status          | int    | (optional; default: `0`) Initial TV status (0 = ON, 1 = OFF).                                                                                                  |
| power_on                | bool   | (optional; default: `True`) Test power on command.                                                                                                             |
| power_off               | bool   | (optional; default: `True`) Test power off command.                                                                                                            |
| controller_type         | str    | (optional; default: `'AP'`) The CEC controller type (EC or AP) for the device.                                                                                 |
| index                   | int    | (optional; default: `0`) The index of the CEC device. The CEC device is at /dev/cec\`\`index\`\`                                                               |
| manual_mode             | bool   | (optional; default: `False`) Manually check if power status is on or off.                                                                                      |
