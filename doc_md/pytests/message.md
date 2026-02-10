# message

**Source code:** [message.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/message.py)

Displays a message.

## Description

This test displays a HTML message to the operator, and wait for the operator
pressing space key to pass the test.

If `manual_check` is True, the operator can also press escape key to fail the
test.

If `seconds` is given, the test would pass automatically after `seconds`
seconds.

## Test Procedure

When started, the test will show a message and wait for operator to press space
to pass the test, or press escape to fail the test (if `manual_check` is set).

## Dependency

None.

## Examples

To show a message, add this in test list:

```default
{
  "pytest_name": "message",
  "args": {
    "html": "i18n! Hello world!"
  }
}
```

To show a message with some formatting, and give operator ability to fail the
test:

```default
{
  "pytest_name": "message",
  "args": {
    "text_size": 300,
    "manual_check": true,
    "show_press_button_hint": true,
    "html": "i18n! Please check if the result is <b>correct</b>.",
    "text_color": "red"
  }
}
```

To show a message for 20 seconds, and automatically pass:

```default
{
  "pytest_name": "message",
  "args": {
    "seconds": 20,
    "html": "i18n! Waiting for something..."
  }
}
```

## Test Arguments

| Name                   | Type      | Description                                                                                                   |
|------------------------|-----------|---------------------------------------------------------------------------------------------------------------|
| html                   | str, dict | Message in HTML                                                                                               |
| text_size              | str       | (optional; default: `'200'`) size of message in percentage                                                    |
| text_color             | str       | (optional; default: `'black'`) color of message (in CSS)                                                      |
| background_color       | str       | (optional; default: `'white'`) background color (in CSS)                                                      |
| seconds                | int, None | (optional; default: `None`) duration to display message. Specify None to show until key press.                |
| manual_check           | bool      | (optional; default: `False`) If set to true, operator can press ESC to fail the test case.                    |
| show_press_button_hint | bool      | (optional; default: `False`) If set to true, will show addition message to ask operators to press the button. |
