# bluetooth_host

**Source code:** [bluetooth_host.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/bluetooth_host.py)

Station-based Bluetooth scan and pair test, using hciconfig and hcitool.

## Description

Station-based Bluetooth scan and pair test, using hciconfig and hcitool.

## Test Procedure

This is an automated test.

## Dependency

- A bluetooth.

## Examples

To run this test, add this into test list:

```default
{
  "pytest_name": "bluetooth_host",
}
```

## Test Arguments

| Name                 | Type      | Description                                                                                                                                                                                 |
|----------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| max_retry_times      | int       | (optional; default: `3`) The maximum number attempts to retry scanning or pairing before failure.                                                                                           |
| enable_pair          | bool      | (optional; default: `False`) Set to True to enable pairing test.                                                                                                                            |
| pre_command          | str, None | (optional; default: `None`) Command to be run before executing the test.  For example, this could be used to initialize Bluetooth module on the DUT.  Does not check output of the command. |
| post_command         | str, None | (optional; default: `None`) Command to be run after executing the test.  For example, this could be used to unload a Bluetooth module on the DUT.  Does not check output of the command.    |
| host_hci_device      | str, None | (optional; default: `None`) The target hci device of the host station. Set to None to bindon all interfaces, or set to “hci0” to bind only on specifiedinterfaces.                          |
| dut_hci_device       | str       | (optional; default: `'hci0'`) The target hci device of the DUT.                                                                                                                             |
| dut_hci_num_response | int, None | (optional; default: `None`) Maximum number of inquiry responses for scanning.                                                                                                               |
