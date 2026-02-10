# probe_device_info

**Source code:** [probe_device_info.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/probe_device_info.py)

A factory test for probing device information and updating device data.

## Description

Probes device information, including Wi-Fi MAC address, Bluetooth MAC
address, RW firmware version, release image version, and manufacturer date.
The probed information is then updated to the device data factory section.
Allows for customization of data names via the data_names argument.

## Test Procedure

This is an automated test without user interaction.

## Dependency

- Device Data API (`cros.factory.test.device_data`).
- Bluetooth utility (`cros.factory.test.utils.bluetooth_utils`).
- Device utility (`cros.factory.device.device_utils`).

## Examples

Probe Wi-Fi and Bluetooth MAC address, rw firmware version, release image
version, manufacturer date, update to device data factory section using default
names:

```default
{
  "pytest_name": "probe_device_info"
}
```

Probe Wi-Fi and Bluetooth MAC address, rw firmware version, release image
version, manufacturer date, filter MAC address colon, update to device data
factory section using custom names:

```default
{
  "pytest_name": "probe_device_info",
  "label": "Probe Device Info",
  "args": {
    "filter_colon": true,
    "data_names": {
      "wifi_mac": "factory.WLANID",
      "bluetooth_mac": "factory.BTMAC",
      "rw_fwid": "factory.BIOS",
      "mfg_date": "factory.manufacture_date",
      "release_image_version": "factory.FSI"
    }
  }
}
```

Probe WI-FI MAC address, rw firmware version, release image version,
manufacturer date, and Bluetooth MAC address with specified manufacturer id,
update to device data factory section:

```default
{
  "pytest_name": "probe_device_info",
  "label": "Probe Device Info",
  "args": {
    "filter_colon": false,
    "manufacturer_id": 29
  }
}
```

## Test Arguments

| Name            | Type      | Description                                                                                                                                                                                                                                                              |
|-----------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| filter_colon    | bool      | (optional; default: `False`) If True, the Wi-Fi and Bluetooth MAC will filter out the colon.                                                                                                                                                                             |
| manufacturer_id | int, None | (optional; default: `None`) Specified manufacturer id of the bluetooth hci device adapter.                                                                                                                                                                               |
| uppercase_mac   | bool      | (optional; default: `True`) If True, the Wi-Fi and Bluetooth MAC are converted to uppercase.                                                                                                                                                                             |
| data_names      | dict      | (optional; default: `{}`) Custom names to store data in device data. The key should be one of [“wifi_mac”, “bluetooth_mac”, “rw_fwid”, “mfg_date”, “release_image_version”]. For example, to store RW firmware version in “factory.BIOS”, set “rw_fwid”: “factory.BIOS”. |
