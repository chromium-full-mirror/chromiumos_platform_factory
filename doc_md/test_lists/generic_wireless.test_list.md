# generic_wireless

Predefined wireless tests. wireless is called “Wifi / Bluetooth” in AVL.

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## Bluetooth

### pytest_name

[bluetooth](../pytests/bluetooth.md)

### args

`expected_adapter_count`
: ```default
  1
  ```

`scan_devices`
: ```default
  true
  ```

## ProbeDeviceInfo

### pytest_name

[probe_device_info](../pytests/probe_device_info.md)

## ProbeWireless

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "wireless"
  ]
  ```

`config_file`
: ```default
  "/usr/local/factory/py/hwid/v3/default_probe_statement.json"
  ```

`overridden_rules`
: ```default
  [
    [
      "wireless",
      "==",
      1
    ]
  ]
  ```

## WifiSSIDList

This test object cannot be run directly. Users have to inherit and modify it.

### pytest_name

[wifi_throughput](../pytests/wifi_throughput.md)

## Wireless

Alias of WirelessAntenna for legacy test lists.

### pytest_name

[wireless_antenna](../pytests/wireless_antenna.md)

### args

`device_name`
: ```default
  "wlan0"
  ```

`ignore_missing_services`
: ```default
  true
  ```

`services`
: ```default
  "eval! constants.wireless_services"
  ```

`switch_antenna_config`
: ```default
  {
    "all": [
      3,
      3
    ],
    "aux": [
      2,
      2
    ],
    "main": [
      1,
      1
    ]
  }
  ```

`strength`
: ```default
  {
    "all": -60,
    "aux": -60,
    "main": -60
  }
  ```

`wifi_chip_type`
: ```default
  null
  ```

## WirelessAntenna

Auto detect the type of the wifi chip.

### pytest_name

[wireless_antenna](../pytests/wireless_antenna.md)

### args

`device_name`
: ```default
  "wlan0"
  ```

`ignore_missing_services`
: ```default
  true
  ```

`services`
: ```default
  "eval! constants.wireless_services"
  ```

`switch_antenna_config`
: ```default
  {
    "all": [
      3,
      3
    ],
    "aux": [
      2,
      2
    ],
    "main": [
      1,
      1
    ]
  }
  ```

`strength`
: ```default
  {
    "all": -60,
    "aux": -60,
    "main": -60
  }
  ```

`wifi_chip_type`
: ```default
  null
  ```

## WirelessAntennaRadiotap

Only allow wifi chips which supports radiotap.

### pytest_name

[wireless_antenna](../pytests/wireless_antenna.md)

### args

`device_name`
: ```default
  "wlan0"
  ```

`ignore_missing_services`
: ```default
  true
  ```

`services`
: ```default
  "eval! constants.wireless_services"
  ```

`switch_antenna_config`
: ```default
  {
    "all": [
      3,
      3
    ],
    "aux": [
      2,
      2
    ],
    "main": [
      1,
      1
    ]
  }
  ```

`strength`
: ```default
  {
    "all": -60,
    "aux": -60,
    "main": -60
  }
  ```

`wifi_chip_type`
: ```default
  "radiotap"
  ```

## WirelessAntennaSwitchAntenna

Only allow wifi chips which supports switch_antenna.

### pytest_name

[wireless_antenna](../pytests/wireless_antenna.md)

### args

`device_name`
: ```default
  "wlan0"
  ```

`ignore_missing_services`
: ```default
  true
  ```

`services`
: ```default
  "eval! constants.wireless_services"
  ```

`switch_antenna_config`
: ```default
  {
    "all": [
      3,
      3
    ],
    "aux": [
      2,
      2
    ],
    "main": [
      1,
      1
    ]
  }
  ```

`strength`
: ```default
  {
    "all": -60,
    "aux": -60,
    "main": -60
  }
  ```

`wifi_chip_type`
: ```default
  "switch_antenna"
  ```

## WirelessConnect

### pytest_name

[wireless_connect](../pytests/wireless_connect.md)

### args

`service_name`
: ```default
  [
    {
      "passphrase": "crosfactory",
      "security": "psk",
      "ssid": "crosfactory20"
    },
    {
      "passphrase": "crosfactory",
      "security": "psk",
      "ssid": "crosfactory21"
    }
  ]
  ```

## WirelessDisconnect

### pytest_name

[wireless_connect](../pytests/wireless_connect.md)

### args

`service_name`
: ```default
  []
  ```

## WirelessRadiotap

Alias of WirelessAntennaRadiotap for legacy test lists.

### pytest_name

[wireless_antenna](../pytests/wireless_antenna.md)

### args

`device_name`
: ```default
  "wlan0"
  ```

`ignore_missing_services`
: ```default
  true
  ```

`services`
: ```default
  "eval! constants.wireless_services"
  ```

`switch_antenna_config`
: ```default
  {
    "all": [
      3,
      3
    ],
    "aux": [
      2,
      2
    ],
    "main": [
      1,
      1
    ]
  }
  ```

`strength`
: ```default
  {
    "all": -60,
    "aux": -60,
    "main": -60
  }
  ```

`wifi_chip_type`
: ```default
  "radiotap"
  ```
