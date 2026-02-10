# display

**Source code:** [display.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/display.py)

Test display functionality.

## Description

This test checks basic display functionality by showing colors or images on
display, and asks the operator to judge if the output looks correct.

The test can also be used to show an image for `idle_timeout` seconds, and
automatically pass itself after timeout is reached.

## Test Procedure

`Idle mode`
If `idle_timeout` is set and `symptoms` is not set:

> 1. An image is shown on the display.
> 2. If the image looks incorrect, press escape key to fail the test.
> 3. The test passes itself after `idle_timeout` seconds.

`Normal mode`
If `idle_timeout` and `symptoms` are both not set:

> 1. A table of images to be tested is shown.
> 2. Operator presses space key to show the image.
> 3. For each image, if it looks correct, operator presses enter key to mark the
>    item as passed, otherwise, operator presses escape key to mark the item as
>    failed.  Operator can press space key to return to the table view.
> 4. The next image would be shown after the previous one is judged.
> 5. The test is passed if all items are judged as passed, and is failed if any
>    item is judged as failed.

`Symptom mode`
If `symptom` is set and `idle_timeout` is not set:

> 1. A table of images and symptoms to be checked is shown.
> 2. For each symptom, if it is observed, click the corresponding symptom grid
>    to mark it.
> 3. Press enter to end the subtest. The test is passed if all symptoms are not
>    marked, and is failed if any symptom is marked.
> 4. The next image would be shown after the previous one is judged.
> 5. The test is passed if all items are judged as passed, and is failed if any
>    item is judged as failed.

## Dependency

Each item of `items` is either:
: 1. `image-<image_name>`: The corresponding <image_name> should be in the
     : compressed file `test_images.tar.bz2`. For example, if the item is
       “image-horizontal-rgbw.bmp”, an image named “horizontal-rgbw.bmp”
       should be in `test_images.tar.bz2`. We support image file formats:
       apng, avig, bmp, gif, ico, jpeg, png, svg, and webp.
  2. `hex-color-<hex_color_code>`.
  3. A predefined CSS item listed in `_CSS_ITEMS`.

## Examples

To test display functionality, add this into test list:

```default
{
  "pytest_name": "display",
  "label": "Display",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ]
}
```

To test display functionality, show gray image, idle for an hour and pass, add
this into test list:

```default
{
  "pytest_name": "display",
  "label": "Display Gray For An Hour",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "items": [
      "solid-gray-127"
    ],
    "idle_timeout": 3600
  }
}
```

To test images with symptoms, add this into test list:

```default
{
  "pytest_name": "display",
  "label": "Front Of Screen Test (Symptom mode)",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "items": [
      "image-complex.bmp",
      "solid-red",
      "hex-color-#afafaf"
    ],
    "symptoms": [
      "Symptom1",
      "Symptom2",
      "Dark Dots",
      "Light Leakage",
      "Others"
    ]
  }
}
```

To test display functionality, and show some more images, add this into test
list:

```default
{
  "pytest_name": "display",
  "label": "Front Of Screen Test (More Images)",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "items": [
      "grid",
      "rectangle",
      "gradient-red",
      "image-complex.bmp",
      "image-black.bmp",
      "image-white.bmp",
      "image-crosstalk-black.bmp",
      "image-crosstalk-white.bmp",
      "image-gray-63.bmp",
      "image-gray-127.bmp",
      "image-gray-170.bmp",
      "image-horizontal-rgbw.bmp",
      "image-vertical-rgbw.bmp",
      "hex-color-#afafaf",
      "hex-color-#abc"
    ]
  }
}
```

Default images in compressed file `test_images.tar.bz2`:

```default
['black.bmp',
 'complex.bmp',
 'crosstalk-black.bmp',
 'crosstalk-white.bmp',
 'gray-127.bmp',
 'gray-170.bmp',
 'gray-63.bmp',
 'horizontal-rgbw.bmp',
 'vertical-rgbw.bmp',
 'white.bmp']
```

## Test Arguments

| Name          | Type      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|---------------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| items         | list      | (optional; default: `['solid-gray-170', 'solid-gray-127', 'solid-gray-63', 'solid-red', 'solid-green', 'solid-blue']`) Set items to be shown on screen. Available items are: items with prefix “image-” and<br/>: * `"solid-gray-170"`<br/>  * `"solid-gray-127"`<br/>  * `"solid-gray-63"`<br/>  * `"solid-red"`<br/>  * `"solid-green"`<br/>  * `"solid-blue"`<br/>  * `"solid-white"`<br/>  * `"solid-gray"`<br/>  * `"solid-black"`<br/>  * `"grid"`<br/>  * `"rectangle"`<br/>  * `"gradient-red"`<br/>  * `"gradient-green"`<br/>  * `"gradient-blue"`<br/>  * `"gradient-white"` |
| idle_timeout  | int, None | (optional; default: `None`) If given, the test would be start automatically, run for idle_timeout seconds, and pass itself. Note that items should contain exactly one item in this mode.                                                                                                                                                                                                                                                                                                                                                                                               |
| quick_display | bool      | (optional; default: `True`) If set to true, the next item will be shown automatically on enter pressed i.e. no additional space needed to toggle screen.                                                                                                                                                                                                                                                                                                                                                                                                                                |
| show_timer    | bool      | (optional; default: `False`) If set to true, the timer will be shown in idle mode.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| symptoms      | list      | (optional; default: `[]`) Symptoms to check for images                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
