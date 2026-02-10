# audio

**Source code:** [audio.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/audio.py)

Tests audio playback.

## Description

The test plays a random digit from speaker, and checks if the operator presses
the correct key.

If `test_left_right` is set, left and right output channels are tested
separately.

If `check_headphone` is set, before the digit is played, the test would check
if the headphone status is same as `require_headphone` , and ask the operator
to plug in / disconnect the headphone otherwise.

A valid `output_dev` should be specified, which is in the form of
`(card_name, sub_device)`. Both value can be obtained from output of
`aplay -l` on DUT.

Also, you may need to set `initial_actions` for audio to work correctly.
Refer to the audio.json config file on what actions should be set as
`initial_actions`.

## Test Procedure

1. If `check_headphone` is set, operator will be prompted to plug in or
   disconnect to headphone.
2. A digit would be played.
3. Operator presses the key corresponds to the digit played. Test fail if the
   operator presses the wrong key.
4. If `test_left_right`, repeat 2. and 3. on another channel.

## Dependency

- External program [sox](http://sox.sourceforge.net/).
- Device API `cros.factory.device.audio`.

## Examples

To check if the audio can be played, add this in test list:

```default
{
  "pytest_name": "audio",
  "label": "Speaker Manual Test",
  "related_components": [
    "test_tags.TestCategory.AUDIOCODEC",
    "test_tags.TestCategory.SMART_SPEAKER_AMPLIFIER",
    "test_tags.TestCategory.SPEAKERAMPLIFIER"
  ],
  "args": {
    "output_dev": [
      "eval! device.component.audio_card_name or constants.audio.card_name",
      "0"
    ],
    "check_headphone": true,
    "require_headphone": false
  }
}
```

To check that headphone is plugged in before audio is played, add this in test
list:

```default
{
  "pytest_name": "audio",
  "label": "Headphone Manual Test",
  "related_components": [
    "test_tags.TestCategory.AUDIOCODEC",
    "test_tags.TestCategory.SMART_SPEAKER_AMPLIFIER",
    "test_tags.TestCategory.SPEAKERAMPLIFIER"
  ],
  "args": {
    "output_dev": [
      "eval! device.component.audio_card_name or constants.audio.card_name",
      "1"
    ],
    "check_headphone": true,
    "require_headphone": true
  }
}
```

See [audio_loop.py](./audio_loop.html) for more details about how to set
`output_dev`.

## Test Arguments

| Name              | Type       | Description                                                                                                     |
|-------------------|------------|-----------------------------------------------------------------------------------------------------------------|
| audio_conf        | str, None  | (optional; default: `None`) Audio config file path                                                              |
| initial_actions   | list, None | (optional; default: `None`) List of [card, actions]. If actions is None, the Initialize method will be invoked. |
| output_dev        | list       | (optional; default: `['0', '0']`) Onput ALSA device. [card_name, sub_device].For example: [“audio_card”, “0”].  |
| port_label        | str, dict  | (optional; default: `{'en-US': 'Internal Speaker'}`) Label of audio.                                            |
| test_left_right   | bool       | (optional; default: `True`) Test left and right channel.                                                        |
| require_headphone | bool       | (optional; default: `False`) Require headphone option                                                           |
| check_headphone   | bool       | (optional; default: `False`) Check headphone status whether match require_headphone                             |
| sample_rate       | int, None  | (optional; default: `None`) Required sample rate to be played by the device.                                    |
