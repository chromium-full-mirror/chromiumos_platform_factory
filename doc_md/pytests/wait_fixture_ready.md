# wait_fixture_ready

**Source code:** [wait_fixture_ready.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/wait_fixture_ready.py)

Waits Fixture until it’s ready.

## Description

This test will try to set up a connection to the given fixture, when the
connection is established, the test will pass.  Otherwise, it will keep
retrying.

## Test Procedure

This is an automated test without user interaction.

## Dependency

Depends on how to connect to the fixture, it can be SSH or ADB or something
else.

## Examples

NA.

## Test Arguments

| Name       | Type   | Description                                          |
|------------|--------|------------------------------------------------------|
| class_name | str    | Class name of the BFTFixture implementation to use.  |
| params     | dict   | A dictionary of parameters for the BFTFixture class. |
