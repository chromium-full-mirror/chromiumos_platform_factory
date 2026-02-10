# rf_graphyte.rf_graphyte

**Source code:** [rf_graphyte/rf_graphyte.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/rf_graphyte/rf_graphyte.py)

Tests RF chip’s transmitting and receiving capabilities using Graphyte.

## Description

A station-based test using
[Graphyte framework](https://chromium.googlesource.com/chromiumos/graphyte/)
to validate RF chip’s transmitting and receiving capabilities in conductive or
radiated way. Currently it supports WLAN, Bluetooth, and 802.15.4 technologies.

Graphyte is a RF testing framework that runs on Linux and ChromeOS, and
provide a unified RF testing way for each product in Google. It contains three
parts: Graphyte framework, DUT plugin and instrument plugin.

## Test Procedure

This is an automated test without user interaction.

1. (Optional) Use pytest `retrieve parameter` to fetch the config files from
   the Chrome OS factory server.
2. Start running Graphyte framework with the assigned config file.
3. Parse the result and upload them via testlog.

## Dependency

Need Graphyte framework with DUT and instrument plugins. This can be easily done
by deploying a RF bundle. First, you need to make a RF bundle as follows.

```bash
# Inside Chromium chroot
cros_workon --board <board> start graphyte-<board>
emerge-<board> graphyte-<board>
ls /build/<board>/var/lib/graphyte/rf_bundle_*.tar.gz
```

This will generate the RF bundle named `rf_bundle_*.tar.gz`. Copy this to
target machine, and install Graphyte by:

```bash
mkdir -p /tmp/graphyte
cd /tmp/graphyte
tar xvf /path/to/rf_bundle_xxx.tar.gz
./install_graphyte.sh
# Choose (Y) to install Graphyte to another folder
# Press (Enter) to install Graphyte to /usr/local
rm -rf /tmp/graphyte
```

## Examples

To run Graphyte framework with the config file conductive_config.json, add
this in test list:

```default
{
  "pytest_name": "rf_graphyte.rf_graphyte",
  "args": {
    "graphyte_config_file": "conductive_config.json",
    "verbose": true
  }
}
```

## Test Arguments

| Name                  | Type   | Description                                                                                                                                                                                |
|-----------------------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| graphyte_package      | str    | (optional; default: `'/usr/local/graphyte/'`) Path to Graphyte package folder                                                                                                              |
| graphyte_config_file  | str    | Path to Graphyte config file. This is passed to config-file parameter to Graphyte framework.                                                                                               |
| patch_dhcp_ssh_dut_ip | bool   | (optional; default: `False`) Set to True if Goofy uses SSH link with DHCP enabled to connect to DUT. This will patch the IP from Goofy’s link into Graphyte’s target DUT IP configuration. |
| verbose               | bool   | (optional; default: `True`) Enable Graphyte debug logging                                                                                                                                  |
