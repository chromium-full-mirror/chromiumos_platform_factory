# audio_diagnostic

**Source code:** [audio_diagnostic.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/audio_diagnostic.py)

Tests to manually test audio playback and record quality.

## Description

This test case is a manual test to do audio functions on DUT and let operator or
engineer mark pass or fail from their own judgement.

## Test Procedure

1. Operator triggers audio function on the UI.
2. Operator marks pass or fail.

## Dependency

- JavaScript MediaStream API

## Examples

To check that audio can be recorded and played, add this into test list:

```default
{
  "pytest_name": "audio_diagnostic",
  "label": "Audio Diagnostic",
  "related_components": [
    "test_tags.TestCategory.AUDIOCODEC",
    "test_tags.TestCategory.SMART_SPEAKER_AMPLIFIER",
    "test_tags.TestCategory.SPEAKERAMPLIFIER"
  ]
}
```

## Test Arguments

This test does not have any arguments.
