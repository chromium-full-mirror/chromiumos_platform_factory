# generic_storage_examples

Examples for testing storage components.

## Inherit

- [generic_storage.test_list](generic_storage.test_list.md)

## BadBlocks2GB

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
  2147483648
  ```

## BadBlocksForceOnSSD

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

`force_badblocks_on_ssd`
: ```default
  true
  ```

## BadBlocksForceOnSSD10MB

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
  10240
  ```

`force_badblocks_on_ssd`
: ```default
  true
  ```

## StorageSimpleStress

### pytest_name

[storage_simple_stress](../pytests/storage_simple_stress.md)

### args

`operations`
: ```default
  1
  ```

`dir`
: ```default
  "/home/root"
  ```

`file_size`
: ```default
  10485760
  ```

## StorageSimpleStress3Times

### pytest_name

[storage_simple_stress](../pytests/storage_simple_stress.md)

### args

`operations`
: ```default
  3
  ```

`dir`
: ```default
  "/home/root"
  ```

`file_size`
: ```default
  10485760
  ```

## StorageTests

### Serial subtests

- ProbeStorage
- BadBlocks
- [BadBlocks2GB]()
- [BadBlocksForceOnSSD]()
- [BadBlocksForceOnSSD10MB]()
- [StorageSimpleStress]()
- [StorageSimpleStress3Times]()
- VerifyRootPartition
