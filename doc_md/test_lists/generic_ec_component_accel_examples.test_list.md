# generic_ec_component_accel_examples

Examples for testing ec_component_accel components. ec_component_accel is called “Accelerometer/IMU” in AVL.

## Inherit

- [generic_ec_component_accel.test_list](generic_ec_component_accel.test_list.md)

## BaseAccelerometersCalibrationByEC

### run_if

```default
not constants.has_device_data or device.component.has_base_accelerometer
```

### pytest_name

[spatial_sensor_calibration](../pytests/spatial_sensor_calibration.md)

### args

`device_name`
: ```default
  "cros-ec-accel"
  ```

`device_location`
: ```default
  "base"
  ```

`raw_entry_template`
: ```default
  "in_accel_%s_raw"
  ```

`calibbias_entry_template`
: ```default
  "in_accel_%s_calibbias"
  ```

`vpd_entry_template`
: ```default
  "in_accel_%s_base_calibbias"
  ```

## BaseAccelerometersLooserLimits

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

`limits`
: ```default
  {
    "x": [
      -1.0,
      1.0
    ],
    "y": [
      -1.0,
      1.0
    ],
    "z": [
      8.0,
      11.0
    ]
  }
  ```

## GoToTabletModeAndGoBack

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
  true
  ```

`lid_filter`
: ```default
  "cros_ec_buttons"
  ```

## GoToTabletModeAndGoBackSetLid

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
  true
  ```

`lid_filter`
: ```default
  "Lid Switch"
  ```

## GyroscopeCalibrationByEC

### run_if

```default
not constants.has_device_data or device.component.has_base_gyroscope
```

### pytest_name

[spatial_sensor_calibration](../pytests/spatial_sensor_calibration.md)

### args

`device_name`
: ```default
  "cros-ec-gyro"
  ```

`device_location`
: ```default
  "base"
  ```

`raw_entry_template`
: ```default
  "in_anglvel_%s_raw"
  ```

`calibbias_entry_template`
: ```default
  "in_anglvel_%s_calibbias"
  ```

`vpd_entry_template`
: ```default
  "in_anglvel_%s_base_calibbias"
  ```

## LidAccelerometersCalibrationByEC

### run_if

```default
not constants.has_device_data or device.component.has_lid_accelerometer
```

### pytest_name

[spatial_sensor_calibration](../pytests/spatial_sensor_calibration.md)

### args

`device_name`
: ```default
  "cros-ec-accel"
  ```

`device_location`
: ```default
  "lid"
  ```

`raw_entry_template`
: ```default
  "in_accel_%s_raw"
  ```

`calibbias_entry_template`
: ```default
  "in_accel_%s_calibbias"
  ```

`vpd_entry_template`
: ```default
  "in_accel_%s_lid_calibbias"
  ```

## SetHasBaseAccelerometer

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_base_accelerometer=1"
  ```

## SetHasBaseGyroscope

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_base_gyroscope=1"
  ```

## SetHasLidAccelerometer

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_lid_accelerometer=1"
  ```

## SetHasTabletmode

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_tabletmode=1"
  ```

## TabletRotationBase

### run_if

```default
constants.has_device_data and device.component.has_base_accelerometer
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
constants.has_device_data and device.component.has_lid_accelerometer
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

## UnsetHasBaseAccelerometer

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_base_accelerometer=0"
  ```

## UnsetHasBaseGyroscope

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_base_gyroscope=0"
  ```

## UnsetHasLidAccelerometer

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_lid_accelerometer=0"
  ```

## UnsetHasTabletmode

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "factory device-data component.has_tabletmode=0"
  ```

## AccelerometerIMUTests

### Serial subtests

- [SetHasBaseAccelerometer]()
- [SetHasLidAccelerometer]()
- [SetHasBaseGyroscope]()
- [SetHasTabletmode]()
- BaseAccelerometersCalibration
- [BaseAccelerometersCalibrationByEC]()
- BaseAccelerometers
- [BaseAccelerometersLooserLimits]()
- LidAccelerometersCalibration
- [LidAccelerometersCalibrationByEC]()
- LidAccelerometers
- AccelerometersLidAngle
- GyroscopeCalibration
- [GyroscopeCalibrationByEC]()
- Gyroscope
- GyroscopeAngle
- [GoToTabletModeAndGoBack]()
- [GoToTabletModeAndGoBackSetLid]()
- [ScreenRotation]()
- TabletRotation
- [UnsetHasBaseAccelerometer]()
- [UnsetHasLidAccelerometer]()
- [UnsetHasBaseGyroscope]()
- [UnsetHasTabletmode]()

## ScreenRotation

### run_if

```default
not constants.has_device_data or device.component.has_tabletmode
```

### Serial subtests

- TabletMode
- TabletRotationAll
- [TabletRotationBase]()
- [TabletRotationLid]()
- NotebookMode
