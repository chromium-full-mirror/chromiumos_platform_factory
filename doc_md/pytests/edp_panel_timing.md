# edp_panel_timing

**Source code:** [edp_panel_timing.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/edp_panel_timing.py)

Test eDP panel is supported with proper timing.

## Description

The eDP panel driver ‘panel-simple-dp-aux’ is a driver on ARM for ePD
panel, it can drive unknown panels as well with generic but conservative
timings. This test is to verify the eDP panel is not driven by generic but
conservative timing. It is only working with device with exactly 1
dp-aux device, and will perform check only if the used driver is
‘panel-simple-dp-aux’, and will check the debugfs content of
/sys/kernel/debug/dri/ */eDP*/panel/detected_panel and fail if the content is
‘UNKNOWN’.
If the test failed due to not driving the panel with dedicated power sequence,
a message ‘Unknown panel {panel_name} {panel_id}, using conservative timings’
is logged into dmesg. Please contact panel driver developers to ask them to add
support for the panel in the ‘drivers/gpu/drm/panel/panel-edp.c’, upstream the
change to Linux kernel, then land it in both main and relevant Chrome OS kernel
branches.

## Test Procedure

This is an automated test without user interaction.

## Dependency

- cros.factory.device.device_utils
- cros.factory.utils.sys_interface.Glob
- cros.factory.utils.sys_interface.ReadFile

## Examples

To test the eDP:

```default
{
  "pytest_name": "edp_panel_timing",
  "label": "Edp Panel Timing",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ]
}
```

## Test Arguments

This test does not have any arguments.
