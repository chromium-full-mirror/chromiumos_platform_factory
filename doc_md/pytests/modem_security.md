# modem_security

**Source code:** [modem_security.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/modem_security.py)

Verify and close modem access authority.

## Description

This test verifies the modem access level. If the access level is not 0,
this test will try to set it to 0.

## Internal references

- b/120004153#comment23

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. Verify the access level of modem is 0. Pass the test if so.
2. Set the access level to 0.
3. Verify the access level of modem is 0. Pass the test if so.

## Dependency

- modem

## Examples

To verify and set modem access level to 0:

```default
{
  "pytest_name": "modem_security",
  "label": "Modem Security",
  "related_components": [
    "test_tags.TestCategory.WWAN"
  ]
}
```

## Test Arguments

This test does not have any arguments.
