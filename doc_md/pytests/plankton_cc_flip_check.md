# plankton_cc_flip_check

**Source code:** [plankton_cc_flip_check.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/plankton_cc_flip_check.py)

USB type-C CC line polarity check and operation flip test w/ Plankton-Raiden.

## Description

This test flips the polarity bit of the USB type-C. Usually, the test will come
along with other USB type-C test, for example, CC1/CC2 USB performance
(`removable_storage.py`).

Automated test is unstable, you may have to retry. The Plankton-Raiden board
guesses the polarity bit everytime `SetDeviceEngaged()`. Then it tries to
flip the CC polarity to the another side. We have found that we need to charge
the DUT in order to flip, and because of the charge action, the Plankton-Raiden
board guesses the logical polarity bit again (you can find that the polarity is
switching between CC1 and CC2 back-and-forth) and thus the flipping is unstable.

## Test Procedure

This test can be tested manualy with the help from operator or automatically.

For normal USB type-C cable, this is a manual test with the help from operator:

1. Check USB type-C cable connected direction is right by CC polarity
2. Show operation instruction for cable flipping to test another CC line.

For double CC cable, this is an automated test:

- This test can flip CC automatically or you can set Arg
  `double_cc_flip_target` as ‘CC1’ or ‘CC2’ to indicate the final CC
  position.
- If test scheme can guarantee double CC cable connection is not twisted,
  that is, Plankton CC1 is connected to DUT CC1, then it can set Arg
  `double_cc_quick_check` as True to accelerate the test.

## Dependency

- For manual test, you need a normal USB type-C cable to connect with
  Plankton-Raiden board.
- For automated test, you need a double CC cable to connection with
  Plankton-Raiden board.

## Examples

To manual test with a dummy BFTFixture by asking operator to flip the cable,
add this in test list:

```default
{
  "pytest_name": "plankton_cc_flip_check",
  "args": {
    "bft_fixture": {
      "class_name":
        "cros.factory.test.fixture.dummy_bft_fixture.DummyBFTFixture",
      "params": {}
    },
    "ask_flip_operation": true,
    "usb_c_index": 0,
    "state_src_ready": "SNK_READY"
  }
}
```

Automated test with a dolphin BFTFixture and flipping the polarity to CC1:

```default
{
  "pytest_name": "plankton_cc_flip_check",
  "args": {
    "bft_fixture": {
      "class_name":
        "cros.factory.test.fixture.dummy_bft_fixture.DummyBFTFixture",
      "params": {}
    },
    "double_cc_flip_target": "CC1",
    "usb_c_index": 1,
    "state_src_ready": "SNK_READY"
  }
}
```

## Test Arguments

| Name                      | Type      | Description                                                                                                                                                                                                                                                                                                                           |
|---------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bft_fixture               | dict      | A dictionary with the following items:<br/><br/>> `class_name`<br/>> : Fully-qualified class name of the BFTFixture implementation<br/>>   to use.<br/><br/>> `params`<br/>> : A dictionary of parameters for the BFTFixture class’s `Init()`<br/>>   method.<br/><br/>The default value of `None` means that no BFT fixture is used. |
| adb_remote_test           | bool      | (optional; default: `False`) Run test against remote ADB target.                                                                                                                                                                                                                                                                      |
| usb_c_index               | int       | Index of DUT USB_C port                                                                                                                                                                                                                                                                                                               |
| original_enabled_cc       | str, None | (optional; default: `None`) Set “CC1” or “CC2” if you want to check what CC pin is enabled now. There is no check if it is not set.                                                                                                                                                                                                   |
| ask_flip_operation        | bool      | (optional; default: `False`) Determine whether to ask operator to flip cable.                                                                                                                                                                                                                                                         |
| double_cc_flip_target     | str, None | (optional; default: `None`) If using double CC cable, set either “CC1” or “CC2” for the target to flip. Flip anyway if this is not set.                                                                                                                                                                                               |
| double_cc_quick_check     | bool      | (optional; default: `False`) If using double CC cable, set True if you guarantee CC pair is not reversed. CC polarity in Plankton side implies DUT side.                                                                                                                                                                              |
| timeout_secs              | int       | (optional; default: `0`) Timeout seconds for operation, set 0 for operator pressing enter key to finish operation.                                                                                                                                                                                                                    |
| state_src_ready           | int, str  | (optional; default: `22`) State number of pd state SRC_READY.                                                                                                                                                                                                                                                                         |
| wait_dut_reconnect_secs   | int       | (optional; default: `5`) Wait DUT to reconnect for n seconds after CC flip. This is required if remote DUT might be disconnected a while after CC flip, e.g. DUT has no battery and will reboot on CC flip. If n equals to 0, will wait forever.                                                                                      |
| init_cc_state_retry_times | int       | (optional; default: `3`) Retry times for init CC state.                                                                                                                                                                                                                                                                               |
