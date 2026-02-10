# audio_basic

**Source code:** [audio_basic.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/audio_basic.py)

Test basic audio record and playback.

## Description

This test check both record and playback for headset and built-in audio by
recording audio, play it back and ask operator for confirmation. An additional
pre-recorded sample is played to confirm speakers operate independently. Each
channel of input and output would be tested.

## Test Procedure

1. Instruction is shown on screen to ask operator to press either ‘P’ or ‘R’.
2. After operator press ‘P’, a pre-recorded sample is played back.
3. After operator press ‘R’, 3 seconds of audio would be recorded and played
   back.
4. Operator press space key to confirm both 2. and 3. step completes without
   problem, and the audio played back sounds correct.

## Dependency

- External program [sox](http://sox.sourceforge.net/).
- Device API `cros.factory.device.audio`.

## Examples

To check that audio can be recorded and played, add this into test list:

```default
{
  "pytest_name": "audio_basic",
  "label": "Speaker/Microphone Manual Test",
  "related_components": [
    "test_tags.TestCategory.AUDIOCODEC",
    "test_tags.TestCategory.SMART_SPEAKER_AMPLIFIER",
    "test_tags.TestCategory.SPEAKERAMPLIFIER"
  ],
  "args": {
    "input_dev": [
      "eval! device.component.audio_card_name or constants.audio.card_name",
      "99"
    ],
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

| Name              | Type       | Description                                                                                                     |
|-------------------|------------|-----------------------------------------------------------------------------------------------------------------|
| audio_title       | str, dict  | (optional; default: `{'en-US': 'Headset'}`) Label Title of audio test                                           |
| audio_conf        | str, None  | (optional; default: `None`) Audio config file path                                                              |
| initial_actions   | list, None | (optional; default: `None`) List of [card, actions]. If actions is None, the Initialize method will be invoked. |
| input_dev         | list       | (optional; default: `['0', '0']`) Input ALSA device. [card_name, sub_device].For example: [“audio_card”, “0”].  |
| output_dev        | list       | (optional; default: `['0', '0']`) Output ALSA device. [card_name, sub_device].For example: [“audio_card”, “0”]. |
| output_channels   | int        | (optional; default: `2`) number of output channels.                                                             |
| input_channels    | int        | (optional; default: `2`) number of input channels.                                                              |
| require_headphone | bool       | (optional; default: `False`) Require headphone option                                                           |
| timeout_secs      | int        | (optional; default: `30`) The timeout in seconds that the test waits for the headphone.                         |
