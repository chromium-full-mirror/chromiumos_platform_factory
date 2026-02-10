# check_cr50_board_id

**Source code:** [check_cr50_board_id.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/check_cr50_board_id.py)

Check the board ID of the Cr50 firmware.

## Description

This test checks the board ID in the Cr50 firmware matched the given
expectation or not.  The test gains the board ID by invoking gsctool
utility on DUT.

See [https://chrome-internal.googlesource.com/ti50/common/ti50/+/main/docs/board_id_flags.md#values-in-info-pages](https://chrome-internal.googlesource.com/ti50/common/ti50/+/main/docs/board_id_flags.md#values-in-info-pages) for available flags.

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

1. Firstly, this test gets the board ID from the Cr50 firmware.
2. If the argument `board_id_type` is set, the test checks if the
   board ID type field is equal to the argument value or not.
3. If the argument `board_id_flags` is set, the test checks if the
   board ID flags field is equal to the argument value or not.

## Dependency

- DUT link must be ready before running this test.
- gsctool on DUT.

## Examples

To check if the board ID is still unprogrammed, add this in test list:

```default
{
  "pytest_name": "check_cr50_board_id",
  "label": "Assert GSC Board ID Is Unset",
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT"
  ],
  "args": {
    "board_id_type": "ffffffff",
    "board_id_flags": "ffffffff"
  }
}
```

To check if the board ID flags is set to normal prePVT, you can set the argument
`board_id_flags` to PHASE_PREPVT:

```default
{
  "pytest_name": "check_cr50_board_id",
  "label": "Assert GSC Board ID flags is pre-pvt",
  "related_components": [
    "test_tags.TestCategory.SECURE_ELEMENT"
  ],
  "args": {
    "board_id_flags": "PHASE_PREPVT"
  }
}
```

## Test Arguments

| Name           | Type           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|----------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| board_id_type  | int, str, None | (optional; default: `None`) The expected board ID type, can be either an integer or a string of hex code.                                                                                                                                                                                                                                                                                                                                    |
| board_id_flags | int, str, None | (optional; default: `None`) The expected board ID flags, can be either an integer or a string.  If the value is a string, the value can be either the hex code of the board ID flags orPHASE_UNSET for ffffffff, PHASE_UNKNOWN for 0000ff00, PHASE_PREPVT for 00007f7f, PHASE_PVT for 00007f80, PHASE_WHITELABEL_PREPVT for 00003f7f, PHASE_WHITELABEL for 00003f80, PHASE_CUSTOM_LABEL_PREPVT for 00003f7f, PHASE_CUSTOM_LABEL for 00003f80 |
