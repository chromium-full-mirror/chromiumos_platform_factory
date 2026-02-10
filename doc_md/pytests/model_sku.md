# model_sku

**Source code:** [model_sku.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/model_sku.py)

A test to confirm and set SKU information.

## Description

A test to confirm SKU information, then apply SKU or model specific settings.
And there are two modes:

1. manually ask to operator to confirm SKU information.
2. automatically compare SKU information with device data - component.sku.

If device data - component.sku is set then this test will go to automatic mode
or manual mode will be executed.

This is a test to verify hardware root of trust, so there’s no options to
set auto verification for this test. Instead, either it relies on the operator
to check manually or compares with device data from shopfloor which would need
to be configured in advance.

After the SKU is confirmed, the test will load a JSON configuration specified by
`config_name`. The config should be a dictionary containing what device data
(usually `component.*`) to set for matched model and SKU. For example, to set
if the touchscreen is available for model ‘coral’ with default True, and only
False for product_name Coral SKU 3:

```default
{
  "model": {
    "coral": {
      "component.has_touchscreen": true
    }
  },
  "product_sku": {
    "Coral": {
      "3": {
        "component.has_touchscreen": false
      }
    }
  }
}
```

## Test Procedure

The test runs following commands:

- cros_config / name
- cros_config /identity sku-id
- cros_config / brand-code

And then asks OP to press ENTER/ESC to confirm if these values are correct.

## Dependency

- `mosys` utility.

## Examples

To ask OP to confirm sku information, add this in test list:

```default
{
  "pytest_name": "model_sku"
}
```

## Test Arguments

| Name         | Type      | Description                                                                                                                                                                            |
|--------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| config_name  | str, None | (optional; default: `None`) Name of JSON config to load for setting device data. Set this argument to boxster if you want to load boxster data.                                        |
| schema_name  | str, None | (optional; default: `None`) Name of JSON schema to load for setting device data.                                                                                                       |
| product_name | str, None | (optional; default: `None`) The product_name of the device. If not specified, read from /sys/class/dmi/id/product_name on x86 devices and /proc/device-tree/compatible on ARM devices. |
