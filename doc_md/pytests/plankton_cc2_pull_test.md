# plankton_cc2_pull_test

**Source code:** [plankton_cc2_pull_test.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/plankton_cc2_pull_test.py)

Plankton USB type-C CC2 function test for Whale fixture.

Pull high C[0/1]_CC2_DUT on Whale Krill and check PD GPIO reponse to test
USB type-C CC2 functionailty. Note that during pull-high test USB type-C port
should be disconnected.

## Test Arguments

| Name                 | Type   | Description                                                                                                                                                                                                                                                                                                                           |
|----------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| whale_bft_fixture    | dict   | A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| plankton_bft_fixture | dict   | A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| usb_c_index          | int    | Index of DUT USB type-C port                                                                                                                                                                                                                                                                                                          |
| disconnect_manually  | bool   | (optional; default: `False`) Ask for operation to disconnect Plankton cable (just for debug usage)                                                                                                                                                                                                                                    |
| disconnect_secs      | int    | (optional; default: `5`) Interval for USB type-C port disconnection.                                                                                                                                                                                                                                                                  |
