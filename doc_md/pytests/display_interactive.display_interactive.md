# display_interactive.display_interactive

**Source code:** [display_interactive/display_interactive.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/display_interactive/display_interactive.py)

Test display functionality with interactive mode.

## Description

This test runs in interactive mode and allows external control via an XML-RPC
server. A host (e.g., test station) can connect to this DUT to interact with
the test and control the display.

Supported XML-RPC Functions:
: - GetSerialNumber: Retrieves the DUT device serial number.
  - ShowPattern: Displays a pattern on the DUT screen. The pattern can be
    defined in CSS or specified as an image file name (without extension).
    Multiple patterns can be shown sequentially, with the previous
    pattern being hidden before the new one is displayed.
  - SetDisplayBrightness: Sets the brightness level of the display.
  - JudgeTestResult: Judges the given test result. The result should be either
    ‘PASS’ or ‘FAIL’. A failure reason can be provided when the result is
    ‘FAIL’.

## Test Procedure

> 1. The test starts an XML-RPC server on the specified port.
> 2. If the ‘autostart’ argument is set to True, the test automatically
>    enters fullscreen mode and sets the display brightness to maximum.
> 3. The test waits for the host to invoke XML-RPC functions to control
>    the display and judge the test result.

## Dependency

- This test uses an XML-RPC server.
- The ‘iptables’ command is used to configure firewall rules.

## Examples

To start the test in interactive mode:

```default
{
  "pytest_name": "display_interactive.display_interactive",
  "label": "Enter Front Of Screen Test Interactive Mode",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "port": 5566,
    "autostart": true
  }
}
```

## Test Arguments

| Name         | Type   | Description                                                                         |
|--------------|--------|-------------------------------------------------------------------------------------|
| autostart    | bool   | (optional; default: `False`) Automatically start the test and enter fullscreen mode |
| port         | int    | (optional; default: `5566`) XML-RPC server port                                     |
| timeout_secs | int    | (optional; default: `300`) Test timed out waiting for result                        |
