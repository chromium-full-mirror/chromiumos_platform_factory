# vswr.vswr

**Source code:** [vswr/vswr.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/vswr/vswr.py)

VSWR measures the efficiency of the transmission line.

## Description

SWR (Standing Wave Ratio) is the ratio of the amplitude of a partial standing
wave at an antinode (maximum) to the amplitude at an adjacent node (minimum).
SWR is usually defined as a voltage ratio called the VSWR, but it is also
possible to define the SWR in terms of current, resulting in the ISWR, which has
the same numerical value. The power standing wave ratio (PSWR) is defined as the
square of the VSWR.

### Why do we need VSWR?

A problem with transmission lines is that impedance mismatches in the cable
tend to reflect the radio waves back to the source, preventing the power from
reaching the destination. SWR measures the relative size of these
reflections. An ideal transmission line would have an SWR of 1:1, with all
the power reaching the destination and none of the power reflected back. An
infinite SWR represents complete reflection, with all the power reflected
back down the cable.

## Test Procedure

Please see
[https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/test/pytests/vswr/README.md](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/test/pytests/vswr/README.md)

## Dependency

This test measures VSWR value using an Agilent E5071C Network Analyzer (ENA).

## Examples

For the format of vswr_config.yaml, please check
[https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/test/pytests/vswr/vswr_config.sample.yaml](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/test/pytests/vswr/vswr_config.sample.yaml).:

```default
{
  "pytest_name": "vswr",
  "args": {
    "event_log_name": "vswr_prepressed",
    "config_path": "/usr/local/factory/config/vswr_config.yaml"
  }
}
```

## Test Arguments

| Name              | Type      | Description                                                                                                                                                                                                 |
|-------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| event_log_name    | str       | Name of the event_log, like “vswr_prepressed” or “vswr_postpressed”.                                                                                                                                        |
| config_path       | str, None | (optional; default: `None`) Configuration path relative to the root of pytest vswr folder. E.g. path/to/config_file_name. Can use `download_from_factory_drive` pytest for downloading latest config files. |
| timezone          | str       | (optional; default: `'Asia/Taipei'`) Timezone of shopfloor.                                                                                                                                                 |
| serial_number_key | str       | (optional; default: `'serial_number'`) The key referring to the serial number in question. This key will be used to retrieve the serial number from the shared data. Default key is serial_number.          |
| keep_raw_logs     | bool      | (optional; default: `True`) Whether to attach the log by Testlog                                                                                                                                            |
