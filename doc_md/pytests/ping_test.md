# ping_test

**Source code:** [ping_test.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/ping_test.py)

Ping connection test.

## Description

Tests network connection by pinging a host for a period of time. Then checks
the percentage of successful pings is above some threshold or not.

If moving_window_size is set, it will check the percentage within the moving
window during the test. It always checks the percentage of successful pings for
the whole duration at the end of the test.

## Test Procedure

This is an automated test without user interaction.

## Dependency

The program `ping`.

## Examples

To ping 192.168.0.1 every 2 seconds for 10 seconds, and checks the successful
pings are >= 70% at the end of the test (The default values), add this in test
list:

```default
{
  "pytest_name": "ping_test",
  "args": {
    "host": "192.168.0.1"
  }
}
```

To ping 192.168.0.1 every 10 seconds for 120 seconds, and checks the successful
pings are >= 60% at the end of the test:

```default
{
  "pytest_name": "ping_test",
  "args": {
    "duration_secs": 120,
    "host": "192.168.0.1",
    "interval_secs": 10,
    "ping_success_percent": 60
  }
}
```

To ping 192.168.0.1 on interface eth0 every 10 seconds for 120 seconds, checks
the successful pings are >= 70% within the moving window of 5 pings, and also
checks the successful pings are >= 70% overall:

```default
{
  "pytest_name": "ping_test",
  "args": {
    "duration_secs": 120,
    "host": "192.168.0.1",
    "interface": "eth0",
    "interval_secs": 10,
    "moving_window_size": 5
  }
}
```

## Test Arguments

| Name                 | Type      | Description                                                                                                                                                                                                                  |
|----------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| host                 | str       | The IP address or hostname to ping.                                                                                                                                                                                          |
| interface            | str, None | (optional; default: `None`) Source interface address, may be numeric IP address or name of network device, ex: eth0.                                                                                                         |
| interval_secs        | int       | (optional; default: `2`) The interval in seconds between two consecutive pings.                                                                                                                                              |
| duration_secs        | int       | (optional; default: `10`) The duration of the ping test in seconds.                                                                                                                                                          |
| ping_success_percent | int       | (optional; default: `70`) The percentage of successful pings to meet.  It will be checked at the end of the test.                                                                                                            |
| moving_window_size   | int, None | (optional; default: `None`) The size of the moving window in number of ping attempts.  If it is set, the percentage of successful pings will be checked within the moving window in addition to that at the end of the test. |
| verbose              | bool      | (optional; default: `False`) Dumps stdout of ping commands.                                                                                                                                                                  |
| packet_size          | int, None | (optional; default: `None`) Specifies the number of data bytes to be sent.                                                                                                                                                   |
