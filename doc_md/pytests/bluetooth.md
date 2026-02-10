# bluetooth

**Source code:** [bluetooth.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/bluetooth.py)

A factory test to verify the functionality of bluetooth device.

## Description

A bluetooth test to detect adapter, scan bluetooth device, check average RSSI
value, and connect with the bluetooth input device.

To run this bluetooth test, the DUT must have at least one bluetooth adapter.

If argument `scan_devices` is set, there should be at least one remote
bluetooth device.

If argument `pair_with_match` is set, there should be a bluetooth input
device like a mouse.

## Test Procedure

1. Setup a bluetooth input device (like a mouse) if needed.
2. Enable the connection ability of bluetooth on DUT.
3. A prompt message will be displayed on the UI if `prompt_scan_message` and
   `scan_devices` is set.
4. The bluetooth test will run automatically.

## Dependency

- Device API (`cros.factory.device.chromeos.bluetooth`).
- Bluetooth utility (`cros.factory.test.utils.bluetooth_utils`).

## Examples

To detect the specified number of bluetooth adapter on DUT, add this in test
list:

```default
{
  "pytest_name": "bluetooth",
  "label": "Detect bluetooth adapter",
  "related_components": [
    "test_tags.TestCategory.WIFI"
  ],
  "args": {
    "expected_adapter_count": 1,
    "scan_devices": false
  }
}
```

To scan remote bluetooth device and try to find at least one device whose name
contains ‘Chromebook’:

```default
{
  "pytest_name": "bluetooth",
  "label": "Scan for Bluetooth device named Chromebook",
  "related_components": [
    "test_tags.TestCategory.WIFI"
  ],
  "args": {
    "expected_adapter_count": 1,
    "scan_devices": true,
    "keyword": "Chromebook"
  }
}
```

To check the the largest average RSSI among all scanned devices is bigger than
threshold:

```default
{
  "pytest_name": "bluetooth",
  "label": "Scan for Bluetooth devices with a specific strength threshold",
  "related_components": [
    "test_tags.TestCategory.WIFI"
  ],
  "args": {
    "expected_adapter_count": 1,
    "scan_devices": true,
    "average_rssi_threshold": -60.0
  }
}
```

To pair, connect with, and disconnect with the bluetooth device:

```default
{
  "inherit": "TestGroup",
  "label": "Pair With Bluetooth Device",
  "subtests": [
    {
      "pytest_name": "scan",
      "label": "Scan Bluetooth Device Name",
      "related_components": [
        "test_tags.TestCategory.VPD"
      ],
      "args": {
        "device_data_key": "factory.bluetooth_device_name",
        "label": "Bluetooth Device Name"
      }
    },
    {
      "pytest_name": "bluetooth",
      "label": "Pair With Bluetooth Device",
      "related_components": [
        "test_tags.TestCategory.WIFI"
      ],
      "args": {
        "expected_adapter_count": 1,
        "pair_with_match": true,
        "scan_devices": true,
        "scan_counts": 1,
        "keyword": "eval! device.factory.bluetooth_device_name"
      }
    }
  ]
}
```

## Test Arguments

| Name                             | Type              | Description                                                                                                                                                                                                                                                                  |
|----------------------------------|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| expected_adapter_count           | int               | (optional; default: `0`) Number of bluetooth adapters on the machine.                                                                                                                                                                                                        |
| manufacturer_id                  | int, None         | (optional; default: `None`) ID of the manufacturer.                                                                                                                                                                                                                          |
| detect_adapters_retry_times      | int               | (optional; default: `10`) Maximum retry time to detect adapters.                                                                                                                                                                                                             |
| detect_adapters_interval_secs    | int               | (optional; default: `2`) Interval in seconds between each retry to detect adapters.                                                                                                                                                                                          |
| read_bluetooth_uuid_timeout_secs | int, None         | (optional; default: `None`) Timeout to read bluetooth characteristics via uuid.                                                                                                                                                                                              |
| scan_devices                     | bool              | (optional; default: `False`) Scan bluetooth device.                                                                                                                                                                                                                          |
| prompt_scan_message              | bool              | (optional; default: `True`) Prompts a message to tell user to enable remote devices discovery mode.                                                                                                                                                                          |
| keyword                          | str, None         | (optional; default: `None`) Only cares remote devices whose “Name” contains keyword.                                                                                                                                                                                         |
| average_rssi_threshold           | float             | (optional; default: `-70.0`) Checks the largest average RSSI among scanned device is equal to or greater than average_rssi_threshold. The thresholds recommended by Google are -60.0 at 3ft (0.9144m) distance over the air or -70.0 at 6ft (1.8288m) distance over the air. |
| scan_counts                      | int               | (optional; default: `3`) Number of scans to calculate average RSSI.                                                                                                                                                                                                          |
| scan_timeout_secs                | int               | (optional; default: `10`) Timeout to do one scan.                                                                                                                                                                                                                            |
| input_device_mac                 | str, None         | (optional; default: `None`) The mac address of bluetooth input device.                                                                                                                                                                                                       |
| input_device_mac_key             | str, None         | (optional; default: `None`) A key for factory shared data containing the mac address.                                                                                                                                                                                        |
| input_device_rssi_key            | str, None         | (optional; default: `None`) A key for factory shared data containing the rssi value.                                                                                                                                                                                         |
| firmware_revision_string_key     | str, None         | (optional; default: `None`) A key of factory shared data containing firmware revision string.                                                                                                                                                                                |
| firmware_revision_string         | str, None         | (optional; default: `None`) The firmware revision string.                                                                                                                                                                                                                    |
| average_rssi_lower_threshold     | float, dict, None | (optional; default: `None`) Checks the average RSSI of the target mac is equal to or greater than this threshold.                                                                                                                                                            |
| average_rssi_upper_threshold     | float, dict, None | (optional; default: `None`) Checks the average RSSI of the target mac is equal to or less than this threshold.                                                                                                                                                               |
| pair_with_match                  | bool              | (optional; default: `False`) Whether to pair with the strongest match.                                                                                                                                                                                                       |
| finish_after_pair                | bool              | (optional; default: `False`) Whether the test should end immediately after pairing completes.                                                                                                                                                                                |
| unpair                           | bool              | (optional; default: `False`) Whether to unpair matching devices instead of pair.                                                                                                                                                                                             |
| check_shift_pair_keys            | bool              | (optional; default: `False`) Check if shift-p-a-i-r keys are pressed.                                                                                                                                                                                                        |
| check_battery_charging           | bool              | (optional; default: `False`) Whether to check if the battery is charging.                                                                                                                                                                                                    |
| read_battery_level               | int, None         | (optional; default: `None`) Read the battery level.                                                                                                                                                                                                                          |
| check_battery_level              | bool              | (optional; default: `False`) Whether to check the battery level.                                                                                                                                                                                                             |
| prompt_into_fixture              | bool              | (optional; default: `False`) Prompt the user to place the base into the test fixture.                                                                                                                                                                                        |
| use_charge_fixture               | bool              | (optional; default: `False`) Whether a charge fixture is employed.                                                                                                                                                                                                           |
| reset_fixture                    | bool              | (optional; default: `False`) Whether to reset the fixture.                                                                                                                                                                                                                   |
| start_charging                   | bool              | (optional; default: `False`) Prompt the user to start charging the base.                                                                                                                                                                                                     |
| enable_magnet                    | bool              | (optional; default: `False`) Enable the base.                                                                                                                                                                                                                                |
| reset_magnet                     | bool              | (optional; default: `False`) Reset the base.                                                                                                                                                                                                                                 |
| stop_charging                    | bool              | (optional; default: `False`) Prompt the user to stop charging the base.                                                                                                                                                                                                      |
| base_enclosure_serial_number     | str, None         | (optional; default: `None`) The base enclosure serial number.                                                                                                                                                                                                                |
| battery_log                      | str, None         | (optional; default: `None`) The battery log file.                                                                                                                                                                                                                            |
| expected_battery_level           | int               | (optional; default: `100`) The expected battery level.                                                                                                                                                                                                                       |
| log_path                         | str, None         | (optional; default: `None`) The directory of the log on the local test host.                                                                                                                                                                                                 |
| keep_raw_logs                    | bool              | (optional; default: `True`) Whether to attach the log by Testlog.                                                                                                                                                                                                            |
| test_host_id_file                | str, None         | (optional; default: `None`) The file storing the id of the test host.                                                                                                                                                                                                        |
