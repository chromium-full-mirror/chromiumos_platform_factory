# summary

**Source code:** [summary.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/summary.py)

Displays a status summary for all tests in the current section.

## Description

This is a test to display a summary of test results in same test group.
The summary includes tests up to, but not including, this test itself.

For example, if the test tree is:

```default
SMT
  ...
Runin
  A
  B
  C
  report (this test)
  shutdown
```

Then this test will show the status summary for A, B, and C. No shutdown.

This test is often used as a “barrier” or “check point” when the argument
`disable_input_on_fail` is set, since operators can’t skip to next test item
when the overall status is not PASSED.

Moreover, if argument `pass_without_prompt` is `True`, the test will pass
silently and move to next test item without user interaction. This is usually
known as “Barrier” mode. Otherwise, it’ll prompt the given message and wait for
input, which is known as “Check Point” mode.

## Test Procedure

1. If all previous tests in same group are passed, this test will display
   nothing and simply pass when argument `pass_without_prompt` is True,
   otherwise display a table of test names and results, prompt the given (or
   default) message and wait for input to pass or fail.
2. Otherwise, if any previous tests in same group failed, a table listing test
   names and results will be displayed. Depends on argument
   `disable_input_on_fail`, operator may choose to continue or will stay in
   failure screen.

## Dependency

None.

## Examples

To list previous tests in same group, and always prompt and wait for input to
decide if we can move on, add this in test list:

```default
{
  "pytest_name": "summary"
}
```

To only stop when any previous tests in same group has failed (“Barrier”):

```default
{
  "pytest_name": "summary",
  "allow_reboot": true,
  "disable_abort": true,
  "args": {
    "disable_input_on_fail": true,
    "pass_without_prompt": true
  }
}
```

To always prompt but only pass if all previous tests in same group passed
(“Check Point”):

```default
{
  "pytest_name": "summary",
  "allow_reboot": true,
  "disable_abort": true,
  "args": {
    "prompt_message": "i18n! Press space to shutdown.",
    "disable_input_on_fail": true,
    "pass_without_prompt": false
  }
}
```

## Test Arguments

| Name                      | Type       | Description                                                                                                                                                                                                                                                   |
|---------------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| prompt_message            | str, dict  | (optional; default: `{'en-US': 'Click or press SPACE to continue'}`) Prompt message in HTML when all tests passed                                                                                                                                             |
| disable_input_on_fail     | bool       | (optional; default: `False`) Disable user input to pass/fail when the overall status is not PASSED                                                                                                                                                            |
| pass_without_prompt       | bool       | (optional; default: `False`) If all tests passed, pass this test without prompting                                                                                                                                                                            |
| bft_fixture               | dict, None | (optional; default: `None`) BFT fixture arguments (see bft_fixture test).  If provided, then a red/green light is lit to indicate failure/success rather than showing the summary on-screen.  The test does not fail if unable to connect to the BFT fixture. |
| accessibility             | bool       | (optional; default: `False`) Display bright red background when the overall status is not PASSED                                                                                                                                                              |
| include_parents           | bool       | (optional; default: `False`) Recursively include parent groups in summary                                                                                                                                                                                     |
| run_factory_external_name | str, None  | (optional; default: `None`) Notify DUT that external test is over, will use DUT interface to write result file under /run/factory/external/<NAME>.                                                                                                            |
| screensaver_timeout       | int, None  | (optional; default: `None`) Timeout in seconds to turn on the screensaver, set to `None` to disable the screensaver.                                                                                                                                          |
