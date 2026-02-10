# sample_customized_test

**Source code:** [sample_customized_test.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/sample_customized_test.py)

This is the sample code of a board specific test.

## Description

This is a sample test code to demonstrate how to write a board-specific test.

A board specific test should be put in the board overlay. For example, assuming
the overlay is located at
`~/trunk/src/private-overlays/overlay-${BOARD}-private`, then you have to
create the factory-board package and put files under relative path
`chromeos-base/factory-board/files/py/pytests/`.

To avoid file name conflict, please name the python script as “${BOARD}_xxx.py”.
For example, if you are implementing your own touchscreen test for board ABC, a
reasonable file name would be: `abc_touchscreen.py`.

## Test Procedure

This is only a sample code to demonstrate how to write a board-specific test.

## Dependency

None.

## Examples

To run this sample code with default arguments, add this in test list:

```default
{
  "pytest_name": "sample_customized_test",
  "args": {
    "foo": 1
  }
}
```

## Test Arguments

| Name   | Type      | Description                                                    |
|--------|-----------|----------------------------------------------------------------|
| foo    | int       | foo can only be int, not optional                              |
| bar    | str, None | (optional; default: `None`) bar is optional, default to None   |
| baz    | str       | (optional; default: `'BAZ'`) baz is optional, default to “BAZ” |
