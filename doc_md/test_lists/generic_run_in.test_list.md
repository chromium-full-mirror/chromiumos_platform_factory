# generic_run_in

## Inherit

- [generic_battery.test_list](generic_battery.test_list.md)
- [generic_camera.test_list](generic_camera.test_list.md)
- [generic_dram.test_list](generic_dram.test_list.md)
- [generic_tpm.test_list](generic_tpm.test_list.md)
- [generic_storage.test_list](generic_storage.test_list.md)
- [generic_common.test_list](generic_common.test_list.md)

## RunInBlockingCharge

Charges battery to min_charge_pct from Goofy’s charge_manager. There will be no AC power during FATP process, so we must make sure DUT battery has enough charge before leaving RunIn.

### pytest_name

[blocking_charge](../pytests/blocking_charge.md)

### args

`timeout_secs`
: ```default
  7200
  ```

## RunInCountdown

temp_criteria: A list of rules to check that temperature is under the given range, rule format is [name, temp_index, warning_temp, critical_temp]

### pytest_name

[countdown](../pytests/countdown.md)

### args

`log_interval`
: ```default
  10
  ```

`grace_secs`
: ```default
  480
  ```

`temp_max_delta`
: ```default
  10
  ```

`temp_criteria`
: ```default
  [
    [
      "CPU",
      null,
      null,
      null
    ]
  ]
  ```

## RunInRebootSequence

### pytest_name

[shutdown](../pytests/shutdown.md)

### args

`operation`
: ```default
  "reboot"
  ```

`warmup_post_shutdown`
: ```default
  "eval! constants.run_in.reboot_warmup_secs"
  ```

## RunInRebootStep

### pytest_name

[shutdown](../pytests/shutdown.md)

### args

`operation`
: ```default
  "reboot"
  ```

`warmup_post_shutdown`
: ```default
  "eval! constants.run_in.reboot_warmup_secs"
  ```

## RunInStressAppTest

### pytest_name

[stressapptest](../pytests/stressapptest.md)

### args

`seconds`
: ```default
  "eval! constants.run_in.sat_duration_secs"
  ```

`wait_secs`
: ```default
  10
  ```

`free_memory_only`
: ```default
  true
  ```

## RunInStressCountdown

temp_criteria: A list of rules to check that temperature is under the given range, rule format is [name, temp_index, warning_temp, critical_temp]

### pytest_name

[countdown](../pytests/countdown.md)

### args

`log_interval`
: ```default
  10
  ```

`grace_secs`
: ```default
  480
  ```

`temp_max_delta`
: ```default
  10
  ```

`temp_criteria`
: ```default
  [
    [
      "CPU",
      null,
      null,
      null
    ]
  ]
  ```

`wifi_update_interval`
: ```default
  10
  ```

`bluetooth_update_interval`
: ```default
  10
  ```

`als_update_interval`
: ```default
  10
  ```

`duration_secs`
: ```default
  "eval! constants.run_in.sat_duration_secs"
  ```

## RunInStressFrontCamera

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_front_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "front"
  ```

`mode`
: ```default
  "timeout"
  ```

`show_image`
: ```default
  false
  ```

`timeout_secs`
: ```default
  "eval! constants.run_in.sat_duration_secs"
  ```

## RunInStressRearCamera

This test object cannot be run directly. User have to inherit and modify it.

### run_if

```default
not constants.has_device_data or device.component.has_rear_camera
```

### pytest_name

[camera](../pytests/camera.md)

### args

`camera_facing`
: ```default
  "rear"
  ```

`mode`
: ```default
  "timeout"
  ```

`show_image`
: ```default
  false
  ```

`timeout_secs`
: ```default
  "eval! constants.run_in.sat_duration_secs"
  ```

## RunInSuspendStress

This test runs \`suspend_stress_test\`.

### pytest_name

[suspend_stress](../pytests/suspend_stress.md)

### args

`cycles`
: ```default
  "eval! constants.run_in.dozing_sat_duration_secs // 20"
  ```

`suspend_time_margin_min_secs`
: ```default
  -1
  ```

## RunInSuspendStressMemoryCheck

This test runs \`suspend_stress_test –memory-check\`.

### pytest_name

[suspend_stress](../pytests/suspend_stress.md)

### args

`cycles`
: ```default
  "eval! constants.run_in.dozing_sat_duration_secs // 20"
  ```

`suspend_time_margin_min_secs`
: ```default
  -1
  ```

`memory_check`
: ```default
  true
  ```

## RunInURandom

### pytest_name

[urandom](../pytests/urandom.md)

### args

`duration_secs`
: ```default
  "eval! constants.run_in.sat_duration_secs"
  ```

## RunInWebGLAquarium

You can enhance RunInStressGroup by adding this test. However, running WebGLAquarium with a bunch of other stress tests is not a FSI gate. go/pe-sw-gates

### pytest_name

[webgl_aquarium](../pytests/webgl_aquarium.md)

### args

`duration_secs`
: ```default
  "eval! constants.run_in.sat_duration_secs"
  ```

## RunInWebGLAquarium1000

Monitor the performance of graphics.

### pytest_name

[webgl_aquarium](../pytests/webgl_aquarium.md)

### args

`duration_secs`
: ```default
  "eval! constants.run_in.run_fishes_for_secs"
  ```

`num_fish`
: ```default
  1000
  ```

## RunInWebGLAquarium50

Monitor the performance of graphics.

### pytest_name

[webgl_aquarium](../pytests/webgl_aquarium.md)

### args

`duration_secs`
: ```default
  "eval! constants.run_in.run_fishes_for_secs"
  ```

`num_fish`
: ```default
  50
  ```

## RunIn

### Serial subtests

- [RunInStart]()
- Barrier
- [RunInItems]()
- CheckPoint
- [RunInEnd]()

## RunInDozingStress

This test runs \`stressapptest\` and \`suspend_stress_test\` simultaneously.

In addition to measure the ability of a device to transition between ACPI power states, \`stressapptest\` can detect bad memory.

### Parallel subtests

- ```default
  {
    "args": {
      "free_memory_only": true,
      "seconds": "eval! constants.run_in.dozing_sat_duration_secs"
    },
    "inherit": "StressAppTest"
  }
  ```
- ```default
  {
    "args": {
      "cycles": "eval! constants.run_in.dozing_sat_duration_secs // 40",
      "suspend_delay_max_secs": 30,
      "suspend_delay_min_secs": 28,
      "suspend_time_margin_min_secs": -1
    },
    "inherit": "SuspendStress"
  }
  ```
- ```default
  {
    "args": {
      "duration_secs": "eval! constants.run_in.dozing_sat_duration_secs"
    },
    "inherit": "RunInCountdown"
  }
  ```

## RunInEnd

### Serial subtests

- StationEnd
- CheckPoint
- [RunInRebootStep]()

## RunInItems

RunIn is a stage to stress all ports for checking system stability. This stage may have many test barriers to let it fail early and reduce wasted test time.

The Factory Requirements ([https://chromeos.google.com/partner/dlm/docs/factory/factoryrequirements.html](https://chromeos.google.com/partner/dlm/docs/factory/factoryrequirements.html)) states that suspend resume is required as an essential part of Run-In testing. The purpose is to measure the ability of a device to transition between ACPI power states. To be more specific, ODM is required to perform one of RunInSuspendStress, RunInSuspendStressMemoryCheck, or RunInDozingStress.

### Serial subtests

- TPMVerifyEK
- ClearTPMOwnerRequest
- [RunInMRCCache]()
- [RunInRebootStep]()
- Fan
- [RunInStressGroupWithFrontCamera]()
- Barrier
- [RunInStressGroupWithRearCamera]()
- Barrier
- [RunInWebGLAquarium50]()
- Barrier
- [RunInWebGLAquarium1000]()
- Barrier
- [RunInRebootStep]()
- Barrier
- [RunInSuspendStress]()
- Barrier
- [RunInRebootSequence]()
- Barrier
- VerifyRootPartition
- Barrier
- [RunInBlockingCharge]()
- Barrier
- MemorySize
- BatterySysfs

## RunInMRCCache

### Serial subtests

- ```default
  {
    "args": {
      "mode": "create"
    },
    "label": "i18n! Create Cache",
    "pytest_name": "mrc_cache"
  }
  ```
- [RunInRebootStep]()
- ```default
  {
    "args": {
      "mode": "verify_update"
    },
    "label": "i18n! Verify Cache Update",
    "pytest_name": "mrc_cache"
  }
  ```
- [RunInRebootStep]()
- ```default
  {
    "args": {
      "mode": "verify_no_update"
    },
    "label": "i18n! Verify Cache No Update",
    "pytest_name": "mrc_cache"
  }
  ```

## RunInStart

### Serial subtests

- StationStart

## RunInStressGroup

### Parallel subtests

- [RunInStressFrontCamera]()
- [RunInURandom]()
- [RunInStressAppTest]()
- [RunInStressCountdown]()

## RunInStressGroupWithFrontCamera

### Parallel subtests

- [RunInStressFrontCamera]()
- [RunInURandom]()
- [RunInStressAppTest]()
- [RunInStressCountdown]()

## RunInStressGroupWithRearCamera

### run_if

```default
not constants.has_device_data or device.component.has_rear_camera
```

### Parallel subtests

- [RunInStressRearCamera]()
- [RunInURandom]()
- [RunInStressAppTest]()
- [RunInStressCountdown]()
