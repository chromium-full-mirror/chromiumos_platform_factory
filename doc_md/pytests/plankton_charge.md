# plankton_charge

**Source code:** [plankton_charge.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/plankton_charge.py)

Test USB type-C port charging function with Plankton-Raiden board.

## Description

This test can be tested locally or in remote ADB connection manner.

Use Plankton-Raiden board control to verify device battery current. It supports
charge-5V, charge-12V, charge-20V, and discharge. This test also takes INA
current and voltage value on Plankton-Raiden board into account as a judgement.

Sometimes the charge current may not be stable, we have to wait for several
seconds until the current stable then sampling the current value.

## Test Procedure

This is an automated test without user interaction, but the environment must
be setup first:

1. Connect the testing USB type-C port to Plankton-Raiden board.
2. Connect the Plankton-Raiden serial commanding port to Plankton-Raiden board.
3. Specify the type of the bft_fixutre connecting to.
4. Specify the charging/discharing voltage/current and its minimun/maximun
   threshold.
5. Start the test.

## Dependency

- Connections to Plankton-Raiden board must setup before starting.

## Examples

To test 5V charge, add this in test list:

```default
{
  "pytest_name": "plankton_usb_c_charge",
  "args": {
    "bft_fixture": {
      "class_name":
        "cros.factory.test.fixture.dummy_bft_fixture.DummyBFTFixture",
      "params": {}
    },
    "min_charge_5V_current_mA": 0
  }
}
```

Test 20V charge without checking the input current:

```default
{
  "pytest_name": "plankton_usb_c_charge",
  "args": {
    "bft_fixture": {
      "class_name":
        "cros.factory.test.fixture.dummy_bft_fixture.DummyBFTFixture",
      "params": {}
    },
    "min_charge_20V_current_mA": 0,
    "check_ina_current": false
  }
}
```

## Test Arguments

| Name                          | Type             | Description                                                                                                                                                                                                                                                                                                                           |
|-------------------------------|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bft_fixture                   | dict             | A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| charge_duration_secs          | int, float       | (optional; default: `5`) The duration in seconds to charge the battery                                                                                                                                                                                                                                                                |
| discharge_duration_secs       | int, float       | (optional; default: `5`) The duration in seconds to discharge the battery                                                                                                                                                                                                                                                             |
| wait_after_engage_secs        | int, float       | (optional; default: `0`) The duration in seconds to wait after engage / disengage charge device                                                                                                                                                                                                                                       |
| min_charge_5V_current_mA      | int, float, None | (optional; default: `None`) The minimum charge current in mA that the battery needs to reach during charge-5V test, if is None, it would not check on this voltage level                                                                                                                                                              |
| min_charge_12V_current_mA     | int, float, None | (optional; default: `None`) The minimum charge current in mA that the battery needs to reach during charge-12V test, if is None, it would not check on this voltage level                                                                                                                                                             |
| min_charge_20V_current_mA     | int, float, None | (optional; default: `None`) The minimum charge current in mA that the battery needs to reach during charge-20V test, if is None, it would not check on this voltage level                                                                                                                                                             |
| min_discharge_current_mA      | int, float, None | (optional; default: `None`) The minimum discharge current in mA that the battery needs to reach during discharging test, if is None, it would not check on this voltage level                                                                                                                                                         |
| current_sampling_period_secs  | int, float       | (optional; default: `0.5`) The period in seconds to sample charge/discharge current during test                                                                                                                                                                                                                                       |
| check_battery_cycle           | bool             | (optional; default: `False`) Whether to check battery cycle count is lower than threshold                                                                                                                                                                                                                                             |
| battery_cycle_threshold       | int              | (optional; default: `0`) The threshold for battery cycle count                                                                                                                                                                                                                                                                        |
| check_protect_ina_current     | bool             | (optional; default: `True`) If set True, it would check if Plankton 5V INA current is within protect_ina_current_range first for high-V protection                                                                                                                                                                                    |
| protect_ina_current_range     | list             | (optional; default: `[2000, 3400]`) A list for indicating reasonable current in mA of charge-5V from Plankton INA for high-V protection                                                                                                                                                                                               |
| protect_ina_retry_times       | int              | (optional; default: `5`) Retry times for checking 5V INA current for high-V protection, interval with 1 second                                                                                                                                                                                                                        |
| check_ina_current             | bool             | (optional; default: `True`) If set True, it would check Plankton INA current during testing whether within ina_current_charge_range for charging, or ina_current_discharge_range for discharge                                                                                                                                        |
| ina_current_charge_range      | list             | (optional; default: `[2000, 3400]`) A list for indicating reasonable current in mA during charging from Plankton INA                                                                                                                                                                                                                  |
| ina_current_discharge_range   | list             | (optional; default: `[-3500, 0]`) A list for indicating reasonable current in mA during discharging from Plankton INA                                                                                                                                                                                                                 |
| ina_voltage_tolerance         | float            | (optional; default: `0.12`) Tolerance ratio for Plankton INA voltage compared to expected charging voltage                                                                                                                                                                                                                            |
| monitor_plankton_voltage_only | bool             | (optional; default: `False`) If set True, it would only check Plankton INA voltage whether as expected (not check DUT side)                                                                                                                                                                                                           |
