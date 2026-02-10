# lightbar

**Source code:** [lightbar.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/lightbar.py)

Factory test for lightbar on A-case.

## Description

The test checks if the color of the light bar is correct for given colors.

[Here](https://chromeunboxed.com/lenovos-light-bar-toting-14-chromebook-5i-is-available-and-100-off) is a site that introduces a chromebook with a light
bar.

## Test Procedure

1. Set light bar to a color in colors_to_test.
2. The operator judges if the color is correct.
3. Go back to 1. until all the colors in colors_to_test are tested.

## Dependency

- `ectool lightbar`

## Examples

An example:

```default
{
  "pytest_name": "lightbar"
}
```

## Test Arguments

| Name           | Type   | Description                                                                                                                                                                                                                                                                                                |
|----------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| colors_to_test | list   | (optional; default: `[[{'en-US': 'red'}, [4, 255, 0, 0]], [{'en-US': 'green'}, [4, 0, 255, 0]], [{'en-US': 'blue'}, [4, 0, 0, 255]], [{'en-US': 'dark'}, [4, 0, 0, 0]], [{'en-US': 'white'}, [4, 255, 255, 255]]]`) a list of colors to test; each element of the list is [label, [LED, RED, GREEN, BLUE]] |
