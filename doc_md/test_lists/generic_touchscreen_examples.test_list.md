# generic_touchscreen_examples

Examples for testing touchscreen components. touchscreen is called “Touch screen controller (EMR Stylus)”, “Touch screen Controller (non stylus)”, or “Touch screen controller (USI Stylus)” in AVL.

## Inherit

- [generic_touchscreen.test_list](generic_touchscreen.test_list.md)

## StylusSpiralHoverMode

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touchscreen](../pytests/touchscreen.md)

### args

`stylus`
: ```default
  true
  ```

`hover_mode`
: ```default
  true
  ```

## StylusSpiralTouchMode

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touchscreen](../pytests/touchscreen.md)

### args

`stylus`
: ```default
  true
  ```

`hover_mode`
: ```default
  false
  ```

## StylusTopLeftToBottomLeft

### run_if

```default
not constants.has_device_data or device.component.has_stylus
```

### pytest_name

[stylus](../pytests/stylus.md)

### args

`endpoints_ratio`
: ```default
  [
    [
      0,
      0
    ],
    [
      0,
      1
    ]
  ]
  ```

## TouchDeviceFWUpdate

### pytest_name

[touch_device_fw_update](../pytests/touch_device_fw_update.md)

### args

`device_name`
: ```default
  "MyTouchDevice"
  ```

`fw_name`
: ```default
  "xxx.bin"
  ```

`fw_version`
: ```default
  "160.0"
  ```

## Touchscreen30x20

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touchscreen](../pytests/touchscreen.md)

### args

`y_segments`
: ```default
  30
  ```

`x_segments`
: ```default
  20
  ```

## TouchscreenArbitraryOrder

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touchscreen](../pytests/touchscreen.md)

### args

`spiral_mode`
: ```default
  false
  ```

## TouchscreenE2EMode

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touchscreen](../pytests/touchscreen.md)

### args

`e2e_mode`
: ```default
  true
  ```

## TouchscreenWithoutTimeLimit

### run_if

```default
not constants.has_device_data or device.component.has_touchscreen
```

### pytest_name

[touchscreen](../pytests/touchscreen.md)

### args

`timeout_secs`
: ```default
  null
  ```

## TouchscreenTests

### Serial subtests

- ProbeTouchscreen
- Stylus
- [StylusTopLeftToBottomLeft]()
- [StylusSpiralHoverMode]()
- [StylusSpiralTouchMode]()
- StylusGarage
- StylusAndGarage
- Touchscreen
- [Touchscreen30x20]()
- [TouchscreenWithoutTimeLimit]()
- [TouchscreenE2EMode]()
- [TouchscreenArbitraryOrder]()
- TouchscreenUniformity
- [TouchDeviceFWUpdate]()
