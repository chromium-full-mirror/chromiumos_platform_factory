# branded_chassis

**Source code:** [branded_chassis.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/branded_chassis.py)

A test to check if chassis is branded.

## Description

This pytest reads the data from device_data and ask the operator to verify if
there the A panel of the chassis has “SOMETHING” on it. Upon verifying by the
operator, the Pytest will store the information.

## Test Procedure

The operator should visually inspect if the chassis has “SOMETHING” on the
A panel.

## Dependency

- Display
- Chassis

## Examples

To verify the the chassis is branded, add this to the test list:

```default
{
  "pytest_name": "branded_chassis",
}
```

or

> “BrandedChassis”

## Test Arguments

| Name     | Type   | Description                                   |
|----------|--------|-----------------------------------------------|
| rma_mode | bool   | (optional; default: `False`) Enable rma_mode. |
