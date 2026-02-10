# cr50_ap_ro_hash

**Source code:** [cr50_ap_ro_hash.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/cr50_ap_ro_hash.py)

A test to set/clear AP RO hash.

## Description

When re-flowing, RO hash can’t be modified since board ID is set.
We decided to skip this test with the following assumptions: (might hold in
most cases, but not always)
- If board ID is set, then DUT must have been finalized.
- AP RO verification is always tested before finalization, and this feature
won’t be broken after that.
- Even if the hash is set in cr50, the verification will always fail since
the stored hash is calculated with gbb flags 0, which is not the same as the
gbb flags we use in the factory.

## Test Procedure

These steps describe the whole procedure of AP RO verification test.
1. Set RO hash to be verified.
2. Verify RO hash by ap_ro_verification.py.
3. Clear RO Hash after verifying.

## Dependency

- The test will set/clear RO hash, which needs board ID not being set on DUT.

## Examples

The feature is decided to be deprecated, no need to add this test item.

## Test Arguments

| Name   | Type   | Description                                 |
|--------|--------|---------------------------------------------|
| action | str    | The action for AP RO hash (‘set’, ‘clear’). |
