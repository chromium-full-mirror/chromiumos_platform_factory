# cr50_ap_ro_verification

**Source code:** [cr50_ap_ro_verification.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/cr50_ap_ro_verification.py)

A test to ensure the AP RO verification works.

## Description

The test is to verify the functionality of AP RO verification in early phase
(The hash is usually written in PVT), but not the correctness of the hash.

If the verification failed, then the device won’t be bootable. Reinsert the
battery or cr50 reboot to recover.
To avoid the risk of bricking the DUT, we should try to clear RO hash after
verifying. And it’s recommended to set RO hash by ap_ro_hash.py to make sure
RO hash is set correctly, .

We decided to skip this test when Board ID has already been set. This might
happen when re-flowing or RMA. Details are in ap_ro_hash.py.

## Test Procedure

First round (rebooted flag should be None)
: 1. ccd open.
  2. Trigger the AP RO verification, and the device will reboot.

Second round (rebooted flag should be true)
: 1. Deal with the verification result.

## Dependency

- The verification needs AP RO hash set, or it won’t do anything.
- OS version >= 14704.0.0 (gsctool -aB and gsctool -aB start)
- cr50 version >= 0.5.111 (vendor commands to trigger RO verification)
- In cr50 factory mode to ccd open without physical presence.

## Examples

The feature is decided to be deprecated, no need to add this test item.

## Test Arguments

| Name         | Type   | Description                                                                          |
|--------------|--------|--------------------------------------------------------------------------------------|
| timeout_secs | int    | (optional; default: `5`) How many seconds to wait for the RO verification key combo. |
| manual_test  | bool   | (optional; default: `False`) True to trigger the verification by key combo.          |
