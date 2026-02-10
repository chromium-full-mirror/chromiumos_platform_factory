# whale_cover

**Source code:** [whale_cover.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/whale_cover.py)

Checks if Whale’s cover is opened / closed.

## Description

### Internal references

- go/cros_whale_slides

## Test Procedure

1. Display instruction to tell the operator to open/close the cover.
2. The operator opens/closes the cover.

## Dependency

- bft_fixture
- Whale

## Examples

An example of checking if whale is closed:

```default
{
  "pytest_name": "whale_cover",
  "args": {
    "bft_fixture": {
      "class_name":
        "cros.factory.test.fixture.dummy_bft_fixture.DummyBFTFixture",
      "params": {}
    },
    "check_interval_secs": 0.2,
    "check_open": false
  }
}
```

## Test Arguments

| Name                | Type       | Description                                                                                                                                                                                                                                                                                                                           |
|---------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bft_fixture         | dict       | A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| check_interval_secs | int, float | (optional; default: `0.5`) Interval of checking cover                                                                                                                                                                                                                                                                                 |
| check_open          | bool       | (optional; default: `True`) True to check if the cover is open; False to check if it’s closed                                                                                                                                                                                                                                         |
