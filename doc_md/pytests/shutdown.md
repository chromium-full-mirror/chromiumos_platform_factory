# shutdown

**Source code:** [shutdown.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/shutdown.py)

Shutdown/Reboot the device.

## Description

This test halts or reboots the device.
This test provides three types of shutdown: reboot, full reboot, and direct EC
reboot. A reboot is leveraging the external binary ‘shutdown’ for rebooting, a
full reboot halts the device, then trigger a ec reboot, and a direct EC reboot
triggers a hard reset directly.

A direct EC reboot is suggested if in developmental phase, a firmware update is
triggered when system is powered on, which might cause a normal reboot fail.

## Test Procedure

If argument check_gpt is set to True (default), it checks if partitions are
good for the next boot. Then, it reboots / halts the device according to the
argument operation.

## Dependency

* If DUT is a remote device, and argument check_gpt is set to True( default),
  it depends on the external binary ‘cgpt’ or ‘partx’ to read GPT info.
* Depends on the external binary ‘shutdown’ to perform the operation.
* Depends on the external binary ‘ectool’ to perform a full reboot and a direct
  EC reboot.

## Examples

To reboot the device after a 5-second delay, add this in test list:

```default
{
  "pytest_name": "shutdown",
  "args": {
    "operation": "reboot"
  }
}
```

This also checks the GPT info to ensure partitions look good for the next boot.

To shutdown the device with a maximum 60-second waiting:

```default
{
  "pytest_name": "shutdown",
  "args": {
    "operation": "halt"
  }
}
```

## Test Arguments

| Name                 | Type                                                  | Description                                                                                                                                |
|----------------------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| operation            | [‘direct_ec_reboot’, ‘full_reboot’, ‘halt’, ‘reboot’] | The command to run to perform the shutdown (‘reboot’, ‘full_reboot’, ‘halt’, or ‘direct_ec_reboot’).                                       |
| delay_secs           | int                                                   | (optional; default: `5`) Number of seconds the operator has to abort the shutdown.                                                         |
| max_reboot_time_secs | int                                                   | (optional; default: `180`) Maximum amount of time allowed between reboots. If this threshold is exceeded, the reboot is considered failed. |
| wait_shutdown_secs   | int                                                   | (optional; default: `60`) Number of seconds to wait for system shutdown.                                                                   |
| check_tag_file       | bool                                                  | (optional; default: `False`) Checks shutdown failure tag file                                                                              |
| check_audio_devices  | int, None                                             | (optional; default: `None`) Check total number of audio devices. None for non-check.                                                       |
| check_gpt            | bool                                                  | (optional; default: `True`) Check GPT info before shutdown/reboot.                                                                         |
| warmup_post_shutdown | int                                                   | (optional; default: `0`) Number of seconds to wait after reboot for warming up the system                                                  |
