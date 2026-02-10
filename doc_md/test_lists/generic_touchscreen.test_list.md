# generic_touchscreen

Predefined touchscreen tests. touchscreen is called “Touch screen controller (EMR Stylus)”, “Touch screen Controller (non stylus)”, or “Touch screen controller (USI Stylus)” in AVL.

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## ProbeTouchscreen

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "touchscreen"
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
      "touchscreen",
      "==",
      1
    ]
  ]
  ```

## Stylus

### run_if

```default
not constants.has_device_data or device.component.has_stylus
```

### pytest_name

[stylus](../pytests/stylus.md)

## StylusGarage

### run_if

```default
not constants.has_device_data or device.component.has_stylus_garage
```

### pytest_name

[stylus_garage](../pytests/stylus_garage.md)

## Touchscreen

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touchscreen](../pytests/touchscreen.md)

## TouchscreenUniformity

Ask vendor how to calibrate touchscreen if they do not support this test

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touch_uniformity](../pytests/touch_uniformity.md)

### args

`check_list`
: ```default
  [
    [
      0,
      "i18n! References",
      23400,
      25100,
      0,
      0
    ],
    [
      1,
      "i18n! Deltas",
      -30,
      40,
      0,
      0
    ]
  ]
  ```

## StylusAndGarage

### Serial subtests

- ```default
  {
    "args": {
      "target_state": "ejected"
    },
    "inherit": "StylusGarage",
    "label": "Remove stylus"
  }
  ```
- [Stylus]()
- ```default
  {
    "args": {
      "target_state": "inserted"
    },
    "inherit": "StylusGarage",
    "label": "Insert stylus"
  }
  ```
