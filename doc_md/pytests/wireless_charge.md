# wireless_charge

**Source code:** [wireless_charge.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/wireless_charge.py)

Test wireless charge port functionality.

## Description

Verify wireless charging port functionality by asking operator to follow the
instructions by occupy/free charging port then probe the port status.

## Test Procedure

1. Show instruction on screen and instruct operator to occupy port with
   peripheral, then press SPACE to probe state.
2. Show instruction on screen and instruct operator to free port with
   peripheral, then press SPACE to probe state.

## Dependency

- Based on ectool pchg <port>

## Examples

To test charging port 0:

```default
{
  "pytest_name": "wireless_charge",
  "args": {
    "port": 0,
    "occupy_instruction": "Attach stylus on the DUT right side",
    "release_instruction": "Remove stylus from the DUT right side"
  }
}
```

## Test Arguments

| Name                | Type      | Description                                                                                                               |
|---------------------|-----------|---------------------------------------------------------------------------------------------------------------------------|
| port                | int       | (optional; default: `0`) Wireless charging port to test.                                                                  |
| occupy_instruction  | str, dict | (optional; default: `'Attach peripheral to charging port'`) Text to display the instruction to operator to occupy port    |
| release_instruction | str, dict | (optional; default: `'Remove peripheral from charging port'`) Text to display the instruction to operator to release port |
| timeout             | int       | (optional; default: `200`) Timeout of the test.                                                                           |
