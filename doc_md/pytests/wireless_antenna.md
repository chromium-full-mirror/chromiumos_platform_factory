# wireless_antenna

**Source code:** [wireless_antenna.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/wireless_antenna.py)

A factory test for basic Wifi.

## Description

This test checks if the signal strength of the antennas satisfy the input spec.

This test can accept a list of wireless services but only the strongest one is
used as the test AP and the other APs are ignored.

This test can test signal strength via `iw dev {device} scan` or radiotap.

Be sure to set AP correctly.
1. Select a fixed channel instead of auto.
2. Disable the power control in AP.
3. Make sure SSID of AP is unique.

## Test Procedure

1. Accepts a dict of antenna:strength and a list of (ssid, frequency).
2. For each (antenna, AP=(ssid, frequency)), we test the signal strength of it.
3. Chooses AP with maximum strength as the test AP.
4. Checks if (antenna, test AP) is greater than the spec for all antennas.

## Dependency

- iw utility
- ifconfig utility
- ip utility (radiotap)
- tcpdump utility (radiotap)
- `iw phy {phy_name} set antenna 1 1` (switch_antenna)

## Examples

To run this test on DUT, add a test item in the test list:

```default
{
  "pytest_name": "wireless_antenna",
  "label": "Wireless Antenna",
  "exclusive_resources": [
    "NETWORK"
  ],
  "related_components": [
    "test_tags.TestCategory.WIFI"
  ],
  "args": {
    "device_name": "wlan0",
    "ignore_missing_services": true,
    "services": "eval! constants.wireless_services",
    "switch_antenna_config": {
      "main": [
        1,
        1
      ],
      "aux": [
        2,
        2
      ],
      "all": [
        3,
        3
      ]
    },
    "strength": {
      "main": -60,
      "aux": -60,
      "all": -60
    },
    "wifi_chip_type": null,
    "press_space_to_start": false
  }
}
```

Set the 2nd element in a service if you only want to use a specific frequency:

```default
{
  "pytest_name": "wireless_antenna",
  "label": "Wireless Antenna With Specific Frequency",
  "exclusive_resources": [
    "NETWORK"
  ],
  "related_components": [
    "test_tags.TestCategory.WIFI"
  ],
  "args": {
    "device_name": "wlan0",
    "ignore_missing_services": true,
    "services": [
      [
        "GoogleGuest-Legacy",
        2412,
        null
      ]
    ],
    "switch_antenna_config": {
      "main": [
        1,
        1
      ],
      "aux": [
        2,
        2
      ],
      "all": [
        3,
        3
      ]
    },
    "strength": {
      "main": -60,
      "aux": -60,
      "all": -60
    },
    "wifi_chip_type": null,
    "press_space_to_start": false
  }
}
```

## Test Arguments

| Name                      | Type      | Description                                                                                                                                                                                                                                                                                                                                                                  |
|---------------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| device_name               | str, None | (optional; default: `None`) Wireless device name to test. e.g. wlan0. If not specified, it willfail if multiple devices are found, otherwise use the only one device it found.                                                                                                                                                                                               |
| services                  | list      | A list of `[<service_ssid>:str, <freq>:int|None, <password>:str|None]` sequences like `[[SSID1, FREQ1, PASS1], [SSID2, FREQ2, PASS2], ...]`. Each sequence should contain exactly 3 items. If `<freq>` is `None` the test will detect the frequency by `iw <device_name> scan` command automatically.  `<password>=None` implies the service can connect without a password. |
| ignore_missing_services   | bool      | (optional; default: `False`) Ignore services that are not found during scanning. This argument is not needed for switch antenna wifi chip                                                                                                                                                                                                                                    |
| scan_timeout              | int       | (optional; default: `20`) Timeout for scanning the services.                                                                                                                                                                                                                                                                                                                 |
| connect_timeout           | int       | (optional; default: `10`) Timeout for connecting to the service.                                                                                                                                                                                                                                                                                                             |
| strength                  | dict      | A dict of minimal signal strengths. For example, a dict like `{"main": strength_1, "aux": strength_2, "all": strength_all}`. The test will check signal strength according to the different antenna configurations in this dict.                                                                                                                                             |
| scan_count                | int       | (optional; default: `5`) Number of scans to get average signal strength.                                                                                                                                                                                                                                                                                                     |
| switch_antenna_config     | dict      | (optional; default: `{'main': [1, 1], 'aux': [2, 2], 'all': [3, 3]}`) A dict of `{"main": (tx, rx), "aux": (tx, rx), "all": (tx, rx)}` for the config when switching the antenna.                                                                                                                                                                                            |
| switch_antenna_sleep_secs | int       | (optional; default: `10`) The sleep time after switching antenna and ifconfig up. Need to decide this value carefully since it depends on the platform and antenna config to test.                                                                                                                                                                                           |
| press_space_to_start      | bool      | (optional; default: `True`) Press space to start the test.                                                                                                                                                                                                                                                                                                                   |
| wifi_chip_type            | str, None | (optional; default: `None`) The type of wifi chip. Indicates how the chip test the signal strength of different antennas. Currently, the valid options are `switch_antenna`, `radiotap`, `station_dump`, or `disable_switch`. If the value is None, it will detect the value automatically. Note that Qualcomm Atheros chip does not support auto-detection.                 |
| keep_monitor              | bool      | (optional; default: `False`) Set to True for WiFi driver that does not support `iw dev antmon0 del`.                                                                                                                                                                                                                                                                         |
