# storage_simple_stress

**Source code:** [storage_simple_stress.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/storage_simple_stress.py)

Performs consecutive read/write operations on a single file.

## Description

This pytest performs consecutive read/write operations on a single file under a
specific directory or mount point. The primary purpose is to keep storage busy
for some reliability test. It can also be used as a simple approach to stress a
storage device as well.

Since it operates on a single file under user space, controls over which block
is exercising are limited (e.g., it might always write on the same block.)
In this sense, this test should be considered as a test with limited coverage.

Also noted that, an unexpected abortion will leave the temporary file uncleaned
in the specified directory or mount point.

Please also refer to the pytest removable_storage, which might also be useful
to test a storage device.

## Test Procedure

This is an automated test without user interaction.

## Dependency

Use toybox and dd to perform read/write operations.
Use /dev/urandom to generate random data for write.

## Examples

To test read/write of a 10MB file under /home/root:

<!-- test_list:

generic_storage_examples:StorageTests.StorageSimpleStress -->

To test read/write of a 10MB file 3 times:

<!-- test_list:

generic_storage_examples:StorageTests.StorageSimpleStress3Times -->

## Test Arguments

| Name         | Type      | Description                                                                                                                                                                                                                  |
|--------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dir          | str       | Directory for creating files for random access.                                                                                                                                                                              |
| file_size    | int       | The file size of generated file.                                                                                                                                                                                             |
| operations   | int       | The number of operations to perform.                                                                                                                                                                                         |
| mount_device | str, None | (optional; default: `None`) If not None, we mount the given device first to a temp directory, and perform reading / writing under the directory. The arugment ‘dir’ will be used as the relative path under the mount point. |
