# suspend_stress

**Source code:** [suspend_stress.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/suspend_stress.py)

Suspend and resume device with given cycles.

## Description

Suspends and resumes the device an adjustable number of times for adjustable
random lengths of time.
See `suspend_stress_test` for more details.

## Test Procedure

This is an automated test without user interaction.

When started, the test will try to suspend and resume by given arguments.
Will fail if unexpected reboot, crash or error found.

## Dependency

- power manager `powerd`.
- power manager tool `suspend_stress_test`.

## Examples

To suspend/resume in 1 cycle, suspend in 5~10 seconds, resume in 5~10 seconds,
and suspend to idle by writing freeze to `/sys/power/state`:

```default
{
  "pytest_name": "suspend_stress"
}
```

## Test Arguments

| Name                         | Type      | Description                                                                          |
|------------------------------|-----------|--------------------------------------------------------------------------------------|
| cycles                       | int       | (optional; default: `1`) Number of cycles to suspend/resume                          |
| suspend_delay_max_secs       | int       | (optional; default: `10`) Max time in sec during suspend per cycle                   |
| suspend_delay_min_secs       | int       | (optional; default: `5`) Min time in sec during suspend per cycle                    |
| resume_delay_max_secs        | int       | (optional; default: `10`) Max time in sec during resume per cycle                    |
| resume_delay_min_secs        | int       | (optional; default: `5`) Min time in sec during resume per cycle                     |
| suspend_time_margin_min_secs | int       | (optional; default: `0`) Min seconds of the (actual - expected) suspended time diff  |
| suspend_time_margin_max_secs | int       | (optional; default: `30`) Max seconds of the (actual - expected) suspended time diff |
| ignore_wakeup_source         | str, None | (optional; default: `None`) Wakeup source to ignore                                  |
| backup_rtc                   | bool      | (optional; default: `False`) Use second rtc if present for backup                    |
| memory_check                 | bool      | (optional; default: `False`) Use memory_suspend_test to suspend                      |
| memory_check_size            | int       | (optional; default: `0`) Amount of memory to allocate (0 means as much as possible)  |
| fw_errors_fatal              | bool      | (optional; default: `True`) Abort on firmware errors                                 |
| premature_wake_fatal         | bool      | (optional; default: `True`) Abort on any premature wakes from suspend                |
| late_wake_fatal              | bool      | (optional; default: `True`) Abort on any late wakes from suspend                     |
| pre_suspend_command          | str       | (optional; default: `''`) Command to run before each suspend                         |
| post_resume_command          | str       | (optional; default: `''`) Command to run after each resume                           |
