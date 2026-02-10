# line_check_item

**Source code:** [line_check_item.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/line_check_item.py)

A factory test to interactively check a sequence of shell commands on DUT.

## Description

This test is very similar to `exec_shell` test, except that
`line_check_item` has the ability to get operator confirmation no matter if
the shell command success or not.

If you simply want to run few commands (and fail if the return value is
non-zero), especially if you need to run commands on host or station, use
`exec_shell`.

If you simply want to run few commands and don’t care if the commands success
or not, use `exec_shell` and add `'|| true'` for all commands.

If you are running some commands and some (at least one) commands need operator
to judge if that passed or not manually (for example checking if some LED has
lightened properly), use `line_check_item`.

`line_check_item` evaluates and executes the given `items` argument, where
each item is a sequence with 3 elements (instruction, command, judge_to_pass):

1. `instruction`: A string passed to `i18n.Translated` to display on UI.
2. `command`: A sequence or str as shell command to be passed to dut.Popen.
3. `judge_to_pass`: A boolean value to indicate if these commands need user to
   judge pass or failure, even if the command returns zero (success).

## Test Procedure

The test will go through each item and:

1. Display instruction on UI.
2. Execute command.
3. If judge_to_pass is True, wait for operator to confirm if passed or not.

## Dependency

The commands specified in items must be available on DUT.

## Examples

To turn on a ‘lightbar’ component and wait for confirmation, add this to test
list:

```default
{
  "pytest_name": "line_check_item",
  "args": {
    "items": [
      ["i18n! Initialization", "lightbar init", false],
      ["i18n! Turn on lightbar", "lightbar enable", true],
      ["i18n! Clean up", "lightbar reset", false]
    ],
    "title": "i18n! LED Test"
  }
}
```

## Test Arguments

| Name       | Type      | Description                                                                                                                                         |
|------------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| title      | str, dict | test title.                                                                                                                                         |
| items      | list      | A sequence of items to check. Each item is a sequence:  [instruction, command, judge_to_pass].                                                      |
| is_station | bool      | (optional; default: `False`) Run the given commands on station (usually local host) instead of DUT, for example preparing connection configuration. |
