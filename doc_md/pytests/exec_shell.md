# exec_shell

**Source code:** [exec_shell.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/exec_shell.py)

A test to invoke a list of shell commands.

## Description

This test will execute the shell commands given from argument `commands` one
by one, and fail if any of the return value is non-zero.

By default the commands are executed on DUT (specified by Device API). If you
need to run on station (usually local), set argument `is_station` to True.

The working directory for the commands is given by argument `working_dir`,
which default is `.`, i.e. the current working directory.  Set
`working_dir=None` if you want this test to create a temporary working
directory and remove it after the test is finished.

If argument `attachment_name` is specified, the log files specified from
argument `attachment_path` will be archived (using tar+gz) and uploaded as an
attachment via TestLog.

If `attachment_path` is empty, the command working directory will be
used.  In other words, we are doing something like this shell script:

```bash
#!/bin/sh
DIR="${WORKING_DIR:-$(mktemp -d)}"
TARBALL="$(mktemp --suffix=.tar.gz)"
( cd "${DIR}"; "$@"; tar -zcf "${TARBALL}" ./ )
echo "Log is generated in ${TARBALL}."
```

And `$@` will be replaced by the `commands` argument. To test if your logs
will be created properly, save the snippet above as `test.sh`, then run it
with your commands, for example:

```default
(WORKING_DIR=somewhere ./test.sh
 /usr/local/factory/third_party/some_command some_arg)
```

## Test Procedure

This is an automated test without user interaction.

Start the test and it will run the shell commands specified, one by one; and
fail if any of the command returns false.

If `attachment_name` is specified, after all commands are finished (or if any
command failed), the results will be archived and saved to TestLog.

## Dependency

The test uses system shell to execute commands, which may be different per
platform. Also, the command may be not always available on target system.
You have to review each command to check if that’s provided on DUT.

If `attachment_name` is specified, the DUT must support `tar` command with
`-zcf` arguments.

## Examples

To add multiple ports to iptables, add this in test list:

```default
{
  "pytest_name": "exec_shell",
  "args": {
    "commands": [
      "iptables -A input -p tcp --dport 4020",
      "iptables -A input -p tcp --dport 4021",
      "iptables -A input -p tcp --dport 4022"
    ]
  }
}
```

To load module ‘i2c-dev’ (and never fails), add this in test list:

```default
{
  "pytest_name": "exec_shell",
  "args": {
    "commands": "modprobe i2c-dev || true"
  }
}
```

Echo a message and dump into a temp folder as working directory then save the
files in TestLog attachment:

```default
{
  "pytest_name": "exec_shell",
  "args": {
    "working_dir": None,
    "commands": "echo test >some.output",
    "attachment_name": "logtest"
  }
}
```

Echo a message and dump into an existing folder then save the files in TestLog
attachment:

```default
{
  "pytest_name": "exec_shell",
  "args": {
    "working_dir": "/usr/local/factory/my_log",
    "commands": "echo test >some.output",
    "attachment_name": "logtest"
  }
}
```

## Test Arguments

| Name               | Type            | Description                                                                                                                                                                                                   |
|--------------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| commands           | list, str       | A list (or one simple string) of shell commands to execute.                                                                                                                                                   |
| is_station         | bool            | (optional; default: `False`) Run the given commands on station (usually local host) instead of DUT, for example preparing connection configuration.                                                           |
| working_dir        | None, str       | (optional; default: `'.'`) Path name of the working directory for running the commands. If set to `None`, a temporary directory will be used.                                                                 |
| attachment_name    | str, None       | (optional; default: `None`) File base name for collecting and creating testlog attachment. None to skip creating attachments.                                                                                 |
| log_command_output | bool            | (optional; default: `True`) Log the executed results of each commands, which includes stdout,stderr and the return code.                                                                                      |
| attachment_path    | str, None       | (optional; default: `None`) Source path for collecting logs to create testlog attachment. None to run commands in a temporary folder and attach everything created, otherwise tar everything from given path. |
| source_codes       | list, str, None | (optional; default: `None`) A list (or single path) of source codes to log.                                                                                                                                   |
