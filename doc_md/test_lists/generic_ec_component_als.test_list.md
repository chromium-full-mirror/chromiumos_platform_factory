# generic_ec_component_als

Predefined ec_component_als tests. ec_component_als is called “Ambient Light Sensor” in AVL.

## Inherit

- [base.test_list](base.test_list.md)

## LightSensor

### pytest_name

[light_sensor](../pytests/light_sensor.md)

### args

`device_name`
: ```default
  "eval! constants.light_sensor_name"
  ```

`subtest_cfg`
: ```default
  {
    "Light sensor dark": {
      "below": 30
    },
    "Light sensor exact": {
      "between": [
        60,
        300
      ]
    },
    "Light sensor light": {
      "above": 500
    }
  }
  ```

`subtest_instruction`
: ```default
  {
    "Light sensor dark": "i18n! Cover light sensor with finger",
    "Light sensor exact": "i18n! Remove finger from light sensor",
    "Light sensor light": "i18n! Shine light sensor with flashlight"
  }
  ```

`subtest_list`
: ```default
  [
    "Light sensor dark",
    "Light sensor exact",
    "Light sensor light"
  ]
  ```

`timeout_per_subtest`
: ```default
  20
  ```

## LightSensorCalibration

### pytest_name

[light_sensor_calibration](../pytests/light_sensor_calibration.md)

### args

`control_chamber`
: ```default
  true
  ```

`assume_chamber_connected`
: ```default
  true
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
