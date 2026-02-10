**source code:** [setup/CUSTOM\_RESET\_PROCESS.md](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/setup/CUSTOM_RESET_PROCESS.md)

# Custom Factory Reset Process

[TOC]

## Overview

The factory reset is the standard process that will be run in the [reset shim](https://docs.google.com/document/d/1TMLcsOpz0EeokAhMrWBEO1sNH_NTltc0EIoyElUGjtU/edit?tab=t.0#heading=h.lw60tlfrbrqw).
The process of factory reset is quite different between factories, since it
depends on how partners wants to control the factory flow.

To increase the flexibility without breaking the security concern, we enabled
some limited actions with limited arguments. This doc describes the format of
the config file, and the process to enable this feature.

### Steps

* Prepare a config json file.
* In the factory repo, `setup/image_tool edit_toolkit_config -i shim.bin`.
* Press 6 and input the path of the config file.
* Boot the factory shim and perform `action_p`.

Note:

* Check [RMA SHIM](RMA_SHIM.md) for the details of image tool.
* The format of config file is an array of actions, the action\_p will execute
  the actions in order.

```default
config_file.json
[
    <action1>,
    <action2>,
    <action3>,
    ...
]
```

### Actions

#### Reset the device

This action cleans the data on the device.

```default
config_file.json
[
    "ResetDevice",
]
```

#### Charge/Discharge the battery

This action makes sure the state of battery meets the config in [cutoff.json](../sh/cutoff/README.md).

```default
config_file.json
[
    "ChargeBattery",
]
```

#### Request a http request

This action sends a post request to a specific url with specific arguments.

```default
config_file.json
[
    {"HttpRequest": {"url": "<url>", "post_arg": {"<key>": "<value>"}}}
]
```

#### Display QRcodes

This action displays multiple qrcodes with specific size in specific location.
If `position` is not given, the qrcode will be displayed in the center.
If `continue_key` is given, the action will stop after displaying the qrcodes. The behavior is the same as
`StopAndConfirm`. We adjust the order of displayed content to make it more stable.
If the content contains the pattern `<ARGUMENT>`, then it will be replaced by the information of the DUT.

* `<hwid>` will be replaced by the hwid string.
* `<serial_number>` will be replaced by the serial\_number in vpd.
* `<mlb_serial_number>` will be replaced by the mlb\_serial\_number in vpd.
* `<wifi_mac0>` will be replaced by the wifi\_mac0 in vpd.
* `<service_tag>` will be replaced by the service\_tag in vpd.

```default
config_file.json
[
    {"DisplayQRcode": {
        "qrcodes": [{"size": <size>, "position": [<x>, <y>], "content": "<string to display>"}],
        "continue_key": "a"
    }}
]
```

#### Wait a user input

This action stops the process and waits user to input a specific string and
press enter to continue the process.

```default
config_file.json
[
    {"StopAndConfirm": "<string to input>"}
]
```

#### Check AC state

This action makes sure the state of AC meets the config in [cutoff.json](../sh/cutoff/README.md).

```default
config_file.json
[
    "CheckAcState"
]
```

#### Clear the terminal

This action clears the terminal.

```default
config_file.json
[
    "Clear"
]
```

#### Cutoff the battery

This action cuts off the battery by the method in [cutoff.json](../sh/cutoff/README.md)
and sets the charge mode to normal.

This action is mandatory to be executed in the end of the process.
