# shopfloor_service

**Source code:** [shopfloor_service.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/shopfloor_service.py)

Invoke remote procedure call for interaction with shopfloor backend.

## Description

The Chromium OS Factory Software has defined a protocol, “Chrome OS Factory
Shopfloor Service Specification”, to access factory manufacturing line shopfloor
system (or MES) backend system. This test allows interaction with a shopfloor
service, by requesting the factory server with defined protocol.

For more information about Chrome OS Factory Shopfloor Service Specification,
read
[https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/shopfloor/README.md](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/shopfloor/README.md)

By default, the protocol has been simplified so you don’t need to manually
generate or process `FactoryDeviceData` or `DeviceData` - just provide
the constant arguments from test list.

For example, the method `NotifyStart(data, station)` can be invoked by
(assume station is `'SMT'`) `method='NotifyStart'` and `args=['SMT']`.
Also the return value is automatically merged into Device Data (see
`cros.factory.test.device_data` for more details).

For OEM Chromebook projects, you should only use the standard methods defined in
Chrome OS Factory Shopfloor Service Specification. However, if you need to work
on a customized project or using a fixture with XMLRPC interface, it is possible
to use this test by setting argument `raw_invocation` to True.

When `raw_invocation` is True, the invocation will simply run with argument
`args` and `kargs`, no auto-generation of FactoryDeviceData or DeviceData.
The return value will still be merged to device data.

## Test Procedure

This is an automated test without user interaction unless manually ‘retry’ is
needed.

When started, the test will connect to remote server and try to invoke specified
method with given arguments, and will display return (error) messages and wait
for retry on failure.

The pytest also sets device data to indicate certain checkpoint is passed, such
as `factory.start_SMT`, `factory.end_SMT`. These values can be synced to RW
VPD by write_device_data_to_vpd.py.

## Dependency

No special dependency on client side, but the server must be implemented with
needed XMLRPC methods.

## Examples

To start ‘SMT’ station tests, add this in test list:

```default
{
  "pytest_name": "shopfloor_service",
  "args": {
    "args": ["SMT"],
    "method": "NotifyStart"
  }
}
```

To invoke a non-standard call ‘DoSomething’ with args (1, 2) and keyword args
{‘arg1’: 1}:

```default
{
  "pytest_name": "shopfloor_service",
  "args": {
    "args": [1, 2],
    "raw_invocation": true,
    "kargs": {
      "arg1": 1
    },
    "method": "DoSomething"
  }
}
```

To manually set factory server URL, set ‘server_url’ in test list:

```default
{
  "pytest_name": "shopfloor_service",
  "args": {
    "args": ["arg1", "arg2"],
    "method": "DoSomething",
    "server_url": "http://my-server:8080"
  }
}
```

To auto-detect factory server by received DHCP IP address, specify a mapping
object with key set to “IP/CIDR” and value set to server URL:

```default
{
  "pytest_name": "shopfloor_service",
  "args": {
    "args": ["arg1", "arg2"],
    "method": "DoSomething",
    "server_url": {
      "192.168.1.0/24": "http://192.168.1.254:8080",
      "10.3.0.0/24": "http://10.3.0.10:8080",
      "10.1.0.0/16": "http://10.1.0.10:8080",
      "default": "http://my-default-factory-server:8080"
    }
  }
}
```

## Test Arguments

| Name           | Type            | Description                                                       |
|----------------|-----------------|-------------------------------------------------------------------|
| method         | str             | Name of shopfloor service method to call                          |
| args           | list, None      | (optional; default: `None`) Arguments for specified method.       |
| kargs          | Mapping, None   | (optional; default: `None`) Keyword arguments for method.         |
| raw_invocation | bool            | (optional; default: `False`) Allow invocation of arbitrary calls. |
| server_url     | str, dict, None | (optional; default: `None`) The URL to factory server             |
