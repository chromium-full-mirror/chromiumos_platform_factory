# generic_audio

Predefined audio tests. It’s called “Audio Jack Codec”, “Smart Speaker Amplifier”, or “Speaker Amplifier” in AVL.

## Inherit

- [base.test_list](base.test_list.md)

## AudioJack

### pytest_name

[audio_loop](../pytests/audio_loop.md)

### args

`input_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Extmic"
  ]
  ```

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Headphone"
  ]
  ```

`mic_source`
: ```default
  "Extmic"
  ```

`require_dongle`
: ```default
  true
  ```

`check_dongle`
: ```default
  true
  ```

`tests_to_conduct`
: ```default
  [
    {
      "freq_threshold": 300,
      "rms_threshold": [
        0.08,
        null
      ],
      "type": "sinewav"
    }
  ]
  ```

## AudioJackConformance

### pytest_name

[audio_loop](../pytests/audio_loop.md)

### args

`input_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Extmic"
  ]
  ```

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Headphone"
  ]
  ```

`mic_source`
: ```default
  "Extmic"
  ```

`require_dongle`
: ```default
  true
  ```

`check_dongle`
: ```default
  false
  ```

`tests_to_conduct`
: ```default
  []
  ```

`autostart`
: ```default
  true
  ```

## ProbeAudioCodec

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "audio_codec"
  ]
  ```

`config_file`
: ```default
  "/usr/local/factory/py/hwid/v3/default_probe_statement.json"
  ```

`overridden_rules`
: ```default
  [
    [
      "audio_codec",
      ">",
      0
    ]
  ]
  ```

## SpeakerDMic

### pytest_name

[audio_loop](../pytests/audio_loop.md)

### args

`input_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Dmic"
  ]
  ```

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Speaker"
  ]
  ```

`mic_source`
: ```default
  "Dmic"
  ```

`require_dongle`
: ```default
  false
  ```

`check_dongle`
: ```default
  true
  ```

`tests_to_conduct`
: ```default
  [
    {
      "threshold": 80,
      "type": "audiofun",
      "volume_gain": 50
    }
  ]
  ```

## SpeakerDMicConformance

### pytest_name

[audio_loop](../pytests/audio_loop.md)

### args

`input_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Dmic"
  ]
  ```

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Speaker"
  ]
  ```

`mic_source`
: ```default
  "Dmic"
  ```

`require_dongle`
: ```default
  false
  ```

`check_dongle`
: ```default
  false
  ```

`tests_to_conduct`
: ```default
  []
  ```

`autostart`
: ```default
  true
  ```
