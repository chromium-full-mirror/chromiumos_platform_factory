# download_from_factory_drive

**Source code:** [download_from_factory_drive.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/download_from_factory_drive.py)

Retrieve factory drive files from factory server.

## Description

This pytest retrieves files uploaded to factory drive space on factory server.
Pytests with freuquenly modified config files can use this test to download
latest configs before running tests.

To locate config files, assign `source_namespace` to directory path of files
relatively to root directory(i.e. `Current directory` on factory server) and
assign `source_file` to config file name. If targeting all files under given
namespace, no need to assign `source_file`.

To store config files, assign `destination_namespace` to an absolute path on
target machine(e.g. DUT, test station). Default is `/tmp`.

## Test Procedure

Make sure DUT is connected to factory server, and files are uploaded to server.
Wait for the files to be downloaded.

## Dependency

Nothing special.
This test uses only server components in Chrome OS Factory Software.

## Examples

Assume updating config file `testplan.csv` for `rf_graphyte` test, and this
file is uploaded to `graphyte` namespace on factory server. Destination path
on test station is `/usr/local/graphyte/config_files`.

The JSON config with main pytest can be:

```default
{
  "subtests": [
    {
      "pytest_name": "download_from_factory_drive",
      "args": {
        "source_namespace": "/graphyte",
        "source_file": "testplan.csv",
        "destination_namespace": "/usr/local/graphyte/config_files"
      }
    },
    "rf_graphyte"
  ]
}
```

Assume updating files `vswr_config.yaml` and `vswr_config_postpress.yaml`
for `vswr` test. These files should be uploaded to a directory path on factory
server, and suppose this directory is `dut1/vswr`. Destination path on DUT for
these files is `/usr/local/factory/py/test/pytests/vswr`.

The JSON config with main pytest can be:

```default
{
  "subtests": [
    {
      "pytest_name": "download_from_factory_drive",
      "args": {
        "source_namespace": "/dut1/vswr",
        "destination_namespace": "/usr/local/factory/py/test/pytests/vswr"
      }
    },
    "vswr"
  ]
}
```

## Test Arguments

| Name                  | Type      | Description                                                                                                  |
|-----------------------|-----------|--------------------------------------------------------------------------------------------------------------|
| source_namespace      | str       | (optional; default: `'/'`) The path to retrieve parameter files.                                             |
| source_file           | str, None | (optional; default: `None`) Target parameter file name; `None` if targeting all files under given namespace. |
| destination_namespace | str       | (optional; default: `'/tmp'`) The path on DUT to save parameter files to.                                    |
| timeout_secs          | int       | (optional; default: `600`) How many seconds to wait for the download.                                        |
