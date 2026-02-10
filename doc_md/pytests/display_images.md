# display_images

**Source code:** [display_images.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/display_images.py)

A station-based factory test to test the function of display.

## Description

The test will display images on the display.
It will extract image files from factory/misc/display_images.tar.gz by default.
User can add new xx.tar.gz in the private overlay.
The display order is based on the sorted file name.

Two directories, dut/ and station/, are required in the image archive xx.tar.gz.
For each image to be tested, two images with same file name are required in each
directory, but we can use different extension name depending on the file format.
The image under dut/ is for displaying on DUT. The image under station/ is for
providing information to operators.
e.g.
dut/abc.ppm and station/abc.bmp

This test is also known as FOS (front-of-screen) test.

## Test Procedure

1. Display one image.
2. Operator marks pass or fail.
3. Go back to 1. until there is no image left.

## Dependency

- Device API cros.factory.device.display.
- Device API cros.factory.device.path.
- Device API cros.factory.device.temp.

## Examples

To test display on remote DUT:

```default
{
  "pytest_name": "display_images",
  "label": "Front Of Screen Test Station",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "compressed_image_file": "display_images.tar.gz"
  }
}
```

## Test Arguments

| Name                  | Type      | Description                                                                |
|-----------------------|-----------|----------------------------------------------------------------------------|
| title                 | str, dict | (optional; default: `{'en-US': 'Display Test'}`) Label Title of the test   |
| compressed_image_file | str       | (optional; default: `'display_images.tar.gz'`) Compressed image file name. |
