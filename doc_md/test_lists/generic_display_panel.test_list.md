# generic_display_panel

Predefined display_panel tests. display_panel is called “Display Panel” in AVL.

## Inherit

- [base.test_list](base.test_list.md)

## Backlight

### pytest_name

[backlight](../pytests/backlight.md)

## Display

### pytest_name

[display](../pytests/display.md)

## DisplayPoint

### pytest_name

[display_point](../pytests/display_point.md)

### args

`point_size`
: ```default
  3.0
  ```

`max_point_count`
: ```default
  5
  ```

## EDPPanelTiming

### pytest_name

[edp_panel_timing](../pytests/edp_panel_timing.md)

## ProbeDisplayPanel

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "display_panel"
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
      "display_panel",
      "==",
      1
    ]
  ]
  ```
