# webgl_aquarium

**Source code:** [webgl_aquarium.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/webgl_aquarium.py)

WebGL performance test that executes a set of WebGL operations.

## Description

The test runs the WebGL aquarium test for testing the 3D hardware-accelerated
JavaScript API ‘WebGL’, and get FPS value from frontend for checking.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.
Just set the argument before start, and wait for the completion.
It runs the WebGL aquarium test, and fail if the moving average FPS value
less than ‘min_fps’ while testing.

## Dependency

None.

## Examples

To disable the performance restriction, add this in test list:

```default
{
  "pytest_name": "webgl_aquarium",
  "args": {
    "min_fps": 0
  }
}
```

To sample and check FPS more frequently with higher standard for FPS,
add this in test list:

```default
{
  "pytest_name": "webgl_aquarium",
  "args": {
    "min_fps": 30,
    "fps_sample_interval": 0.5,
    "fps_check_interval": 3
  }
}
```

## Test Arguments

| Name                | Type   | Description                                                                                                                                                                                                                                                                                                               |
|---------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| duration_secs       | int    | (optional; default: `60`) Duration of time in seconds to run the test                                                                                                                                                                                                                                                     |
| num_fish            | int    | (optional; default: `50`) Number of fishes. Must be one of [1, 10, 50, 100, 250, 500, 1000]                                                                                                                                                                                                                               |
| hide_options        | bool   | (optional; default: `True`) Whether to hide the options on UI                                                                                                                                                                                                                                                             |
| full_screen         | bool   | (optional; default: `True`) Whether to go full screen mode by default                                                                                                                                                                                                                                                     |
| min_fps             | int    | (optional; default: `10`) Minimum moving average FPS to pass the test, if the moving average FPS is lower than it, the test will fail.The default value of it is set to 10 for warning that FPS is low.You can set it to 0 if FPS does not matter at all, or set it to a higher value for strict performance requirement. |
| fps_sample_interval | float  | (optional; default: `1.0`) Period of FPS sampling in seconds                                                                                                                                                                                                                                                              |
| fps_log_interval    | int    | (optional; default: `60`) Period of FPS logging in seconds                                                                                                                                                                                                                                                                |
| fps_check_interval  | int    | (optional; default: `10`) Period of FPS checking in seconds                                                                                                                                                                                                                                                               |
| fps_window_size     | int    | (optional; default: `10`) Number of FPS samples in window for calculating moving average FPS                                                                                                                                                                                                                              |
