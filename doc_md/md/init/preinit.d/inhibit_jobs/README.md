**source code:** [init/preinit.d/inhibit\_jobs/README.md](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/init/preinit.d/inhibit_jobs/README.md)

# ChromeOS Factory Software: Inhibit Upstart Jobs

To inhibit an Upstart job (`/etc/init/*.conf`) from execution, add a file using
job name and describe why we want to disable it as file content. The job will be
disabled by `/usr/share/cros/factory_utils.sh`.

To start these jobs, execute

```default
run_inhibited_job <JOBNAME>
```

## Examples

To stop `powerd`, create a file `powerd` with following contents:

```default
In factory environment, we need to disable powerd so run-in tests (and many
non-interactive tests) will not fall into suspended mode.  Also we need to
disable powerd to access power button (and being able to close lid).
```

To start `powerd` maually, do:

```default
run_inhibited_job powerd
```
