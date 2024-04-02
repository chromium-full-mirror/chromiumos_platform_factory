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
- Prepare a config json file.
- In the factory repo, `setup/image_tool edit_custom_process -i shim.bin -f config_file.json`.
- Boot the factory shim and perform `action_p`.

Note:
- Check [RMA SHIM](./RMA_SHIM.md) for the details of image tool.
- The format of config file is an array of actions, the action_p will execute
the actions in order.
```
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
```
config_file.json
[
    "ResetDevice",
]
```

#### Charge/Discharge the battery
This action makes sure the state of battery meets the config in [cutoff.json](../sh/cutoff/README.md).
```
config_file.json
[
    "ChargeBattery",
]
```

#### Request a http request
This action sends a post request to a specific url with specific arguments.
```
config_file.json
[
    "HttpRequest": {"url": "<url>", "post_arg": {"<key>": "<value>"}}
]
```

#### Display QRcodes
This action displays multiple qrcodes with specific size in specific location.
If `position` is not given, the qrcode will be displayed in the center.
```
config_file.json
[
    "DisplayQRcode": {
        "qrcodes": [{"size": <size>, "position": [<x>, <y>], "content": "<string to display>"}]
    }
]
```

#### Wait a user input
This action stops the process and waits user to input a specific string and
press enter to continue the process.
```
config_file.json
[
    "StopAndConfirm": "<string to input>"
]
```

#### Check AC state
This action makes sure the state of AC meets the config in [cutoff.json](../sh/cutoff/README.md)
```
config_file.json
[
    "CheckAcState"
]
```

#### Cutoff the battery
This action cuts off the battery by the method in [cutoff.json](../sh/cutoff/README.md)
and sets the charge mode to normal.

This action is mandatory to be executed in the end of the process.