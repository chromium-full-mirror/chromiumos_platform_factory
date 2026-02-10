# wait_external_test

**Source code:** [wait_external_test.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/wait_external_test.py)

A stub test waiting for external fixture to finish testing.

## Description

If you want to add a test driven by external fixture or instruments and still
want to track test results in Chrome OS Factory Software, this test provides an
easy way for test integration.

This test will check and wait for a file `/run/factory/external/<NAME>` to
be available. If the file content is `PASS` then the test item in test list
will be set as “passed”, otherwise it will fail with the content from file.
Empty file is also considered as failure.

A script is included in factory software toolkit to help doing this:
`bin/factory_external_result`. It needs at least two parameters - `NAME` and
`RESULT`. For example, to pass a `RF1` test, do:

```default
/usr/local/factory/bin/factory_external_result RF1 PASS
```

To fail a `VSWR` test with message, do:

```default
/usr/local/factory/bin/factory_external_result RF1 "Failed to init instrument"
```

In summary, to design and implement a test item with external fixture:

1. Decide a test name, for example `RF1`.
2. In Chrome OS Factory Software test list, add a test item with `pytest_name`
   set to `wait_external_test`, and `run_factory_external_name` argument set
   to the test name.
3. In the fixture side, detect if the DUT is connected. For Chromebooks, this
   is usually done by ethernet dongle. For Android devices, try ADB.
4. Fixture should drive the test and implement all logic and test procedure. To
   access Chromebooks, execute programs using SSH with SSH keys that can be
   authenticated to DUTs (testing_rsa at
   [https://source.chromium.org/chromiumos/chromiumos/codesearch/+/main:chromite/ssh_keys/testing_rsa](https://source.chromium.org/chromiumos/chromiumos/codesearch/+/main:chromite/ssh_keys/testing_rsa)
   or partner_testing_rsa). For Android, use `adb shell`.
5. When the test by fixture is finished, invoke the `factory_external_result`
   to set result or manually create the files under `/run/factory/external`.

## Test Procedure

This is an automated test without user interaction.

When started, the test will wait for specified file to become available,
and pass or fail according to the file content.

The test procure will depend on remote fixture.

## Dependency

None.

## Examples

To add an entry for external fixture with name `RF1`, add this in test list:

```default
{
  "pytest_name": "wait_external_test",
  "args": {
    "run_factory_external_name": "RF1"
  }
}
```

To add a test for external fixture with name `VSWR`, with customized message:

```default
{
  "pytest_name": "wait_external_test",
  "args": {
    "msg": "i18n! Move DUT to station {name}",
    "run_factory_external_name": "VSWR"
  }
}
```

In the fixture side, it should do something like this:

```sh
SSH_KEY=/path/to/ssh_key
TEST_NAME=VSWR
SET_RESULT=/usr/local/factory/bin/factory_external_result
chmod go-rwx "${SSH_KEY}"  # SSH needs private key to be restricted.
ssh root@dut -i "${SSH_KEY}" "${SET_RESULT} ${TEST_NAME} PASS"
```

## Test Arguments

| Name                      | Type      | Description                                                                                                |
|---------------------------|-----------|------------------------------------------------------------------------------------------------------------|
| run_factory_external_name | str       | File name to check in /run/factory/external.                                                               |
| msg                       | str, dict | (optional; default: `{'en-US': 'Please run external test: {name}'}`) Instruction for running external test |
