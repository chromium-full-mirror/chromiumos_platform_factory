# probe_sim_card_tray

**Source code:** [probe_sim_card_tray.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/probe_sim_card_tray.py)

Probes SIM card tray

## Description

Detects SIM card tray by GPIO.

## Test Procedure

1. Insert sim card.
2. The test checks the GPIO automatically.
3. Remove sim card.
4. The test checks the GPIO automatically.

or

1. Remove sim card.
2. The test checks the GPIO automatically.
3. Insert sim card.
4. The test checks the GPIO automatically.

## Dependency

- /sys/class/gpio

## Examples

Just check presence:

```default
{
  "pytest_name": "probe_sim_card_tray",
  "args": {
    "tray_detection_gpio": 159,
    "tray_already_present": true
  }
}
```

Ask user to insert then remove tray:

```default
{
  "pytest_name": "probe_sim_card_tray",
  "args": {
    "tray_detection_gpio": 159,
    "tray_already_present": false,
    "insert": true,
    "remove": true,
    "only_check_presence": false
  }
}
```

Ask user to remove then insert tray:

```default
{
  "pytest_name": "probe_sim_card_tray",
  "args": {
    "tray_detection_gpio": 159,
    "tray_already_present": true,
    "insert": true,
    "remove": true,
    "only_check_presence": false
  }
}
```

## Test Arguments

| Name                 | Type   | Description                                                                                                               |
|----------------------|--------|---------------------------------------------------------------------------------------------------------------------------|
| timeout_secs         | int    | (optional; default: `10`) timeout in seconds for insertion/removal                                                        |
| tray_already_present | bool   | (optional; default: `False`) SIM card tray is in machine before test starts                                               |
| tray_detection_gpio  | int    | (optional; default: `159`) SIM card tray detection gpio number                                                            |
| insert               | bool   | (optional; default: `False`) Check sim card tray insertion                                                                |
| remove               | bool   | (optional; default: `False`) Check sim card tray removal                                                                  |
| only_check_presence  | bool   | (optional; default: `True`) Only checks sim card tray presence matches tray_already_present. No user interaction required |
| gpio_active_high     | bool   | (optional; default: `True`) Whether GPIO is active high.                                                                  |
