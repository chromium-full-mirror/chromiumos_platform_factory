# display_point

**Source code:** [display_point.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/display_point.py)

A factory test to test the function of display panel using some points.

## Description

Show some points on the display. The test is designed to catch display with
dark dots.

## Test Procedure

1. Display white/black screen with a random number of black/white dots at random
   generated positions.
2. Operator reports the number of dots.
3. Fails if the numbers don’t match.
4. Display the other color in step 1 and generate the dots again.
5. Operator reports the number of dots.
6. Fails if the numbers don’t match.

## Dependency

- A browser to run display_point.js.

## Examples

Sample test_list entry:

```default
{
  "pytest_name": "display_point",
  "label": "Display Point",
  "related_components": [
    "test_tags.TestCategory.LCD"
  ],
  "args": {
    "point_size": 3.0,
    "max_point_count": 5
  }
}
```

## Test Arguments

| Name            | Type       | Description                                                        |
|-----------------|------------|--------------------------------------------------------------------|
| point_size      | float, int | (optional; default: `3.0`) width and height of testing point in px |
| max_point_count | int        | (optional; default: `3`) maximum number of points in each subtest  |
