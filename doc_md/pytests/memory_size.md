# memory_size

**Source code:** [memory_size.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/memory_size.py)

Test if the memory size is correctly written in the firmware.

## Description

Linux kernel trusts the available memory region specified from firmware, via
ACPI or Device Tree. However, it is possible for the firmware to send wrong
values, for example always only assigning 8GB for kernel while the system
has 16GB memory installed.

On traditional PC, the memory information is stored on SPD chipset on memory
module so firmware should read and claim free space for kernel according to SPD.
On modern Chromebooks, the SPD is replaced by a pre-defined mapping table and
decided by straps. When the mapping table is out-dated, for example if an old
firmware is installed, then the allocated memory for kernel would be wrong.

The Chrome OS command, `mosys`, can read from physical or virtual SPD and
report expected memory size. So this test tries to compare the value from
`mosys` and kernel `meminfo` to figure out if firmware has reported wrong
memory size for kernel.

Usually firmware has to reserve some memory, for example ACPI tables, DMA,
I/O port mappings, so the kernel is expected to get less memory. This is
specified by argument `max_diff_ratio`.

Meanwhile, for virtual SPD, it is possible that both firmware and `mosys` have
out-dated information of memory straps, so optionally we support a third source,
the shopfloor backend, to provide memory size.

If argument `device_data_key` is set, we will also check memory size by the
information from device data (usually retrieved from shopfloor backend if
factory supports it).

## Test Procedure

This is an automated test without user interaction.

When started, the test collects memory size information from different source
and fail if the difference is too large.

## Dependency

- Command `mosys`: `mosys -k memory spd print geometry`.
- Kernel to support `/proc/meminfo`, search for string `MemTotal`.
- Optionally, shopfloor integration to save memory in device data.

## Examples

To compare and check the memory size from `mosys` and kernel:

```default
{
  "pytest_name": "memory_size",
  "label": "Memory Size",
  "related_components": [
    "test_tags.TestCategory.DRAM"
  ]
}
```

To compare and check the memory size from `mosys` and kernel, with difference
up to 30 percent:

```default
{
  "pytest_name": "memory_size",
  "label": "Memory Size Max Diff Ratio 30 Percent",
  "related_components": [
    "test_tags.TestCategory.DRAM"
  ],
  "args": {
    "max_diff_ratio": 0.3
  }
}
```

To compare and check the memory size from `mosys`, kernel, and device data
`component.memory_size`:

```default
{
  "label": "Memory Size Compare To Device Data",
  "subtests": [
    {
      "pytest_name": "scan",
      "label": "Scan Memory Size in GB",
      "related_components": [
        "test_tags.TestCategory.VPD"
      ],
      "action_on_failure": "STOP",
      "args": {
        "device_data_key": "component.memory_size",
        "label": "Memory Size in GB"
      }
    },
    {
      "pytest_name": "memory_size",
      "label": "Memory Size",
      "related_components": [
        "test_tags.TestCategory.DRAM"
      ],
      "action_on_failure": "STOP",
      "args": {
        "device_data_key": "component.memory_size"
      }
    }
  ]
}
```

## Test Arguments

| Name            | Type      | Description                                                                                                              |
|-----------------|-----------|--------------------------------------------------------------------------------------------------------------------------|
| device_data_key | str, None | (optional; default: `None`) Device data key for getting memory size in GB.                                               |
| max_diff_ratio  | float     | (optional; default: `0.2`) Maximum tolerance difference between memory size detected by kernel and mosys within a ratio. |
