# generic_battery_examples

Examples for testing battery tests. It’s called “Battery” in AVL.

## Inherit

- [generic_battery.test_list](generic_battery.test_list.md)
- [generic_common.test_list](generic_common.test_list.md)

## BatteryBasic

### pytest_name

[battery_basic](../pytests/battery_basic.md)

## BatteryBasicCycleCountAtMost5

### pytest_name

[battery_basic](../pytests/battery_basic.md)

### args

`max_cycle_count`
: ```default
  5
  ```

## BatteryCapacity

### run_if

```default
constants.has_battery
```

### pytest_name

[battery](../pytests/battery.md)

## BatteryCapacityBetween4000And8000

### run_if

```default
constants.has_battery
```

### pytest_name

[battery](../pytests/battery.md)

### args

`design_capacity_range`
: ```default
  [
    4000,
    8000
  ]
  ```

## BatteryCycle

### pytest_name

[battery_cycle](../pytests/battery_cycle.md)

## BlockingCharge10PercentMoreIn5Minutes

### pytest_name

[blocking_charge](../pytests/blocking_charge.md)

### args

`target_charge_pct_is_delta`
: ```default
  true
  ```

`timeout_secs`
: ```default
  300
  ```

`target_charge_pct`
: ```default
  10
  ```

## BlockingChargeTo75

### pytest_name

[blocking_charge](../pytests/blocking_charge.md)

### args

`target_charge_pct`
: ```default
  75
  ```

## BlockingChargeToCutOffSetting

### pytest_name

[blocking_charge](../pytests/blocking_charge.md)

### args

`target_charge_pct`
: ```default
  "cutoff"
  ```

## ChargeDischargeCurrentDifference

### pytest_name

[battery_current](../pytests/battery_current.md)

### args

`min_charging_current`
: ```default
  null
  ```

`min_discharging_current`
: ```default
  null
  ```

`timeout_secs`
: ```default
  30
  ```

`max_battery_level`
: ```default
  90
  ```

`current_difference`
: ```default
  250
  ```

## ChargeDischargeCurrentExpectNoChargeWhenCharging

### pytest_name

[battery_current](../pytests/battery_current.md)

### args

`min_charging_current`
: ```default
  -150
  ```

`min_discharging_current`
: ```default
  400
  ```

`timeout_secs`
: ```default
  30
  ```

`max_battery_level`
: ```default
  90
  ```

## Charger

### pytest_name

[charger](../pytests/charger.md)

### args

`min_starting_charge_pct`
: ```default
  87
  ```

`max_starting_charge_pct`
: ```default
  87
  ```

`check_battery_current`
: ```default
  false
  ```

`starting_timeout_secs`
: ```default
  3600
  ```

`spec_list`
: ```default
  []
  ```

## Charger20VInPort0

### pytest_name

[battery_current](../pytests/battery_current.md)

### args

`usbpd_info`
: ```default
  [
    0,
    19000,
    21000
  ]
  ```

`usbpd_prompt`
: ```default
  "i18n! USB TypeC"
  ```

## BatteryTests

### Serial subtests

- ProbeBattery
- [BatteryCapacity]()
- [BatteryCapacityBetween4000And8000]()
- BatterySysfs
- ChargeDischargeCurrent
- [ChargeDischargeCurrentExpectNoChargeWhenCharging]()
- [ChargeDischargeCurrentDifference]()
- [Charger20VInPort0]()
- [BatteryBasic]()
- [BatteryBasicCycleCountAtMost5]()
- ChargerTypeDetection
- [BlockingChargeToCutOffSetting]()
- [BlockingCharge10PercentMoreIn5Minutes]()
- [BlockingChargeTo75]()
- [Charger]()
- BlockingCharge
- [BatteryCycle]()
- BCICGroup
