# thunderbolt_loopback

**Source code:** [thunderbolt_loopback.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/thunderbolt_loopback.py)

Tests thunderbolt port with a loopback card.

## Description

Verifies the thunderbolt port with a loopback card.

## Test Procedure

1. Operator inserts the loopback card.
2. The tool sends payloads to the loopback card.
3. The tool receives payloads from the loopback card and checks correctness.
4. The tool collects lane margining data and uploads it to factory server or
   saves it to local factory report.
5. Operator removes the loopback card.

## Dependency

- Loopback card driver.
- tdtl tool if we want to test lane margining.
- Write serial number to device data before the test for data collecting.
- (Optional) Be able to connect factory server when running the test.

## Examples

Test controller 0-1 with port 0 with 60 seconds timeout:

```default
{
  "pytest_name": "thunderbolt_loopback"
  "args": {
    "usbpd_spec": {
      "port": 0
    },
    "timeout_secs": 60,
    "controller_patterns": [
      "0-1.*"
    ]
  }
}
```

Test controller 0-3 with CC1 port 1 with 60 seconds timeout:

```default
{
  "pytest_name": "thunderbolt_loopback"
  "args": {
    "usbpd_spec": {
      "port": 1,
      "polarity": 1
    },
    "timeout_secs": 60,
    "controller_patterns": [
      "0-3.*"
    ]
  }
}
```

## Test Arguments

| Name                        | Type               | Description                                                                                                                                                                                                                |
|-----------------------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| timeout_secs                | int, None          | (optional; default: `None`) Timeout value for the test.                                                                                                                                                                    |
| expected_link_speed         | [‘Fast’, ‘Slow’]   | (optional; default: `<LinkSpeedType.Fast: 'Fast'>`) Link speed.                                                                                                                                                            |
| expected_link_width         | [‘Dual’, ‘Single’] | (optional; default: `<LinkWidthType.Dual: 'Dual'>`) Link width.                                                                                                                                                            |
| packets_to_send             | int                | (optional; default: `1000`) Amount of packets to be sent.                                                                                                                                                                  |
| packets_to_receive          | int                | (optional; default: `1000`) Amount of packets to be received.                                                                                                                                                              |
| debugfs_path                | str, None          | (optional; default: `None`) The path of debugfs to test.                                                                                                                                                                   |
| controller_port             | str, None          | (optional; default: `None`) Please migrate to controller_patterns.                                                                                                                                                         |
| controller_patterns         | list, tuple        | (optional; default: `('0-1.\*', '0-3.\*', '1-1.\*', '1-3.\*')`) The list of the glob patterns of the controller port to test. Choose a subset of {_DEFAULT_CONTROLLER_PATTERNS!r}.                                         |
| usbpd_spec                  | dict               | A dict which must contain “port” and optionally specify “polarity”. For example, {“port”: 1, “polarity”: 1}.                                                                                                               |
| load_module                 | bool               | (optional; default: `True`) Load test module.                                                                                                                                                                              |
| check_muxinfo_only          | bool               | (optional; default: `False`) Check muxinfo only.                                                                                                                                                                           |
| lane_margining              | bool               | (optional; default: `True`) Collect lane margining data.                                                                                                                                                                   |
| lane_margining_timeout_secs | int, float         | (optional; default: `10`) Timeout for collecting lane margining data.                                                                                                                                                      |
| lane_margining_csv          | bool               | (optional; default: `False`) If set, will upload the lane margining data to the factory server at the end of the test. Thus, DUT needs to connect to the server. If not set, will only save testlog in the factory report. |
| check_card_removal          | bool               | (optional; default: `True`) If set, require removing the card after DMA test.                                                                                                                                              |
