# battery_current

**Source code:** [battery_current.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/battery_current.py)

A factory test to test battery charging/discharging current.

## Description

Test battery charging and discharging current.

If usbpd_info is set, also prompt operator to insert a power adapter of given
voltage to the given USB type C port.

The usbpd_info is a sequence (usbpd_port, min_millivolt, max_millivolt),
represent the USB type C port to insert power adapter:

- `usbpd_port`: (int) usbpd_port number. Specify which port to insert power
  line.
- `min_millivolt`: (int) The minimum millivolt the power must provide.
- `max_millivolt`: (int) The maximum millivolt the power must provide.

## Test Procedure

1. If max_battery_level is set, check that initial battery level is lower
   than the value.
2. If usbpd_info is set, prompt the operator to insert a power adapter of
   given voltage to the given USB type C port, and pass this step when one is
   detected.
3. If min_charging_current is set, force the power into charging mode, and
   check if the charging current is larger than the value.
4. If min_discharging_current is set, force the power into discharging mode,
   and check if the discharging current is larger than the value.
5. If current_difference is set, force the power into charging mode first,
   and record the charging current. Then force the power into discharging mode,
   and also record the discharging current. Pass the test if the (average
   charging current - average discharging current) is greater or equal to the
   value.

Each step would fail after timeout_secs seconds.

## Dependency

Device API cros.factory.device.power.

If usbpd_info is set, device API cros.factory.device.usb_c.GetPDPowerStatus
is also used.

## Examples

To check battery can charge and discharge, add this in test list:

```default
{
  "pytest_name": "battery_current",
  "label": "Charge Discharge Current",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY",
    "test_tags.TestCategory.USB_INTEGRATED"
  ],
  "args": {
    "min_charging_current": 150,
    "min_discharging_current": 400,
    "timeout_secs": 30,
    "max_battery_level": 90
  }
}
```

Sometimes, the system consumes more power than the charger. In that case, we
could set the min_charging_current to negative value, and the test would pass
if the battery discharges less than 150 mA. See b/183679223#comment25:

```default
{
  "pytest_name": "battery_current",
  "label": "Charge Discharge Current Expect No Charge When Charging",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY",
    "test_tags.TestCategory.USB_INTEGRATED"
  ],
  "args": {
    "min_charging_current": -150,
    "min_discharging_current": 400,
    "timeout_secs": 30,
    "max_battery_level": 90
  }
}
```

Alternatively, we could also set current_difference to just test the difference
between charge and discharge:

```default
{
  "pytest_name": "battery_current",
  "label": "Charge Discharge Current Difference",
  "exclusive_resources": [
    "POWER"
  ],
  "related_components": [
    "test_tags.TestCategory.BATTERY",
    "test_tags.TestCategory.USB_INTEGRATED"
  ],
  "args": {
    "min_charging_current": null,
    "min_discharging_current": null,
    "timeout_secs": 30,
    "max_battery_level": 90,
    "current_difference": 250
  }
}
```

To check that a 20V USB type C power adapter is connected to port 0, add this
in test list:

```default
{
  "pytest_name": "battery_current",
  "label": "Charger 20V In Port 0",
  "related_components": [
    "test_tags.TestCategory.BATTERY",
    "test_tags.TestCategory.USB_INTEGRATED"
  ],
  "args": {
    "usbpd_info": [
      0,
      19000,
      21000
    ],
    "usbpd_prompt": "i18n! USB TypeC"
  }
}
```

## Test Arguments

| Name                    | Type       | Description                                                                                                                                               |
|-------------------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| min_charging_current    | int, None  | (optional; default: `None`) minimum allowed charging current                                                                                              |
| min_discharging_current | int, None  | (optional; default: `None`) minimum allowed discharging current                                                                                           |
| current_difference      | int, None  | (optional; default: `None`) The minimum current difference between the charging mode and discharging mode.                                                |
| retry_times             | int        | (optional; default: `2`) Retry for a number of times if the current_difference test fails                                                                 |
| timeout_secs            | int        | (optional; default: `30`) Test timeout value                                                                                                              |
| max_battery_level       | int, None  | (optional; default: `None`) maximum allowed starting battery level                                                                                        |
| usbpd_info              | list, None | (optional; default: `None`) A sequence [usbpd_port, min_millivolt, max_millivolt] used to select a particular port from a multi-port DUT.                 |
| use_max_voltage         | bool       | (optional; default: `False`) Use the negotiated max voltage in ectool usbpdpower to check charger voltage, in case that instant voltage is not supported. |
| usbpd_prompt            | str, dict  | (optional; default: `''`) prompt operator which port to insert                                                                                            |
