# ethernet

**Source code:** [ethernet.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/ethernet.py)

A factory test for basic ethernet connectivity.

## Description

A factory test for basic ethernet connectivity.

## Test Procedure

This is an automated test without user interaction. It may require user
to press the space bar if not set to auto_start.

## Dependency

The pytest depends on the ethernet on the system.

## Examples

To use the test:

```default
{
  "pytest_name": "ethernet",
  "label": "Ethernet Test",
  "related_components": [
    "test_tags.TestCategory.ETHERNET"
  ],
  "args": {
    "auto_start": true,
    "link_only": true,
    "iface": "eth0"
  }
}
```

## Test Arguments

| Name                    | Type            | Description                                                                                                                                    |
|-------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| auto_start              | bool            | (optional; default: `False`) Auto start option.                                                                                                |
| test_url                | str, None       | (optional; default: `None`) URL for testing data transmission.                                                                                 |
| md5sum                  | str, None       | (optional; default: `None`) md5sum of the test file in test_url.                                                                               |
| retry_interval_msecs    | int             | (optional; default: `1000`) Milliseconds before next retry.                                                                                    |
| iface                   | str, None       | (optional; default: `None`) Interface name for testing.                                                                                        |
| interface_name_patterns | list            | (optional; default: `['eno\*', 'ens\*', 'enp\*s\*', 'enx\*', 'eth\*']`) The ethernet interface name patterns                                   |
| link_only               | bool            | (optional; default: `False`) Only test if link is up or not                                                                                    |
| use_swconfig            | bool            | (optional; default: `False`) Use swconfig for polling link status.                                                                             |
| swconfig_switch         | str             | (optional; default: `'switch0'`) swconfig switch name.                                                                                         |
| swconfig_ports          | int, list, None | (optional; default: `None`) swconfig port numbers. Either a single int or a list of int.                                                       |
| swconfig_expected_speed | int, list, None | (optional; default: `None`) expected link speed, if a list is given, each integer in the list will be paired with each port in swconfig_ports. |
