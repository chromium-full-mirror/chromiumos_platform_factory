# compass

**Source code:** [compass.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/compass.py)

Compass test which requires operator place the DUT heading north and south.

## Test Arguments

| Name      | Type            | Description                                                 |
|-----------|-----------------|-------------------------------------------------------------|
| tolerance | int             | (optional; default: `5`) The tolerance in degree.           |
| location  | [‘base’, ‘lid’] | (optional; default: `'base'`) Where the compass is located. |
