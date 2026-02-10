# dsm_calibration

**Source code:** [dsm_calibration.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/dsm_calibration.py)

A factory test to calibrate the smart speaker amplifier.

## Description

The test calibrates the smart speaker amplifier by following steps:

```default
1. Play silent music to load DSM module.
2. Enter calibration mode.
3. Wait for 3 seconds to get stable Rdc.
4. Read Rdc values from two speakers.
5. Store result to VPD.
6. Quit calibration mode.
```

After this test, it is recommended to run `RebootStep` to load calibration
data into cras, and run `SpeakerDMic` test to verify the calibration result.

This test only works for some smart speaker amplifiers because some vendors
don’t want to share their software to public.

## Test Procedure

This is an automated test without user interaction.

## Dependency

- `alsactl-tlv`
- Device API `cros.factory.device.audio`.
- Device API `cros.factory.device.vpd`.

## Examples

To calibrate the speaker device hw:1,0, add this into test list:

```default
{
  "pytest_name": "dsm_calibration",
  "label": "DSM Calibration",
  "related_components": [
    "test_tags.TestCategory.SMART_SPEAKER_AMPLIFIER",
    "test_tags.TestCategory.VPD"
  ],
  "args": {
    "output_dev": [
      "eval! device.component.audio_card_name or constants.audio.card_name",
      "0"
    ]
  }
}
```

See [audio_loop.py](./audio_loop.html) for more details about how to set
`output_dev`.

## Test Arguments

| Name                | Type   | Description                                                                                                     |
|---------------------|--------|-----------------------------------------------------------------------------------------------------------------|
| output_dev          | list   | (optional; default: `['0', '0']`) Output ALSA device. [card_name, sub_device].For example: [“audio_card”, “0”]. |
| num_output_channels | int    | (optional; default: `2`) Number of output channels.                                                             |
