# ac_power

**Source code:** [ac_power.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/ac_power.py)

A test to ensure the power type and status of device under test.

## Description

The test detects the power type of the underlying device. It is also used to
ask operator to unplug the AC from the device.

## Test Procedure

To test if plugged AC power is detected properly:

1. Plug the designated power source to the device, and unplug all the other
   power sources.
2. Starts the test.

To test AC power unplugged:

1. Starts the test.
2. Follow the instruction on the UI to unplug the power.

## Dependency

- Need a power source.

For plugged with required power range:
- Need a USB PD power source with required power range.

## Examples

To test AC unplugged, add this to test list:

```default
{
  "pytest_name": "ac_power",
  "args": {
    "online": false
  }
}
```

To test USBPD 45W plugged on usbpd port 0:

```default
{
  "pytest_name": "ac_power",
  "args": {
    "power_type": "USB_PD",
    "usbpd_power_range": [0, 45, 45],
    "online": true
  }
}
```

## Test Arguments

| Name                   | Type       | Description                                                                                                                                                                                                  |
|------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| power_type             | str, None  | (optional; default: `None`) Type of the power source                                                                                                                                                         |
| usbpd_power_range      | list, None | (optional; default: `None`) The required power usbpd power range [usbpd_port, min, max]                                                                                                                      |
| online                 | bool       | (optional; default: `True`) True if expecting AC power                                                                                                                                                       |
| bft_fixture_class_name | str, None  | (optional; default: `None`) Fully-qualified class name of the BFTFixture implementation to use.                                                                                                              |
| bft_fixture_params     | dict, None | (optional; default: `None`) A dictionary of parameters for the BFTFixture class Init() method.                                                                                                               |
| retries                | int, None  | (optional; default: `None`) Maximum number of retries allowed to pass the test. 0 means only probe once. Default None means probe forever.                                                                   |
| polling_period_secs    | Real       | (optional; default: `1`) Polling period in seconds.                                                                                                                                                          |
| silent_warning         | int        | (optional; default: `2`) Skips first N charger type mismatch before giving a warning. Because EC needs about 1.6 seconds to identify charger type after it is plugged in, it skips first N mismatched probe. |
