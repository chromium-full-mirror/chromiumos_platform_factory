# generic_dram_examples

Examples for testing DRAM components. DRAM is called “Memory” in AVL.

## Inherit

- [generic_dram.test_list](generic_dram.test_list.md)

## MemorySizeMaxDiffRatio30Percent

### pytest_name

[memory_size](../pytests/memory_size.md)

### args

`max_diff_ratio`
: ```default
  0.3
  ```

## StressAppTestForOneDay

### pytest_name

[stressapptest](../pytests/stressapptest.md)

### args

`seconds`
: ```default
  86400
  ```

## StressAppTestOnlyCPUAndMemory

### pytest_name

[stressapptest](../pytests/stressapptest.md)

### args

`disk_thread`
: ```default
  false
  ```

## DRAMTests

### Serial subtests

- ProbeDram
- [UpdateDramPartNum]()
- MemorySize
- [MemorySizeMaxDiffRatio30Percent]()
- [MemorySizeCompareToDeviceData]()
- MRCCache
- StressAppTest
- [StressAppTestOnlyCPUAndMemory]()
- [StressAppTestForOneDay]()

## MemorySizeCompareToDeviceData

### Serial subtests

- ```default
  {
    "args": {
      "device_data_key": "component.memory_size",
      "label": "Memory Size in GB"
    },
    "label": "Scan Memory Size in GB",
    "pytest_name": "scan"
  }
  ```
- ```default
  {
    "args": {
      "device_data_key": "component.memory_size"
    },
    "inherit": "MemorySize"
  }
  ```

## UpdateDramPartNum

### Serial subtests

- ```default
  {
    "args": {
      "commands": [
        "factory device-data component.dram_part_num=\"$(ectool cbi get 3)\""
      ]
    },
    "label": "Read DRAM Part Num From CBI",
    "pytest_name": "exec_shell"
  }
  ```
- ```default
  {
    "args": {
      "device_data_key": "component.dram_part_num",
      "label": "DRAM Part Num"
    },
    "label": "Scan DRAM Part Num",
    "pytest_name": "scan"
  }
  ```
- ```default
  {
    "args": {
      "cbi_data_names": [
        "DRAM_PART_NUM"
      ]
    },
    "label": "Update DRAM Part Num in CBI",
    "pytest_name": "update_cbi"
  }
  ```
