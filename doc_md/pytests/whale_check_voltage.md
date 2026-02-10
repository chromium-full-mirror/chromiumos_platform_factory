# whale_check_voltage

**Source code:** [whale_check_voltage.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/whale_check_voltage.py)

Checks voltages.

## Description

### Internal references

- go/cros_whale_slides

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- bft_fixture
- Whale

## Examples

An example of checking green LED voltage:

```default
{
  "pytest_name": "whale_check_voltage",
  "args": {
    "bft_fixture": {
      "class_name":
        "cros.factory.test.fixture.dummy_bft_fixture.DummyBFTFixture",
      "params": {}
    },
    "criteria": {
      "krill_vc_connector_ina8": ["GREEN_LED", 1600, 100]
    },
    "timeout_secs": 30
  }
}
```

## Test Arguments

| Name               | Type       | Description                                                                                                                                                                                                                                                                                                                           |
|--------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bft_fixture        | dict       | A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| criteria           | dict       | Criteria of measured voltage. A dict {ina_name: (schematic_name, expected_voltage, relative_tolerance)} where the unit of voltage is mV                                                                                                                                                                                               |
| timeout_secs       | int, float | (optional; default: `10`) Total #seconds to perform voltage checking                                                                                                                                                                                                                                                                  |
| poll_interval_secs | int, float | (optional; default: `0.3`) Pause between voltage check                                                                                                                                                                                                                                                                                |
