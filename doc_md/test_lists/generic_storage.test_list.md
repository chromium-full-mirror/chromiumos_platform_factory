# generic_storage

Predefined storage tests.

## Inherit

- [base.test_list](base.test_list.md)

## BadBlocks

When run alone, this takes ~.5s/MiB (for four passes).  We’ll do a gigabyte, which takes about 9 minutes.

### pytest_name

[bad_blocks](../pytests/bad_blocks.md)

### args

`timeout_secs`
: ```default
  120
  ```

`log_threshold_secs`
: ```default
  10
  ```

`max_bytes`
: ```default
  1073741824
  ```

## ProbeStorage

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "storage"
  ]
  ```

`config_file`
: ```default
  "/usr/local/factory/py/hwid/v3/default_probe_statement.json"
  ```

`overridden_rules`
: ```default
  [
    [
      "storage",
      ">",
      0
    ]
  ]
  ```

## VerifyRootPartition

### pytest_name

[verify_root_partition](../pytests/verify_root_partition.md)

### args

`max_bytes`
: ```default
  1048576
  ```
