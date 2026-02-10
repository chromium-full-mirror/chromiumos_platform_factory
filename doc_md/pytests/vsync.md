# vsync

**Source code:** [vsync.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/vsync.py)

VSync pin test.

## Description

This pytest test if VSync pin is connected to EC and camera can receive VSync
signal.

### Internal References

- [b/146452722](http://b/146452722)
- [2021-2H_rfp_announcement](https://chromeos.google.com/partner/dlm/docs/device-rfp/2021-2H_rfp_announcement.html)

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- Yet Another V4L2 Test Application (`yavta`)

## Examples

To run a VSync pin test, add this in test list:

```default
{
  "pytest_name": "vsync"
}
```

## Test Arguments

| Name           | Type                    | Description                                                                                                                                                |
|----------------|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| capture_number | int                     | (optional; default: `10`) The number of capture frames.                                                                                                    |
| camera_facing  | [‘front’, ‘rear’], None | (optional; default: `None`) Direction the camera faces relative to device screen. Only allow “front”, “rear” or None. None is automatically searching one. |
| timeout_secs   | int                     | (optional; default: `60`) Timeout in seconds when waiting for device.                                                                                      |
| repeat_times   | int                     | (optional; default: `5`) Number of cycles to test.                                                                                                         |
