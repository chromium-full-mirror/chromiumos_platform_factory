# generic_wireless_examples

Examples for testing wireless components. wireless is called “Wifi / Bluetooth” in AVL.

## Inherit

- [generic_wireless.test_list](generic_wireless.test_list.md)

## BluetoothDetectAdapterOnly

### pytest_name

[bluetooth](../pytests/bluetooth.md)

### args

`expected_adapter_count`
: ```default
  1
  ```

`scan_devices`
: ```default
  false
  ```

## BluetoothScanChromebook

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

`keyword`
: ```default
  "Chromebook"
  ```

## BluetoothScanSpecificStrength

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

`average_rssi_threshold`
: ```default
  -60.0
  ```

## ExampleWifiSSIDList

This test object cannot be run directly. Users have to inherit and modify it.

### pytest_name

[wifi_throughput](../pytests/wifi_throughput.md)

### args

`event_log_name`
: ```default
  "example_basic_ssid_list"
  ```

## IntelWirelessAntenna

Tested on device with component (cid, qid) = (3645, 7066)

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

`press_space_to_start`
: ```default
  false
  ```

## MediatekWirelessAntenna

Tested on device with component (cid, qid) = (5423, 12758)

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

`press_space_to_start`
: ```default
  false
  ```

## QualcommAtherosWirelessAntenna

Tested on device with component (cid, qid) = (3062, 5436).

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
  "station_dump"
  ```

`press_space_to_start`
: ```default
  false
  ```

## RealtekWirelessAntenna

Tested on device with component (cid, qid) = (1522, 5668)

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

`press_space_to_start`
: ```default
  false
  ```

## WifiThroughputInChamber

Users need to adjust the network topology and the IP. To pass go/pe-sw-gates, the device has to pass suite:wifi_perf which includes some iperf3 tests.

### pytest_name

[wifi_throughput](../pytests/wifi_throughput.md)

### args

`event_log_name`
: ```default
  "wifi_throughput_in_chamber"
  ```

`services`
: ```default
  [
    {
      "iperf_host": "127.0.0.1",
      "iperf_port": 5201,
      "min_rx_throughput": 80,
      "min_strength": -80,
      "password": "",
      "ssid": "GoogleGuest-Legacy"
    },
    {
      "iperf_host": "127.0.0.1",
      "iperf_port": 5201,
      "min_rx_throughput": 80,
      "min_strength": -80,
      "password": "",
      "ssid": "GoogleGuest-IPv4"
    }
  ]
  ```

`enable_iperf_server`
: ```default
  true
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

`press_space_to_start`
: ```default
  false
  ```

## WirelessAntennaSpecificFrequency

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
  [
    [
      "GoogleGuest-Legacy",
      2412,
      null
    ]
  ]
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

`press_space_to_start`
: ```default
  false
  ```

## BluetoothPairWithDevice

### Serial subtests

- ```default
  {
    "args": {
      "device_data_key": "factory.bluetooth_device_name",
      "label": "Bluetooth Device Name"
    },
    "inherit": "Scan",
    "label": "Scan Bluetooth Device Name"
  }
  ```
- ```default
  {
    "args": {
      "expected_adapter_count": 1,
      "keyword": "eval! device.factory.bluetooth_device_name",
      "pair_with_match": true,
      "scan_counts": 1,
      "scan_devices": true
    },
    "label": "Pair With Bluetooth Device",
    "pytest_name": "bluetooth"
  }
  ```

## ExampleWirelessConnect2G

### Serial subtests

- ```default
  {
    "args": {
      "device_data_key": "factory.wifi_2G_name",
      "label": "Wifi 2G Name"
    },
    "inherit": "Scan",
    "label": "Scan Wifi 2G Name"
  }
  ```
- ```default
  {
    "args": {
      "service_name": [
        {
          "passphrase": "",
          "security": "none",
          "ssid": "eval! device.factory.wifi_2G_name"
        }
      ]
    },
    "inherit": "WirelessConnect",
    "label": "Example Wireless Connect 2G"
  }
  ```

## ExampleWirelessConnect5G

### Serial subtests

- ```default
  {
    "args": {
      "device_data_key": "factory.wifi_5G_name",
      "label": "Wifi 5G Name"
    },
    "inherit": "Scan",
    "label": "Scan Wifi 5G Name"
  }
  ```
- ```default
  {
    "args": {
      "service_name": [
        {
          "passphrase": "",
          "security": "none",
          "ssid": "eval! device.factory.wifi_5G_name"
        }
      ]
    },
    "inherit": "WirelessConnect",
    "label": "Example Wireless Connect 5G"
  }
  ```

## WirelessTests

### Serial subtests

- ProbeDeviceInfo
- ProbeWireless
- [ExampleWifiSSIDList]()
- [WirelessAntenna]()
- [WirelessAntennaSpecificFrequency]()
- WirelessAntennaSwitchAntenna
- WirelessAntennaRadiotap
- [IntelWirelessAntenna]()
- [MediatekWirelessAntenna]()
- [QualcommAtherosWirelessAntenna]()
- [RealtekWirelessAntenna]()
- [WifiThroughputInChamber]()
- [ExampleWirelessConnect2G]()
- [ExampleWirelessConnect5G]()
- WirelessDisconnect
- Bluetooth
- [BluetoothDetectAdapterOnly]()
- [BluetoothScanChromebook]()
- [BluetoothScanSpecificStrength]()
- [BluetoothPairWithDevice]()
