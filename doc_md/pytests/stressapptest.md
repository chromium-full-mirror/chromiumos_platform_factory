# stressapptest

**Source code:** [stressapptest.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/stressapptest.py)

A test to stress CPU, memory and disk.

## Description

A test using [stressapptest](https://github.com/stressapptest/stressapptest)
to stress CPU, memory, and disk.

By default the system data partition (or the stateful partition for Chrome OS
devices) is used. However a long stress testing of disk may shorten eMMC or SSD
life, so you may want to set disk_thread argument to False if seconds is
pretty long.

Setting memory ratio may be tricky. If your system does not have enough free
memory (for example if you have lots of tests running in parallel) then the test
will fail, so usually you’ll want to set free_memory_only argument to True.

However, if you start multiple tests at same time, other tests may allocate more
memory after the calculation of “free memory” is done, causing the test to fail.
To solve that, increase the argument wait_secs so the calculation of “free
memory” will be done when the memory usage is stabilized.

### Internal references

- go/memory-testing-with-stressapptest

## Test Procedure

This is an automated test without user interaction.

Start the test and it will run for the time specified in argument seconds, and
pass if no errors found; otherwise fail with error messages and logs, especially
if unexpected reboot or crash were found during execution.

## Dependency

- Need external program [stressapptest](https://github.com/stressapptest/stressapptest).

## Examples

To stress CPU, memory (90% of free memory), and the disk using stateful
partition for 60 seconds. According to go/memory-testing-with-stressapptest,
running the tests with disk generates more unusual memory traffic:

```default
{
  "pytest_name": "stressapptest",
  "label": "Stress App Test",
  "exclusive_resources": [
    "CPU"
  ],
  "related_components": [
    "test_tags.TestCategory.BRIDGE_PCIE_EMMC",
    "test_tags.TestCategory.CPU",
    "test_tags.TestCategory.DRAM",
    "test_tags.TestCategory.STORAGE"
  ]
}
```

To stress CPU and memory (90% of free memory) without disk:

```default
{
  "pytest_name": "stressapptest",
  "label": "Stress App Test Only CPU And Memory",
  "exclusive_resources": [
    "CPU"
  ],
  "related_components": [
    "test_tags.TestCategory.BRIDGE_PCIE_EMMC",
    "test_tags.TestCategory.CPU",
    "test_tags.TestCategory.DRAM",
    "test_tags.TestCategory.STORAGE"
  ],
  "args": {
    "disk_thread": false
  }
}
```

To stress CPU, memory (90% of free memory), and the disk using stateful
partition for one day:

```default
{
  "pytest_name": "stressapptest",
  "label": "Stress App Test For One Day",
  "exclusive_resources": [
    "CPU"
  ],
  "related_components": [
    "test_tags.TestCategory.BRIDGE_PCIE_EMMC",
    "test_tags.TestCategory.CPU",
    "test_tags.TestCategory.DRAM",
    "test_tags.TestCategory.STORAGE"
  ],
  "args": {
    "seconds": 86400
  }
}
```

To stress using only two threads, and only run on cpu core 2 and 3:

```default
{
  "pytest_name": "stressapptest",
  "args": {
    "num_threads": 2,
    "taskset_args": ["-c", "2,3"]
  }
}
```

To specify the minimum cpu frequency to 600 MHz, and the maximum cpu frequency
to 3000 MHz when running stressapptest, and recover to original cpu frequency
after the test:

```default
{
  "pytest_name": "stressapptest",
  "args": {
    "scaling_min_freq": 600000,
    "scaling_max_freq": 3000000
  }
}
```

## Test Arguments

| Name             | Type       | Description                                                                                                                               |
|------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| seconds          | int        | (optional; default: `60`) Time to execute the stressapptest.                                                                              |
| memory_ratio     | float      | (optional; default: `0.9`) Radio of memory to be used by stressapptest.                                                                   |
| free_memory_only | bool       | (optional; default: `True`) Only use free memory for test. When set to True, only memory_radio \* free_memory are used for stressapptest. |
| wait_secs        | int        | (optional; default: `0`) Time to wait in seconds before executing stressapptest.                                                          |
| disk_thread      | bool       | (optional; default: `True`) Stress disk using -f argument of stressapptest.                                                               |
| disk_thread_dir  | str, None  | (optional; default: `None`) Directory of disk thread file will be placed (default to system stateful partition.)                          |
| max_errors       | int        | (optional; default: `1000`) Number of errors to exit early.                                                                               |
| num_threads      | int, None  | (optional; default: `None`) Number of threads to be used. Default to number of cores.                                                     |
| taskset_args     | list, None | (optional; default: `None`) Argument to taskset to change CPU affinity for stressapptest.                                                 |
| scaling_min_freq | int, None  | (optional; default: `None`) Argument to set the value of scaling_min_freq.                                                                |
| scaling_max_freq | int, None  | (optional; default: `None`) Argument to set the value of scaling_max_freq.                                                                |
| scaling_governor | str, None  | (optional; default: `None`) Argument to set the value of scaling_governor.                                                                |
