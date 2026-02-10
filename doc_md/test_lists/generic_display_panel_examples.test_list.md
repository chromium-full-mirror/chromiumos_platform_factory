# generic_display_panel_examples

Examples for testing display_panel components. display_panel is called “Display Panel” in AVL.

## Inherit

- [generic_display_panel.test_list](generic_display_panel.test_list.md)

## BacklightSmallerAdjustLevel

### pytest_name

[backlight](../pytests/backlight.md)

### args

`adjust_level`
: ```default
  0.02
  ```

## BrightnessLCDBacklight

### pytest_name

[brightness.lcd_backlight](../pytests/brightness.lcd_backlight.md)

### args

`levels`
: ```default
  [
    0.2,
    0.4,
    0.6,
    0.8,
    1.0
  ]
  ```

## DisplayGrayForAnHour

### pytest_name

[display](../pytests/display.md)

### args

`items`
: ```default
  [
    "solid-gray-127"
  ]
  ```

`idle_timeout`
: ```default
  3600
  ```

## EnterFrontOfScreenTestInteractiveMode

### pytest_name

[display_interactive.display_interactive](../pytests/display_interactive.display_interactive.md)

### args

`port`
: ```default
  5566
  ```

`autostart`
: ```default
  true
  ```

## FrontOfScreenTestMoreImages

### pytest_name

[display](../pytests/display.md)

### args

`items`
: ```default
  [
    "grid",
    "rectangle",
    "gradient-red",
    "image-complex.bmp",
    "image-black.bmp",
    "image-white.bmp",
    "image-crosstalk-black.bmp",
    "image-crosstalk-white.bmp",
    "image-gray-63.bmp",
    "image-gray-127.bmp",
    "image-gray-170.bmp",
    "image-horizontal-rgbw.bmp",
    "image-vertical-rgbw.bmp",
    "hex-color-#afafaf",
    "hex-color-#abc"
  ]
  ```

## FrontOfScreenTestStation

### pytest_name

[display_images](../pytests/display_images.md)

### args

`compressed_image_file`
: ```default
  "display_images.tar.gz"
  ```

## FrontOfScreenTestSymptom

### pytest_name

[display](../pytests/display.md)

### args

`items`
: ```default
  [
    "image-complex.bmp",
    "solid-red",
    "hex-color-#afafaf"
  ]
  ```

`symptoms`
: ```default
  [
    "Symptom1",
    "Symptom2",
    "Dark Dots",
    "Light Leakage",
    "Others"
  ]
  ```

## PrivacyScreen

### pytest_name

[privacy_screen](../pytests/privacy_screen.md)

### args

`target_state`
: ```default
  "on"
  ```

## DisplayPanelTests

### Serial subtests

- ProbeDisplayPanel
- Backlight
- [BacklightSmallerAdjustLevel]()
- [BrightnessLCDBacklight]()
- Display
- DisplayPoint
- EDPPanelTiming
- [PrivacyScreen]()
- [FrontOfScreenTestSymptom]()
- [FrontOfScreenTestMoreImages]()
- [DisplayGrayForAnHour]()
- [EnterFrontOfScreenTestInteractiveMode]()
- [FrontOfScreenTestStation]()
