# tpm_diagnosis

**Source code:** [tpm_diagnosis.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/tpm_diagnosis.py)

Runs tpm_selftest to perform TPM self-diagnosis.

## Description

This test stopped working after the tpm_selftest being removed.

### Internal references

- b/35577239

## Test Procedure

This is an automatic test that doesn’t need any user interaction.

## Dependency

- /usr/local/sbin/tpm_selftest

## Examples

An example:

```default
{
  "pytest_name": "tpm_diagnosis"
}
```

## Test Arguments

| Name            | Type   | Description                                                                         |
|-----------------|--------|-------------------------------------------------------------------------------------|
| tpm_selftest    | str    | (optional; default: `'/usr/local/sbin/tpm_selftest'`) Path of tpm_selftest program. |
| tpm_args        | list   | (optional; default: `['-l', 'debug']`) List of tpm_selftest args.                   |
| success_pattern | str    | (optional; default: `'tpm_selftest succeeded'`) Pattern of success.                 |
