# bft_fixture

**Source code:** [bft_fixture.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/bft_fixture.py)

A generic interface to control the BFT fixture.

## Test Arguments

| Name        | Type             | Description                                                                                                                                                                                                                                                                                                                           |
|-------------|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bft_fixture | dict             | A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| method      | str              | BFTFixture method to call.                                                                                                                                                                                                                                                                                                            |
| args        | list             | (optional; default: `[]`) args of the method.                                                                                                                                                                                                                                                                                         |
| retry_secs  | int, float, None | (optional; default: `None`) retry interval in seconds (or None for no retry)                                                                                                                                                                                                                                                          |
