# generic_rrt

## Inherit

- [generic_camera.test_list](generic_camera.test_list.md)
- [generic_dram.test_list](generic_dram.test_list.md)
- [generic_common.test_list](generic_common.test_list.md)

## RRTCountdown

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
      90,
      100
    ]
  ]
  ```

## RRTDozingStress

### Parallel subtests

- ```default
  {
    "args": {
      "free_memory_only": true,
      "seconds": "eval! constants.rrt.dozing_sat_duration_secs",
      "wait_secs": 60
    },
    "inherit": "StressAppTest"
  }
  ```
- ```default
  {
    "args": {
      "cycles": 15,
      "suspend_delay_max_secs": 30,
      "suspend_delay_min_secs": 28,
      "suspend_time_margin_min_secs": -1
    },
    "inherit": "SuspendResume",
    "retries": 2
  }
  ```
- ```default
  {
    "args": {
      "duration_secs": "eval! constants.rrt.dozing_sat_duration_secs"
    },
    "inherit": "RRTCountdown"
  }
  ```

## RRTRebootCheck

### Serial subtests

- ```default
  {
    "args": {
      "commands": "ifconfig wlan0"
    },
    "inherit": "ExecShell",
    "label": "Check WLAN"
  }
  ```
- ```default
  {
    "args": {
      "commands": "hciconfig hci0"
    },
    "inherit": "ExecShell",
    "label": "Check Bluetooth"
  }
  ```

## RRTStressGroup

### Parallel subtests

- ```default
  {
    "args": {
      "duration_secs": "eval! constants.rrt.sat_duration_secs"
    },
    "inherit": "WebGLAquarium"
  }
  ```
- ```default
  {
    "args": {
      "mode": "timeout",
      "show_image": false,
      "timeout_secs": "eval! constants.rrt.sat_duration_secs"
    },
    "inherit": "Camera"
  }
  ```
- ```default
  {
    "args": {
      "duration_secs": "eval! constants.rrt.sat_duration_secs"
    },
    "inherit": "URandom"
  }
  ```
- ```default
  {
    "args": {
      "free_memory_only": true,
      "seconds": "eval! constants.rrt.sat_duration_secs",
      "wait_secs": 60
    },
    "inherit": "StressAppTest"
  }
  ```
- ```default
  {
    "args": {
      "duration_secs": "eval! constants.rrt.sat_duration_secs"
    },
    "inherit": "RRTCountdown"
  }
  ```

## RRTWarmColdReboot

### Serial subtests

- ColdReset
- [RRTRebootCheck]()
- Barrier
- ```default
  {
    "args": {
      "wait_secs": 60
    },
    "inherit": "Idle"
  }
  ```
- RebootStep
- [RRTRebootCheck]()
- Barrier
