# removable_storage

**Source code:** [removable_storage.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/removable_storage.py)

Tests accessing to a removable storage.

## Description

Perform following tests on a removable storage device:
1. Random read/write test
2. Sequential read/write test
3. Lock (write protection) test

## Test Procedure

1. Insert device (with lock switch off if there’s a one)
2. Read/write test should now start. Wait for completion.
3. Remove the device

If perform_locktest is set, continue these steps:
4. Insert device with lock switch is on
5. Lock test should now start. Wait for completion.
6. Remove the device

If skip_insert_remove is set, the device should be inserted
before running this test, and the above steps 1,3,4,6 should
be skipped.

## Dependency

1. Use udev to monitor media insertion.
2. Use parted to initialize partitions on SD cards.
3. Use dd to perform read/write test.
4. Use blockdev to get block size and RO status.
5. Use ectool to check USB polarity.

## Examples

To do a random read/write test on 3 blocks (each for 1024 bytes) on an USB
stick, add this in test list:

```default
{
  "pytest_name": "removable_storage",
  "args": {
    "media": "USB",
    "sysfs_path": "/sys/devices/s5p-ehci/usb1/1-1/1-1:1.0"
  }
}
```

To do a sequential read/write test on another USB port:

```default
{
  "pytest_name": "removable_storage",
  "args": {
    "media": "USB",
    "sysfs_path": "/sys/devices/s5p-ehci/usb1/1-2/1-2.3",
    "perform_sequential_test": true,
    "sequential_block_count": 8,
    "block_size": 524288,
    "perform_random_test": false
  }
}
```

Similarly, to test a SD card:

```default
{
  "pytest_name": "removable_storage",
  "args": {
    "media": "SD",
    "sysfs_path": "/path/to/sd/device",
    "perform_sequential_test": true,
    "sequential_block_count": 8,
    "block_size": 524288,
    "perform_random_test": false
  }
}
```

If this test can not properly find the device with a specific sysfs_path, try:

- Replace sysfs_path with its real path which comes from realpath command.
  For example:
  ```default
  (on DUT)
  $ realpath -m /sys/bus/usb/devices/usb1/1-1/1-1.1
  > /sys/devices/platform/soc/11201000.usb/11200000.xhci/usb1/1-1/1-1.1
  ```
- Run udevadm monitor on DUT, plug / unplug USB devices and use paths
  shown on the screen.  For example:
  ```default
  (on DUT)
  $ udevadm monitor

  (plug USB disk in)
  ...
  > UDEV  [20949.971277] add       /devices/platform/soc/11201000.usb/11200000.xhci/usb1/1-1/1-1.1 (usb)
  ...
  ```

> Notice that the path above is not actually a full real path.  Please add
> “/sys” as prefix to get the full path.

## Test Arguments

| Name                       | Type                  | Description                                                                                                                                                                                                                                                                                                                                                       |
|----------------------------|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| media                      | [‘NVME’, ‘SD’, ‘USB’] | Media type. This is used for several logging messages, and to decide the iconsshown on UI.                                                                                                                                                                                                                                                                        |
| sysfs_path                 | str, None             | (optional; default: `None`) The expected sysfs path that udev events should come from, ex: /sys/devices/pci0000:00/0000:00:1a.0/usb1/1-1/1-1.2                                                                                                                                                                                                                    |
| block_size                 | int                   | (optional; default: `1024`) Size of each block in bytes used in read / write test                                                                                                                                                                                                                                                                                 |
| perform_random_test        | bool                  | (optional; default: `True`) Whether to run random read / write test                                                                                                                                                                                                                                                                                               |
| random_read_threshold      | int, float, None      | (optional; default: `None`) The lowest random read rate the device should achieve                                                                                                                                                                                                                                                                                 |
| random_write_threshold     | int, float, None      | (optional; default: `None`) The lowest random write rate the device should achieve                                                                                                                                                                                                                                                                                |
| random_block_count         | int                   | (optional; default: `3`) Number of blocks to test during random read / write test                                                                                                                                                                                                                                                                                 |
| perform_sequential_test    | bool                  | (optional; default: `False`) Whether to run sequential read / write tes                                                                                                                                                                                                                                                                                           |
| sequential_read_threshold  | int, float, None      | (optional; default: `None`) The lowest sequential read rate the device should achieve                                                                                                                                                                                                                                                                             |
| sequential_write_threshold | int, float, None      | (optional; default: `None`) The lowest sequential write rate the device should achieve                                                                                                                                                                                                                                                                            |
| sequential_block_count     | int                   | (optional; default: `1024`) Number of blocks to test in sequential read / write test                                                                                                                                                                                                                                                                              |
| perform_locktest           | bool                  | (optional; default: `False`) Whether to run lock test                                                                                                                                                                                                                                                                                                             |
| timeout_secs               | int                   | (optional; default: `20`) Timeout in seconds for the test to wait before it fails                                                                                                                                                                                                                                                                                 |
| detect_timeout_secs        | int                   | (optional; default: `5`) Timeout in seconds for the removable storage to be detected                                                                                                                                                                                                                                                                              |
| bft_fixture                | dict, None            | (optional; default: `None`) A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| skip_insert_remove         | bool                  | (optional; default: `False`) Skip the step of device insertion and removal                                                                                                                                                                                                                                                                                        |
| bft_media_device           | str, None             | (optional; default: `None`) Device name of BFT used to insert/remove the media.                                                                                                                                                                                                                                                                                   |
| usbpd_port_polarity        | list, None            | (optional; default: `None`) Two integers [port, polarity]                                                                                                                                                                                                                                                                                                         |
| fail_check_polarity        | bool                  | (optional; default: `False`) If set to True or skip_insert_remove is True, would fail the test directly when polarity is wrong. Otherwise, will prompt operator to flip the storage.                                                                                                                                                                              |
| create_partition           | bool, None            | (optional; default: `None`) Try to create a small partition on the media. This is to check if all the pins on the sd card reader module are intact. If not specify, this test will be run for SD card.                                                                                                                                                            |
| use_busybox_dd             | bool                  | (optional; default: `False`) Use busybox dd. This option can be removed when toybox dd is ready.                                                                                                                                                                                                                                                                  |
| expected_max_speed         | int, None             | (optional; default: `None`) The expected max speed of the device in Mpbs.480, 5000, 10000 for USB2, USB3.1 gen1, USB3.1 gen2                                                                                                                                                                                                                                      |
| extra_prompt               | str, dict             | (optional; default: `''`) An extra prompt, e.g., to specify which USB port to use                                                                                                                                                                                                                                                                                 |
