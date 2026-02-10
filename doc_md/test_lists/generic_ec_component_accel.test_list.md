# generic_ec_component_accel

Predefined ec_component_accel tests. ec_component_accel is called “Accelerometer/IMU” in AVL.

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## Accelerometers

### pytest_name

[accelerometers](../pytests/accelerometers.md)

## AccelerometersCalibration

### pytest_name

[accelerometers_calibration](../pytests/accelerometers_calibration.md)

### args

`orientation`
: ```default
  {
    "in_accel_x": 0,
    "in_accel_y": 0,
    "in_accel_z": 1
  }
  ```

`spec_offset`
: ```default
  [
    0.5,
    0.5
  ]
  ```

## AccelerometersLidAngle

### run_if

```default
not constants.has_device_data or (device.component.has_lid_accelerometer and device.component.has_base_accelerometer)
```

### pytest_name

[accelerometers_lid_angle](../pytests/accelerometers_lid_angle.md)

### args

`angle`
: ```default
  180
  ```

`tolerance`
: ```default
  5
  ```

`spec_offset`
: ```default
  [
    0.5,
    0.5
  ]
  ```

## BaseAccelerometers

### run_if

```default
not constants.has_device_data or device.component.has_base_accelerometer
```

### pytest_name

[accelerometers](../pytests/accelerometers.md)

### args

`location`
: ```default
  "base"
  ```

## BaseAccelerometersCalibration

### run_if

```default
not constants.has_device_data or device.component.has_base_accelerometer
```

### pytest_name

[accelerometers_calibration](../pytests/accelerometers_calibration.md)

### args

`orientation`
: ```default
  {
    "in_accel_x": 0,
    "in_accel_y": 0,
    "in_accel_z": 1
  }
  ```

`spec_offset`
: ```default
  [
    0.5,
    0.5
  ]
  ```

`location`
: ```default
  "base"
  ```

## Gyroscope

### run_if

```default
not constants.has_device_data or device.component.has_base_gyroscope
```

### pytest_name

[gyroscope](../pytests/gyroscope.md)

### args

`rotation_threshold`
: ```default
  1.0
  ```

`stop_threshold`
: ```default
  0.1
  ```

## GyroscopeAngle

### run_if

```default
not constants.has_device_data or device.component.has_base_gyroscope
```

### pytest_name

[gyroscope_angle](../pytests/gyroscope_angle.md)

### args

`rotation_threshold`
: ```default
  90
  ```

`stop_threshold`
: ```default
  0.1
  ```

## GyroscopeCalibration

### run_if

```default
not constants.has_device_data or device.component.has_base_gyroscope
```

### pytest_name

[gyroscope_calibration](../pytests/gyroscope_calibration.md)

## LidAccelerometers

### run_if

```default
not constants.has_device_data or device.component.has_lid_accelerometer
```

### pytest_name

[accelerometers](../pytests/accelerometers.md)

### args

`location`
: ```default
  "lid"
  ```

## LidAccelerometersCalibration

### run_if

```default
not constants.has_device_data or device.component.has_lid_accelerometer
```

### pytest_name

[accelerometers_calibration](../pytests/accelerometers_calibration.md)

### args

`orientation`
: ```default
  {
    "in_accel_x": 0,
    "in_accel_y": 0,
    "in_accel_z": 1
  }
  ```

`spec_offset`
: ```default
  [
    0.5,
    0.5
  ]
  ```

`location`
: ```default
  "lid"
  ```

## NotebookMode

### run_if

```default
not constants.has_device_data or device.component.has_tabletmode
```

### pytest_name

[tablet_mode](../pytests/tablet_mode.md)

### args

`timeout_secs`
: ```default
  3600
  ```

`prompt_flip_tablet`
: ```default
  false
  ```

`prompt_flip_notebook`
: ```default
  true
  ```

`lid_filter`
: ```default
  "cros_ec_buttons"
  ```

## TabletMode

### run_if

```default
not constants.has_device_data or device.component.has_tabletmode
```

### pytest_name

[tablet_mode](../pytests/tablet_mode.md)

### args

`timeout_secs`
: ```default
  3600
  ```

`prompt_flip_tablet`
: ```default
  true
  ```

`prompt_flip_notebook`
: ```default
  false
  ```

`lid_filter`
: ```default
  "cros_ec_buttons"
  ```

## TabletRotation

### pytest_name

[tablet_rotation](../pytests/tablet_rotation.md)

### args

`spec_offset`
: ```default
  [
    1.5,
    1.5
  ]
  ```

`timeout_secs`
: ```default
  3600
  ```

## TabletRotationAll

### run_if

```default
not constants.has_device_data or (device.component.has_base_accelerometer and device.component.has_lid_accelerometer)
```

### pytest_name

[tablet_rotation](../pytests/tablet_rotation.md)

### args

`spec_offset`
: ```default
  [
    1.5,
    1.5
  ]
  ```

`timeout_secs`
: ```default
  3600
  ```

`degrees_to_orientations`
: ```default
  {
    "base": {
      "0": {
        "in_accel_x": 0,
        "in_accel_y": -1,
        "in_accel_z": 0
      },
      "180": {
        "in_accel_x": 0,
        "in_accel_y": 1,
        "in_accel_z": 0
      },
      "270": {
        "in_accel_x": -1,
        "in_accel_y": 0,
        "in_accel_z": 0
      },
      "90": {
        "in_accel_x": 1,
        "in_accel_y": 0,
        "in_accel_z": 0
      }
    },
    "lid": {
      "0": {
        "in_accel_x": 0,
        "in_accel_y": 1,
        "in_accel_z": 0
      },
      "180": {
        "in_accel_x": 0,
        "in_accel_y": -1,
        "in_accel_z": 0
      },
      "270": {
        "in_accel_x": -1,
        "in_accel_y": 0,
        "in_accel_z": 0
      },
      "90": {
        "in_accel_x": 1,
        "in_accel_y": 0,
        "in_accel_z": 0
      }
    }
  }
  ```

## TabletRotationBase

### run_if

```default
constants.has_device_data and device.component.has_base_accelerometer and not device.component.has_lid_accelerometer
```

### pytest_name

[tablet_rotation](../pytests/tablet_rotation.md)

### args

`spec_offset`
: ```default
  [
    1.5,
    1.5
  ]
  ```

`timeout_secs`
: ```default
  3600
  ```

`degrees_to_orientations`
: ```default
  {
    "base": {
      "0": {
        "in_accel_x": 0,
        "in_accel_y": -1,
        "in_accel_z": 0
      },
      "180": {
        "in_accel_x": 0,
        "in_accel_y": 1,
        "in_accel_z": 0
      },
      "270": {
        "in_accel_x": -1,
        "in_accel_y": 0,
        "in_accel_z": 0
      },
      "90": {
        "in_accel_x": 1,
        "in_accel_y": 0,
        "in_accel_z": 0
      }
    }
  }
  ```

## TabletRotationLid

### run_if

```default
constants.has_device_data and not device.component.has_base_accelerometer and device.component.has_lid_accelerometer
```

### pytest_name

[tablet_rotation](../pytests/tablet_rotation.md)

### args

`spec_offset`
: ```default
  [
    1.5,
    1.5
  ]
  ```

`timeout_secs`
: ```default
  3600
  ```

`degrees_to_orientations`
: ```default
  {
    "lid": {
      "0": {
        "in_accel_x": 0,
        "in_accel_y": 1,
        "in_accel_z": 0
      },
      "180": {
        "in_accel_x": 0,
        "in_accel_y": -1,
        "in_accel_z": 0
      },
      "270": {
        "in_accel_x": -1,
        "in_accel_y": 0,
        "in_accel_z": 0
      },
      "90": {
        "in_accel_x": 1,
        "in_accel_y": 0,
        "in_accel_z": 0
      }
    }
  }
  ```

## ScreenRotation

### run_if

```default
not constants.has_device_data or device.component.has_tabletmode
```

### Serial subtests

- [TabletMode]()
- [TabletRotationAll]()
- [TabletRotationBase]()
- [TabletRotationLid]()
- [NotebookMode]()
