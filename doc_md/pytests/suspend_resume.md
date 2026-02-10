# suspend_resume

**Source code:** [suspend_resume.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/suspend_resume.py)

Suspend and resume device with given cycles.

## Description

Suspends and resumes the device an adjustable number of times for
adjustable random lengths of time.

## Test Procedure

This is an automated test without user interaction.

When started, the test will try to suspend and resume by given arguments.
Will fail if device wakes too early, or if unexpected reboot (or crash) found.

## Dependency

- rtc’s `wakealarm` entry in `sysfs`.
- `check_powerd_config` if the argument `suspend_type` is not set.

Note that the rtc sysfs entry may vary from device to device, so the test_list
must define the path to the correct sysfs entry for the specific device, the
default assumes a typical `/sys/class/rtc/rtc0` entry.

## Examples

To suspend/resume in 1 cycle, suspend in 5~10 seconds, resume in 5~10 seconds,
and suspend to memory (see more criteria from arguments):

```default
{
  "pytest_name": "suspend_resume"
}
```

## Test Arguments

| Name                         | Type      | Description                                                                                                                      |
|------------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------|
| cycles                       | int       | (optional; default: `1`) Number of cycles to suspend/resume                                                                      |
| suspend_delay_max_secs       | int       | (optional; default: `10`) Max time in sec during suspend per cycle                                                               |
| suspend_delay_min_secs       | int       | (optional; default: `5`) Min time in sec during suspend per cycle                                                                |
| resume_delay_max_secs        | int       | (optional; default: `10`) Max time in sec during resume per cycle                                                                |
| resume_delay_min_secs        | int       | (optional; default: `5`) Min time in sec during resume per cycle                                                                 |
| suspend_time_margin_min_secs | int       | (optional; default: `0`) Min seconds of the (actual - expected) suspended time diff                                              |
| suspend_time_margin_max_secs | int       | (optional; default: `30`) Max seconds of the (actual - expected) suspended time diff                                             |
| suspend_worst_case_secs      | int       | (optional; default: `60`) The worst case time a device is expected to take to suspend                                            |
| wakealarm_path               | str       | (optional; default: `'/sys/class/rtc/rtc0/wakealarm'`) Path to the wakealarm file                                                |
| time_path                    | str       | (optional; default: `'/sys/class/rtc/rtc0/since_epoch'`) Path to the time (since_epoch) file                                     |
| wakeup_count_path            | str       | (optional; default: `'/sys/power/wakeup_count'`) Path to the wakeup_count file                                                   |
| suspend_type                 | str, None | (optional; default: `None`) Suspend type.  The default is to use `freeze` if the platform supports it, or `mem` for other cases. |
| ignore_wakeup_source         | str, None | (optional; default: `None`) Wakeup source to ignore                                                                              |
| early_resume_retry_wait_secs | int       | (optional; default: `3`) Time to wait before re-suspending after early resume                                                    |
| ensure_wakealarm_cleared     | bool      | (optional; default: `True`) Raise exception if wakealarm is not cleared after resume                                             |
