# network_setup.network_setup

**Source code:** [network_setup/network_setup.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/network_setup/network_setup.py)

A pytest to wait operators setup network connection.

## Description

The test set up the network interface as the JSON config specified by
`config_name`.

The interface settings are saved in a JSON config file, the JSON schema for this
config file is py/test/pytests/network_setup/network_config.schema.json.

If some interface can not be set up, the test prompts the operator to check
whether the network cable is plugged as expected, and rerun the setup.

## Test Procedure

For each network interface specified in config, the test set up the interface
automatically. If everything goes well, the test pass without user interaction.

If the interface can’t be set up correctly, the test show error to operator.
Operator can check if cable is plugged as expected, and press space to retry.
The test would fail if space is not pressed within timeout, or the retry fails.

## Dependency

`cros.factory.test.utils.connection_manager`, which depends on `flimflam`.

## Examples

An example of the config file:

```default
--- py/test/pytests/network_setup/fft_network_config.json ---
{
  "eth1": {
    "address": "10.0.1.3",
    "prefixlen": 24
  },
  "/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1:1.0/net": {
    "address": "10.0.2.1",
    "prefixlen": 24,
    "gateway": "10.0.2.254"
  }
}
```

To set up the network using the config file above, add this in test list:

```default
{
  "pytest_name": "network_setup",
  "args": {
    "config_name": "fft_network_config"
  }
}
```

To set up the network using the same config file, but have a 30 seconds timeout
before retries:

```default
{
  "pytest_name": "network_setup",
  "args": {
    "config_name": "fft_network_config",
    "timeout_secs": 30
  }
}
```

## Test Arguments

| Name         | Type        | Description                                                                           |
|--------------|-------------|---------------------------------------------------------------------------------------|
| config_name  | str         | name of the config file.                                                              |
| timeout_secs | float, None | (optional; default: `None`) timeout seconds for each interface, default is no timeout |
