# generic_camera_examples

## Inherit

- [generic_camera.test_list](generic_camera.test_list.md)

## FrontCameraAssemble07

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`mode`
: ```default
  "camera_assemble"
  ```

`min_luminance_ratio`
: ```default
  0.7
  ```

## FrontCameraBrightness

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`num_frames_to_pass`
: ```default
  5
  ```

`mode`
: ```default
  "brightness"
  ```

`timeout_secs`
: ```default
  3
  ```

`brightness_range`
: ```default
  [
    null,
    10
  ]
  ```

## FrontCameraFrames

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`num_frames_to_pass`
: ```default
  100
  ```

`mode`
: ```default
  "frame_count"
  ```

`timeout_secs`
: ```default
  1000
  ```

`show_image`
: ```default
  false
  ```

## FrontCameraManualOpenCV

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`mode`
: ```default
  "manual"
  ```

`e2e_mode`
: ```default
  false
  ```

## FrontCameraQRScan

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`mode`
: ```default
  "qr"
  ```

`QR_string`
: ```default
  "Hello ChromeOS!"
  ```

`timeout_secs`
: ```default
  2000
  ```

## FrontCameraQRScan1920x1080

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`mode`
: ```default
  "qr"
  ```

`QR_string`
: ```default
  "Hello ChromeOS!"
  ```

`timeout_secs`
: ```default
  2000
  ```

`camera_args`
: ```default
  {
    "resolution": [
      1920,
      1080
    ]
  }
  ```

## FrontCameraStress

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`mode`
: ```default
  "timeout"
  ```

`timeout_secs`
: ```default
  1000
  ```

`show_image`
: ```default
  false
  ```

## ProbeOneCamera

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "camera"
  ]
  ```

`config_file`
: ```default
  "/usr/local/factory/py/hwid/v3/default_probe_statement.json"
  ```

`overridden_rules`
: ```default
  [
    [
      "camera",
      "==",
      1
    ]
  ]
  ```

## ProbeTwoCameras

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "camera"
  ]
  ```

`config_file`
: ```default
  "/usr/local/factory/py/hwid/v3/default_probe_statement.json"
  ```

`overridden_rules`
: ```default
  [
    [
      "camera",
      "==",
      2
    ]
  ]
  ```

## RearCameraManualOpenCV

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_rear_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "rear"
  ```

`mode`
: ```default
  "manual"
  ```

`e2e_mode`
: ```default
  false
  ```

## RearCameraQRScan

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_rear_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "rear"
  ```

`mode`
: ```default
  "qr"
  ```

`QR_string`
: ```default
  "Hello ChromeOS!"
  ```

`timeout_secs`
: ```default
  2000
  ```

## RearCameraStress

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_rear_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "rear"
  ```

`mode`
: ```default
  "timeout"
  ```

`timeout_secs`
: ```default
  1000
  ```

`show_image`
: ```default
  false
  ```

## SetHasFrontCamera

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_front_camera=1"
  ```

## SetHasRearCamera

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_rear_camera=1"
  ```

## UnsetHasFrontCamera

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_front_camera=0"
  ```

## UnsetHasRearCamera

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_rear_camera=0"
  ```

## CameraTests

### Serial subtests

- [SetHasFrontCamera]()
- [SetHasRearCamera]()
- [ProbeOneCamera]()
- FrontCameraFace
- FrontCameraLED
- FrontCameraManual
- [FrontCameraManualOpenCV]()
- [FrontCameraQRScan]()
- [FrontCameraQRScan1920x1080]()
- [FrontCameraStress]()
- [FrontCameraFrames]()
- FrontCameraAssemble
- FrontCameraAssembleQR
- [FrontCameraAssemble07]()
- [FrontCameraBrightness]()
- CameraNoCharacteristics
- [ProbeTwoCameras]()
- RearCameraFace
- RearCameraLED
- RearCameraManual
- [RearCameraManualOpenCV]()
- [RearCameraQRScan]()
- RearCameraAssemble
- RearCameraAssembleQR
- [RearCameraStress]()
- [UnsetHasFrontCamera]()
- [UnsetHasRearCamera]()
