# verify_component

**Source code:** [verify_component.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/verify_component.py)

Verify peripheral components.

Verify the number of components from probed results and from device data
are the same. And verify the status of components are supported when the
phase is PVT or PVT_DOGFOOD.

## Test Arguments

| Name                  | Type   | Description                                                                    |
|-----------------------|--------|--------------------------------------------------------------------------------|
| approx_match          | bool   | (optional; default: `True`) Enable apporximate matching results.               |
| enable_factory_server | bool   | (optional; default: `True`) Update hwid data from factory server.              |
| max_mismatch          | int    | (optional; default: `1`) The number of mismatched rules at most.               |
| verify_checksum       | bool   | (optional; default: `True`) Enable converted statements checksum verification. |
