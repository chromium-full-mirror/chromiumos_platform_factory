# generic_dram

Predefined DRAM tests. DRAM is called “Memory” in AVL.

## Inherit

- [base.test_list](base.test_list.md)

## MemorySize

### pytest_name

[memory_size](../pytests/memory_size.md)

## ProbeDram

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`component_list`
: ```default
  [
    "dram"
  ]
  ```

`config_file`
: ```default
  "/usr/local/factory/py/hwid/v3/default_probe_statement.json"
  ```

`overridden_rules`
: ```default
  [
    [
      "dram",
      ">",
      0
    ]
  ]
  ```

## StressAppTest

### pytest_name

[stressapptest](../pytests/stressapptest.md)

## MRCCache

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
- RebootStep
- ```default
  {
    "args": {
      "mode": "verify_update"
    },
    "label": "i18n! Verify Cache Update",
    "pytest_name": "mrc_cache"
  }
  ```
- RebootStep
- ```default
  {
    "args": {
      "mode": "verify_no_update"
    },
    "label": "i18n! Verify Cache No Update",
    "pytest_name": "mrc_cache"
  }
  ```
