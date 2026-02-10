# video_playback

**Source code:** [video_playback.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/video_playback.py)

A video playback test.

## Description

This test exposes options to assign file to play, loop, control ui, and time
limitation.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- HTML <video> Tag

## Examples

To record from camera and internal mics and playback immediately:

```default
{
  "pytest_name": "video_playback"
}
```

To play an video, you must put 720_h264.mp4 under video_playback_static:

```default
{
  "pytest_name": "video_playback",
  "args": {
    "video_file": "720_h264.mp4"
  }
}
```

## Test Arguments

| Name          | Type   | Description                                                          |
|---------------|--------|----------------------------------------------------------------------|
| video_file    | str    | (optional; default: `''`) Relative path to load the video.           |
| loop          | bool   | (optional; default: `False`) Whether we want to loop the video.      |
| time_limit    | int    | (optional; default: `10`) Seconds to force terminate the test.       |
| show_controls | bool   | (optional; default: `False`) Whether we want to show the control UI. |
| audio_device  | str    | (optional; default: `''`) Name of audio input device.                |
| video_device  | str    | (optional; default: `''`) Name of video input device.                |
