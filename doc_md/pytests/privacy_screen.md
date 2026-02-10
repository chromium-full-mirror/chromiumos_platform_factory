# privacy_screen

**Source code:** [privacy_screen.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/privacy_screen.py)

Test that sets privacy screen to specific state.

## Description

This test measures the functionality of the privacy screen. It sets privacy
screen to a specific state then checks if privacy screen is refreshed to that
state.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- Need a built-in privacy screen.
- Command `cros-health-tool`.

## Examples

Turn privacy screen on and then validate state:

```default
{
  "pytest_name": "privacy_screen",
  "label": "Privacy Screen",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "target_state": "on"
  }
}
```

Argument `target_state` is required and must be either `on` or `off`.

## Test Arguments

| Name         | Type          | Description                  |
|--------------|---------------|------------------------------|
| target_state | [‘off’, ‘on’] | Privacy screen target state. |
