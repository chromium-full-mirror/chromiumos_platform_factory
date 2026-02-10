# generic_camera

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## Camera

This test object cannot be run directly. User have to inherit and modify it.

### pytest_name

[camera](../pytests/camera.md)

## CameraManual

This test object cannot be run directly. User have to inherit and modify it.

### pytest_name

[camera](../pytests/camera.md)

### args

`mode`
: ```default
  "manual"
  ```

## CameraNoCharacteristics

This is used if camera_characteristics.conf is not ready. Users must replace \`\`camera_usb_vid_pid\`\` with vid pid they are testing.

### pytest_name

[camera](../pytests/camera.md)

### args

`mode`
: ```default
  "manual"
  ```

`e2e_mode`
: ```default
  false
  ```

`camera_facing`
: ```default
  null
  ```

`camera_usb_vid_pid`
: ```default
  [
    "13d3",
    "56ec"
  ]
  ```

## FrontCamera

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

## FrontCameraAssemble

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
  0.5
  ```

## FrontCameraAssembleQR

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
  "camera_assemble_qr"
  ```

`min_luminance_ratio`
: ```default
  0.5
  ```

`QR_string`
: ```default
  "ChromeTeam"
  ```

## FrontCameraFace

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
  "face"
  ```

## FrontCameraLED

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
  "manual_led"
  ```

## FrontCameraManual

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
  "ChromeTeam"
  ```

`timeout_secs`
: ```default
  2000
  ```

## ProbeCamera

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

## QRScan

Deprecated. Use FrontCameraQRScan or RearCameraQRScan.

### pytest_name

[camera](../pytests/camera.md)

### args

`mode`
: ```default
  "qr"
  ```

`QR_string`
: ```default
  "Hello ChromeOS!"
  ```

## RearCamera

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

## RearCameraAssemble

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
  "camera_assemble"
  ```

`min_luminance_ratio`
: ```default
  0.5
  ```

## RearCameraAssembleQR

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
  "camera_assemble_qr"
  ```

`min_luminance_ratio`
: ```default
  0.5
  ```

`QR_string`
: ```default
  "ChromeTeam"
  ```

## RearCameraFace

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
  "face"
  ```

## RearCameraLED

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
  "manual_led"
  ```

## RearCameraManual

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
  "ChromeTeam"
  ```

`timeout_secs`
: ```default
  2000
  ```

## CameraTests

### Serial subtests

- [FrontCamera]()
- [FrontCameraLED]()
- [RearCamera]()
- [RearCameraLED]()
