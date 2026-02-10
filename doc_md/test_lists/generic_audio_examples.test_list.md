# generic_audio_examples

Examples for testing audio tests. It’s called “Audio Jack Codec”, “Smart Speaker Amplifier”, or “Speaker Amplifier” in AVL.

## Inherit

- [generic_audio.test_list](generic_audio.test_list.md)

## AudioDiagnostic

### pytest_name

[audio_diagnostic](../pytests/audio_diagnostic.md)

## AudioQuality

### pytest_name

[audio_quality](../pytests/audio_quality.md)

### args

`input_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "99"
  ]
  ```

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "0"
  ]
  ```

`wav_file`
: ```default
  "/usr/local/factory/third_party/SPK48k.wav"
  ```

## DSMCalibration

### pytest_name

[dsm_calibration](../pytests/dsm_calibration.md)

### args

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "0"
  ]
  ```

## HeadphoneManual

### pytest_name

[audio](../pytests/audio.md)

### args

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "1"
  ]
  ```

`check_headphone`
: ```default
  true
  ```

`require_headphone`
: ```default
  true
  ```

## ScanAudioCardName

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  [
    "audio_card_name=$(aplay -l | awk -F'[][]' '/card/ && /device 0/{print $2; exit}') && factory device-data component.audio_card_name=$audio_card_name"
  ]
  ```

## SpeakerChannel0DMic

Use the minimal volume_gain and lower frequency to protect ears in the examples. Use default volume_gain and frequency in production to achieve higher accuracy.

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
      "max_frequency": 1000,
      "min_frequency": 500,
      "output_channels": [
        0
      ],
      "threshold": 80,
      "type": "audiofun",
      "volume_gain": 1
    }
  ]
  ```

## SpeakerDMic

Use the minimal volume_gain and lower frequency to protect ears in the examples. Use default volume_gain and frequency in production to achieve higher accuracy.

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
      "max_frequency": 1000,
      "min_frequency": 500,
      "threshold": 80,
      "type": "audiofun",
      "volume_gain": 1
    }
  ]
  ```

## SpeakerDMic2

Dmic2 is an alias of Rear Mic.

### pytest_name

[audio_loop](../pytests/audio_loop.md)

### args

`input_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "Dmic2"
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
  "Dmic2"
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
      "max_frequency": 1000,
      "min_frequency": 500,
      "threshold": 80,
      "type": "audiofun",
      "volume_gain": 1
    }
  ]
  ```

## SpeakerDMicManual

### pytest_name

[audio_basic](../pytests/audio_basic.md)

### args

`input_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "99"
  ]
  ```

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "0"
  ]
  ```

## SpeakerDMicNoiseTest

Use the minimal volume_gain and lower frequency to protect ears in the examples. Use default volume_gain and frequency in production to achieve higher accuracy.

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
      "amplitude_threshold": [
        -0.9,
        0.9
      ],
      "duration": 2,
      "rms_threshold": [
        null,
        0.5
      ],
      "type": "noise"
    }
  ]
  ```

## SpeakerDMicSineWaveTest

Use the minimal volume_gain and lower frequency to protect ears in the examples. Use default volume_gain and frequency in production to achieve higher accuracy.

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
      "freq_threshold": 300,
      "rms_threshold": [
        0.08,
        null
      ],
      "type": "sinewav"
    }
  ]
  ```

## SpeakerExtmic

Use the minimal volume_gain and lower frequency to protect ears in the examples. Use default volume_gain and frequency in production to achieve higher accuracy.

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
    "Speaker"
  ]
  ```

`mic_source`
: ```default
  "Extmic"
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
  [
    {
      "max_frequency": 1000,
      "min_frequency": 500,
      "threshold": 80,
      "type": "audiofun",
      "volume_gain": 1
    }
  ]
  ```

## SpeakerManual

### pytest_name

[audio](../pytests/audio.md)

### args

`output_dev`
: ```default
  [
    "eval! device.component.audio_card_name or constants.audio.card_name",
    "0"
  ]
  ```

`check_headphone`
: ```default
  true
  ```

`require_headphone`
: ```default
  false
  ```

## AudioTests

### Serial subtests

- ProbeAudioCodec
- [ScanAudioCardName]()
- SpeakerDMicConformance
- [SpeakerDMic]()
- [SpeakerDMic2]()
- [SpeakerExtmic]()
- [SpeakerChannel0DMic]()
- [SpeakerDMicNoiseTest]()
- [SpeakerDMicSineWaveTest]()
- [SpeakerManual]()
- [SpeakerDMicManual]()
- [HeadphoneManual]()
- [AudioQuality]()
- AudioJackConformance
- AudioJack
- [AudioDiagnostic]()
- [DSMCalibration]()
