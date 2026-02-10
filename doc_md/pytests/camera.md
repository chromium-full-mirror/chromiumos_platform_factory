# camera

**Source code:** [camera.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/camera.py)

Fixtureless camera test.

## Description

This pytest test if camera is working by one of the following method (choose
by argument `mode`):

* `'camera_assemble'`: Detect whether the camera is well assembled.
* `'qr'`: Scan QR code of given string.
* `'camera_assemble_qr'`: Run camera_assemble and qr mode together.
* `'face'`: Recognize a human face.
* `'timeout'`: Run camera capture until timeout.
* `'frame_count'`: Run camera capture for specified frames.
* `'manual'`: Show captured image.
* `'manual_led'`: Light or blink camera LED.
* `'brightness'`: Check the maximum brightness of frames.

## Test Procedure

If `e2e_mode` is `True`, the operator may be prompt to click on the ‘Allow’
button on Chrome notification to give Chrome camera permission. Set
–use-fake-ui-for-media-stream in /etc/chrome_dev.conf to accept the
permission automatically.

The test procedure differs for each different modes:

* `'camera_assemble'`: Operator prepares a white paper that is large enough
  to cover the FOV of the camera. Test would pass automatically after
  `num_frames_to_pass` frames with white paper are captured.
* `'qr'`: Operator put a QR code with content specified by `QR_string`.
  Test would pass automatically after `num_frames_to_pass` frames with QR code
  are captured.
* `'camera_assemble_qr'`: Operator prepares a white paper that has QR code on
  it. The white paper should be large enough to cover the FOV of the camera,
  and the QR code should locate at the specified detection region. Test would
  pass automatically after `num_frames_to_pass` frames with white paper and
  QR code are captured.
* `'face'`: Operator show a face to the camera. Test would pass automatically
  after `num_frames_to_pass` frames with detected face are captured.
* `'timeout'`: No user interaction is required, the test pass after
  `timeout_secs` seconds.
* `'frame_count'`: No user interaction is required, the test pass after
  `num_frames_to_pass` frames are captured.
* `'manual'`: Screen would show the image captured by camera, and operator
  judge whether the image looks good. Note that this methods require judgement
  by operator, so may yield false positivity.
* `'manual_led'`: The LED light of camera would either be constant on or
  blinking, and operator need to press the correct key to pass the test.
* `'brightness'`: No user interaction is required, the test pass after
  `num_frames_to_pass` frames are captured. Only the frames which the maximum
  brightness is between brightness_range are counted.

Except `'timeout'` mode, the test would fail after `timeout_secs` seconds.

## Dependency

End-to-end `'camera_assemble'`, `'qr'`, `'camera_assemble_qr'` and
`'face'` modes depend on OpenCV and numpy.

If not end-to-end mode, depend on OpenCV and device API
`cros.factory.device.camera`.

`'qr'` and `'camera_assemble_qr'` mode also depend on library `zbar`.

## Examples

To run a manual capture test:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera Manual",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "mode": "manual"
  }
}
```

To run camera_assemble test, and specify the minimal luminance ratio to 0.7:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera Assemble 07",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "mode": "camera_assemble",
    "min_luminance_ratio": 0.7
  }
}
```

To run QR scan test, and specify camera resolution to 1920 x 1080:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera QR Scan 1920x1080",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "mode": "qr",
    "QR_string": "Hello ChromeOS!",
    "timeout_secs": 2000,
    "camera_args": {
      "resolution": [
        1920,
        1080
      ]
    }
  }
}
```

To run camera_assemble_qr test:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera Assemble QR",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "mode": "camera_assemble_qr",
    "min_luminance_ratio": 0.5,
    "QR_string": "ChromeTeam"
  }
}
```

To run facial recognition test:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera Face",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "mode": "face"
  }
}
```

To stress camera for 1000 seconds, and don’t show the image:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera Stress",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "mode": "timeout",
    "timeout_secs": 1000,
    "show_image": false
  }
}
```

To stress camera capturing for 100 frames, have a timeout of 1000 seconds, and
don’t show the image:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera Frames",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "num_frames_to_pass": 100,
    "mode": "frame_count",
    "timeout_secs": 1000,
    "show_image": false
  }
}
```

To check the camera capturing black frames (the maximum brightness less than
10), this is a subitem of testing camera privacy switch:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera Brightness",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "num_frames_to_pass": 5,
    "mode": "brightness",
    "timeout_secs": 3,
    "brightness_range": [
      null,
      10
    ]
  }
}
```

This is used if camera_characteristics.conf is not ready. Users must replace
`camera_usb_vid_pid` with vid pid they are testing:

```default
{
  "pytest_name": "camera",
  "label": "Camera without camera_characteristics.conf",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "mode": "manual",
    "e2e_mode": false,
    "camera_facing": null,
    "camera_usb_vid_pid": [
      "13d3",
      "56ec"
    ]
  }
}
```

To test the LED of the front camera:

```default
{
  "pytest_name": "camera",
  "label": "Front Camera LED",
  "run_if": "not constants.has_device_data or device.component.has_front_camera",
  "related_components": [
    "test_tags.TestCategory.CAMERA",
    "test_tags.TestCategory.MIPI_CAMERA"
  ],
  "args": {
    "camera_facing": "front",
    "mode": "manual_led"
  }
}
```

## Test Arguments

| Name                        | Type                                                                                                                    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| mode                        | [‘brightness’, ‘camera_assemble’, ‘camera_assemble_qr’, ‘face’, ‘frame_count’, ‘manual’, ‘manual_led’, ‘qr’, ‘timeout’] | (optional; default: `'qr'`) The test mode to test camera.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| num_frames_to_pass          | int                                                                                                                     | (optional; default: `10`) The number of frames with faces in mode “face”, QR code presented in mode “qr”, or any frames in mode “frame_count” to pass the test.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| process_rate                | Real                                                                                                                    | (optional; default: `5`) The process rate of face recognition or QR code scanning in times per second.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| QR_string                   | str                                                                                                                     | (optional; default: `'Hello ChromeOS!'`) Encoded string in QR code.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| brightness_range            | list                                                                                                                    | (optional; default: `[None, None]`) **[min, max]**, check if the maximum brightness is between [min, max] (inclusive). None means no limit.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| capture_fps                 | Real                                                                                                                    | (optional; default: `30`) Camera capture rate in frames per second.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| timeout_secs                | int                                                                                                                     | (optional; default: `20`) Timeout value for the test.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| show_image                  | bool                                                                                                                    | (optional; default: `True`) Whether to actually show the image on screen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| e2e_mode                    | bool                                                                                                                    | (optional; default: `True`) Perform end-to-end test or not (for camera).<br/><br/>In non-e2e mode, camera data is grabbed from video device by OpenCV.<br/><br/>In e2e mode, camera data is directly streamed on frontend using<br/>JavaScript [MediaStream API](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream).<br/><br/>In e2e mode, if the test fails to create a video, then run the Tast<br/>test camera.GetUserMedia.real to test the e2e readiness. If it fails,<br/>for USB cameras, you can set e2e_mode to false and try the non-e2e<br/>mode; for MIPI cameras, it means the function is not ready for using<br/>this pytest. |
| resize_ratio                | float                                                                                                                   | (optional; default: `0.4`) The resize ratio of captured image on screen, has no effect on e2e mode.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| camera_facing               | [‘front’, ‘rear’], None                                                                                                 | (optional; default: `None`) String “front” or “rear” for the camera to test. If in normal mode, default is automatically searching one. If in e2e mode, default is “front”.                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| camera_usb_vid_pid          | list, None                                                                                                              | (optional; default: `None`) **[vid, pid]** The USB vendor id and product id of the camera to test. Each is a hex string. For testing an external USB camera. Only valid in normal mode and if camera_facing is not selected.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| flip_image                  | bool, None                                                                                                              | (optional; default: `None`) Whether to flip the image horizontally. This should be set to Falsefor the rear facing camera so the displayed image looks correct.The default value is False if camera_facing is “rear”, True otherwise.                                                                                                                                                                                                                                                                                                                                                                                                                   |
| camera_args                 | dict                                                                                                                    | (optional; default: `{}`) Args used for enabling the camera device.<br/><br/>In non-e2e mode, we call `EnableCamera(**camera_args)` defined<br/>in `camera_utils.ICameraReader`.<br/><br/>In e2e mode, only “resolution” is used. The default resolution is<br/>`[1280, 720]`. See the hardware<br/>[requirement](https://chromeos.google.com/partner/dlm/docs/versioned-requirements/chromebook-12.2.html#cam-usrFcg-0003-v01).                                                                                                                                                                                                                        |
| flicker_interval_secs       | int, float                                                                                                              | (optional; default: `0.5`) The flicker interval in seconds in manual_led mode                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| fullscreen                  | bool                                                                                                                    | (optional; default: `False`) Run the test in fullscreen                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| video_start_play_timeout_ms | int                                                                                                                     | (optional; default: `5000`) The timeout between we open a stream and it starts to play.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| get_user_media_retries      | int                                                                                                                     | (optional; default: `0`) The times that we try to getUserMedia in camera.js. The getUserMedia executes at most (1+get_user_media_retries) times.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| reinitialization_delay_ms   | int                                                                                                                     | (optional; default: `5000`) The delay between disable and enable in camera.js.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| min_luminance_ratio         | float                                                                                                                   | (optional; default: `0.5`) The minimal acceptable luminance of the boundary region of animage. This value is multiplied by the brightest region of animage. If the luminance of the boundary region is lower than orequal to the product, we consider the image containing black edges,and thus the camera is badly assembled. It is recommended to setthis value to 0.5 for USB camera and 0.7 for MIPI camera.                                                                                                                                                                                                                                        |
