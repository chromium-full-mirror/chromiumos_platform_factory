# wireless_connect

**Source code:** [wireless_connect.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/wireless_connect.py)

Connect to an AP.

## Description

Connect to an AP.

## Test Procedure

Auto.

## Dependency

- connection_manager goofy plugin

## Examples

To run this test on DUT, add a test item in the test list:

```default
{
  "inherit": "TestGroup",
  "label": "Example Wireless Connect 2G",
  "subtests": [
    {
      "pytest_name": "scan",
      "label": "Scan Wifi 2G Name",
      "related_components": [
        "test_tags.TestCategory.VPD"
      ],
      "args": {
        "device_data_key": "factory.wifi_2G_name",
        "label": "Wifi 2G Name"
      }
    },
    {
      "pytest_name": "wireless_connect",
      "label": "Example Wireless Connect 2G",
      "related_components": [
        "test_tags.TestCategory.WIFI"
      ],
      "args": {
        "service_name": [
          {
            "ssid": "eval! device.factory.wifi_2G_name",
            "security": "none",
            "passphrase": ""
          }
        ]
      }
    }
  ]
}
```

To disconnect to all WiFi services.:

```default
{
  "pytest_name": "wireless_connect",
  "label": "Disconnect from wireless networks",
  "related_components": [
    "test_tags.TestCategory.WIFI"
  ],
  "args": {
    "service_name": []
  }
}
```

## Test Arguments

| Name           | Type      | Description                                                                              |
|----------------|-----------|------------------------------------------------------------------------------------------|
| device_name    | str, None | (optional; default: `None`) The wifi interface                                           |
| service_name   | list      | (optional; default: `[]`) A list of wlan config. See net_utils.WLAN for more information |
| retries        | int       | (optional; default: `10`) Times to retry.                                                |
| sleep_interval | int       | (optional; default: `3`) Time to sleep.                                                  |
