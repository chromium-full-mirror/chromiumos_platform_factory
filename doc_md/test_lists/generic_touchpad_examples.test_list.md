# generic_touchpad_examples

Examples for testing touchpad components. Touchpad is called “Touchpad Controller” in AVL.

## Inherit

- [generic_touchpad.test_list](generic_touchpad.test_list.md)

## Touchpad100Seconds

### pytest_name

[touchpad](../pytests/touchpad.md)

### args

`timeout_secs`
: ```default
  100
  ```

## TouchpadHover

### pytest_name

[touchpad_hover](../pytests/touchpad_hover.md)

## TouchpadCalibrateAndHover

### Serial subtests

- ```default
  {
    "args": {
      "device_data_key": "component.touchpad.calibration_trigger",
      "label": "Touchpad Calibration Trigger"
    },
    "label": "Scan Touchpad Calibration Trigger",
    "pytest_name": "scan"
  }
  ```
- ```default
  {
    "args": {
      "calibration_trigger": "eval! device.component.touchpad.calibration_trigger"
    },
    "inherit": "TouchpadHover",
    "label": "Touchpad Calibrate And Hover"
  }
  ```

## TouchpadTests

### Serial subtests

- ProbeTouchpad
- Touchpad
- [Touchpad100Seconds]()
- [TouchpadCalibrateAndHover]()
- [TouchpadHover]()
