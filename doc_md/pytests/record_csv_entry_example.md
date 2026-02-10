# record_csv_entry_example

**Source code:** [record_csv_entry_example.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/record_csv_entry_example.py)

An example pytest to show case how to save a CSV entry.

## Description

This is an example pytest. The pytest calls `csv_utils.CSVManager.Append` to
store an entry on the device. This pytest doesn’t need to have the internet
access.

Later in the factory flow, when running the sync_factory_server pytest, if
`upload_csv_entries` is set, it uploads all previously recorded CSV entries to
the Google factory server.

## Test Procedure

The test first do some measurements to collect data. Then call
`csv_utils.CSVManager.Append` to store them.

## Dependency

Nothing special

## Examples

Here is a simple example:

```default
{
  "pytest_name": "record_csv_entry_example"
},
{
  "pytest_name": "sync_factory_server",
  "args": {
    "upload_csv_entries": true
  }
}
```

## Test Arguments

This test does not have any arguments.
