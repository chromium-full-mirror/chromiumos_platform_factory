# update_kernel

**Source code:** [update_kernel.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/update_kernel.py)

Applies new kernel to DUT (for testing).

## Description

This test helps replacing kernel on DUT.

Sometimes in early builds, we do need to update kernel on DUT for enabling extra
drivers, bug fixes, or few workarounds.  Sometimes we may want to enable or
disable few kernel command line arguments.

Another case is to allow finalizing with a DEV signed firmware (due to last
minute changes in manufacturing line and no time to wait for a signed complete
release), we have to re-sign release image kernel with DEV keys (see
[http://go/cros-factory-fw-in-early-builds](http://go/cros-factory-fw-in-early-builds) for more details).

All these leads to the demand of updating kernel on DUT, with the ability to
resign or changing kernel command line, and that’s all supported by this test.

## Test Procedure

This is an automated test without user interaction.

After started, the test will replace kernel on device partition by given
arguments.

## Dependency

- The DUT must be running Chrome OS image.
- `flashrom` and `gooftool` are needed if argument `to_release` is True.
- `futility` is needed if argument `kernel_config` is set.

## Examples

To replace the kernel on TEST image partition and keep old kernel command line:

```default
{
  "pytest_name": "update_kernel",
  "args": {
    "kernel_image": "/usr/local/factory/board/test_kernel.bin"
  }
}
```

To re-sign kernel on RELEASE image partition with DEV key:

```default
{
  "pytest_name": "update_kernel",
  "args": {
    "to_release": true
  }
}
```

To change kernel command line of the kernel on TEST image partition:

```default
{
  "pytest_name": "update_kernel",
  "args": {
    "kernel_config": "/usr/local/factory/board/test_kernel.cmdline"
  }
}
```

## Test Arguments

| Name          | Type      | Description                                                                                                  |
|---------------|-----------|--------------------------------------------------------------------------------------------------------------|
| kernel_image  | str, None | (optional; default: `None`) Full path of kernel.bin                                                          |
| kernel_config | str, None | (optional; default: `None`) Path to a file containing kernel command line.                                   |
| to_release    | bool      | (optional; default: `False`) Set to True to update on release partition, otherwise update on test partition. |
