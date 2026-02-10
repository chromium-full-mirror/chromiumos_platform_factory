# retrieve_config

**Source code:** [retrieve_config.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/retrieve_config.py)

Retrieve JSON config file from either an USB stick or a factory server.

## Description

This pytest retrieves the config file from a specified source, so a following
pytest can use config_utils to load specfic config data.

The config file can be fecthed from two types of sources:
1. Factory server
2. USB stick

To fetch a config file from a factory server, you should put the config
file under the ‘parameters’ folders, and specify the data_method to
FACTORY_SERVER.

To fetch a config file from a USB stick, you can put the file at any partition
you want, as long as the partition and file system on the USB stick can be
recognized by the operating system. The data_method should be set to ‘USB’,
and if there are several partitions on the USB stick, the argument
usb_dev_parition should be set to specify the partition you placed the config
file.

## Test Procedure

If data_method is set to ‘FACTORY_SERVER’, no action needs to be done.

If data_method is set to ‘USB’, then:
1. Insert the USB stick
2. Wait for completion

## Dependency

Depends on ‘udev’ and ‘pyudev’ python module to monitor USB insertion.

## Examples

Assume the config file is located at ‘foo/bar.json’ under the remote source
(i.e., a factory server, or a USB stick).

The JSON config can be loaded from the factory server by:

```default
{
  "pytest_name": "retrieve_config",
  "args": {
    "config_retrieve_path": "foo/bar.json"
  }
}
```

To load the JSON config from a USB stick, add this in test list:

```default
{
  "pytest_name": "retrieve_config",
  "args": {
    "data_method": "USB",
    "config_retrieve_path": "foo/bar.json"
  }
}
```

## Test Arguments

| Name                 | Type                      | Description                                                                                                                                              |
|----------------------|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| data_method          | [‘FACTORY_SERVER’, ‘USB’] | (optional; default: `<DataMethod.FACTORY_SERVER: 'FACTORY_SERVER'>`) The method to retrieve config.                                                      |
| config_retrieve_path | str                       | The path to the config file to retrieve from.                                                                                                            |
| config_save_dir      | str, None                 | (optional; default: `None`) The directory path to the config file to place at;defaults to RuntimeConfigDirectory in config_utils.json.                   |
| config_save_name     | str, None                 | (optional; default: `None`) The config name saved in the config_save_dir; The name should suffix with “.json”. if None then defaults to its origin name. |
| local_ip             | str, None                 | (optional; default: `None`) Local IP address for connecting to the factory server when data_method = FACTORY_SERVER. Set as None to use DHCP.            |
| usb_dev_partition    | int, None                 | (optional; default: `None`) The partition of the usb_dev_path to be mounted. If None, will try to mount the usb_dev_path without partition number.       |
