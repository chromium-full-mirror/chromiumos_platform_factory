# generic_ec_component_als_examples

Examples for testing ec_component_als components. ec_component_als is called “Ambient Light Sensor” in AVL.

## Inherit

- [generic_ec_component_als.test_list](generic_ec_component_als.test_list.md)

## LightSensorCalibrationWithMockedChamber

The test is used to test the software. You need a real chamber to do the real calibration.

### pytest_name

[light_sensor_calibration](../pytests/light_sensor_calibration.md)

### args

`control_chamber`
: ```default
  true
  ```

`assume_chamber_connected`
: ```default
  false
  ```

`chamber_cmd`
: ```default
  {
    "LUX1": [
      [
        "LUX1_ON",
        "LUX1_READY"
      ]
    ],
    "LUX2": [
      [
        "LUX2_ON",
        "LUX2_READY"
      ]
    ],
    "LUX3": [
      [
        "LUX3_ON",
        "LUX3_READY"
      ]
    ],
    "OFF": [
      [
        "OFF",
        "OFF_READY"
      ]
    ]
  }
  ```

`mock_mode`
: ```default
  true
  ```

## AmbientLightSensorTests

### Serial subtests

- LightSensor
- LightSensorCalibration
- [LightSensorCalibrationWithMockedChamber]()
