# flash_netboot

**Source code:** [flash_netboot.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/flash_netboot.py)

Flash system main (AP) firmware to netboot firmware.

## Description

Sometimes in order to re-run factory flow, or to update partitions that can’t be
updated by Chrome OS Factory Software (for example, the disk partition itself,
or release and test image rootfs), we may want to flash system firmware and
restart the process.

The flash_netboot test provides an easy way to flash netboot firmware into
system using flashrom utility, and preserving VPD sections.

Note that it doesn’t reboot after flashing firmware. Please run reboot
step after it.

## Test Procedure

This is an automated test without user interaction.

Start the test and it will reflash system firmware using specified image.

## Dependency

- Utility flashrom ([https://www.flashrom.org/](https://www.flashrom.org/)).
- System firmware is structured with FMAP.
- Chrome OS Verified Boot firmware utility ‘futility’.

## Examples

To flash netboot firmware in provided default location, add this in test list:

```default
{
  "pytest_name": "flash_netboot"
}
```

To flash netboot firmware from a special location:

```default
{
  "pytest_name": "flash_netboot",
  "args": {
    "image": "/usr/local/factory/3rdparty/netboot.bin"
  }
}
```

## Test Arguments

| Name   | Type      | Description                                                                                                       |
|--------|-----------|-------------------------------------------------------------------------------------------------------------------|
| image  | str, None | (optional; default: `None`) Path of netboot firmware image. Default to use /usr/local/factory/board/image.net.bin |
