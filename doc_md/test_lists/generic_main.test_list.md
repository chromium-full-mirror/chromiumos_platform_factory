# generic_main

## Inherit

- [generic_smt.test_list](generic_smt.test_list.md)
- [generic_fat.test_list](generic_fat.test_list.md)
- [generic_run_in.test_list](generic_run_in.test_list.md)
- [generic_fft.test_list](generic_fft.test_list.md)
- [generic_grt.test_list](generic_grt.test_list.md)

## SyncFactoryServer

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! locals.factory_server_url"
  ```

## FATP

### Serial subtests

- FAT
- RunIn
- FFT
- GRT

## SMT

The stage of tests performed after SMT and before FA.  This is also known as SA (System Assembly) testing.  After SMT, most factories will do System Assembly (SA) and then System Imaging then perform SA Testing.

### run_if

```default
is_engineering_mode or not device.factory.end_SMT
```

### Serial subtests

- SMTStart
- SMTItems
- CheckPoint
- SMTEnd
