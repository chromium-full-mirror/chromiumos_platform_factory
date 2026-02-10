# Device Data

A module to manipulate device manufacturing information.

The “Device Data” is a set of mapping data storing manufacturing information for
DUT (device under test), including peripheral information (for example if
touchscreen should be available or not), per-device provisioned data (also known
as Vital Product Data - VPD; for example serial number or shipping region), test
status (has passed SMT, FATP, or other stations).

The Device Data is shared by tests in Chrome OS Factory Software, the test
harness “Goofy” and the “Shopfloor Service API”. The values usually come from
pre-defined values, shopfloor backend, or set by tests using manual selection
or barcode scanner (especially serial numbers).

Device Data can be considered as a mapping or dictionary, with following keys:

- `serials`: A dictionary for serial numbers of device, components, and
  mainboard.  All serial numbers here will be logged by testlog, including:
  - `serial_number`: The serial number of “device” itself (printed on device
    panel).
  - `mlb_serial_number`: The serial number of main logic board (mainboard).
- `component`: A dictionary to indicate what peripherals should exist, for
  example:
  - `has_touchscreen=True`: A touch screen should be available.
  - `has_dram=2`: Two DRAM components should be available.
- `vpd`: A dict for what VPD values need to be set, including:
  - `ro`: VPD values in RO section (RO_VPD), usually including:
    - `region`: Region code as defined in [http://go/cros-regions](http://go/cros-regions).
  - `rw`: VPD values in RW section (RW_VPD), usually including:
    - `ubind_attribute`: User registration code.
    - `gbind_attribute`: Group registration code.
- `hwid`: A value of probed Hardware ID.
- `factory`: A dict for manufacturing flow control, used by shopfloor
  backends. See Shopfloor Service API for more details.
- `feature management`: A dictionary for what feature management will be
  reading, including:
  - `feature management`: boolean value specifying if panel A contains
    logo.
  - `hw_compliance_version`: Int value representing the version in factory?

For example, a typical device usually has both device serial number and
main board serial number, region VPD, registration codes, thus the device data
will be set to:

```default
{
  'serials': {
    'serial_number': 'SN1234567890',
    'mlb_serial_number': 'MLB1234567890'
  },
  'vpd': {
    'ro': {
      'region': 'us'
    },
    'rw': {
      'ubind_attribute': '12345',
      'gbind_attribute': '54321',
    }
  }
}
```

## Using Device Data

Device Data is internally stored as Python dict inside shelves, and provided by
cros.factory.test.state module via RPC calls.

To get all data as single dict,
use `GetAllDeviceData`. To get partial data, use `GetDeviceData` with key
names joined using dot. For example, to fetch only the `ro` values inside
`vpd`:

```default
GetDeviceData('vpd.ro')
```

The key names are also defined in this module. All constants starting with
`KEY_` are complete key names for `GetDeviceData` to use. Constants starting
with `NAME_` are key names (no dot) of the single dict. For example, following
calls are equivalent if `vpd.ro.region` exists:

```default
GetDeviceData('vpd.ro.region')
GetDeviceData('vpd').get('ro').get('region')
GetDeviceData(KEY_VPD).get(NAME_RO).get(NAME_REGION)
GetDeviceData(KEY_VPD_RO).get(NAME_REGION)
GetDeviceData(KEY_VPD_REGION)
```

If `vpd.ro` does not exist, `get('ro')` will return None so you can’t invoke
another `get('region')` on it. So using the complete key path
(`vpd.ro.region`) provides an easier way to retrieve single value without
worrying if the intermediate dictionaries exist or not.

## Using Serial Number

There are some special helpers to access serial number. `GetSerialNumber` and
`SetSerialNumber` expect names of serial numbers (`NAME_*`). But as a syntax
sugar, they will also accept keys with `KEY_SERIALS` prefixed. For example,
following calls are equivalent:

```default
GetSerialNumber('serial_number')
GetSerialNumber(NAME_SERIAL_NUMBER)
GetSerialNumber(KEY_SERIAL_NUMBER)
GetDeviceData(KEY_SERIAL_NUMBER)
```

Note when setting serial numbers (`SetSerialNumber`), a value evaluates to
false (None, false, empty string…) will **delete** the stored serial number.

## API Spec

### cros.factory.test.device_data.CheckValidDeviceDataKey(key, key_prefix=None)

Checks if given key is a valid device data key.

* **Parameters:**
  * **key** – A string of key for device data.
  * **key_prefix** – Key must start with this token.
* **Raises:**
  **KeyError if the key is not valid.** – 

### cros.factory.test.device_data.GetDeviceData(key: str, , data_type: Type[int], throw_if_none: bool = False) → int | None

### cros.factory.test.device_data.GetDeviceData(key: str, , data_type: Type[str], throw_if_none: bool = False) → str | None

### cros.factory.test.device_data.GetDeviceData(key: str, , throw_if_none: bool = False, default: Any = None) → Any

### cros.factory.test.device_data.GetDeviceData(key: str, default: Any = None, , throw_if_none: bool = False) → Any

### cros.factory.test.device_data.GetDeviceData(key: str, default: Any = None, data_type: Type[int] | Type[str] | None = None, , throw_if_none: bool = False) → Any

Returns the device data associated by key.

* **Parameters:**
  * **key** – A string of key to access device data.
  * **default** – The default value if key does not exist.
  * **data_type** – The returned type of the function. We may save integer as an hex
    string in the device data. Use data_type to convert it into int. Do no
    conversion if data_type is None.
  * **throw_if_none** – If set, throw a KeyError if the key is not found.
* **Returns:**
  Associated value if key exists in device data, otherwise the value specified
  by default. Defaults to None.

### cros.factory.test.device_data.GetAllDeviceData()

Returns all device data in a single dict.

### cros.factory.test.device_data.GetDeviceDataSelector()

Returns the data shelf selector rooted at device data.

This is primarily used by invocation module to resolve TestListArgs.

### cros.factory.test.device_data.DeleteDeviceData(delete_keys, optional=False)

Deletes given keys from device data.

* **Parameters:**
  * **delete_keys** – A list of keys (or a single string) to be deleted.
  * **optional** – False to raise a KeyError if not found.
* **Returns:**
  The updated dictionary.

### cros.factory.test.device_data.VerifyDeviceData(device_data)

Verifies whether all fields in the device data dictionary are valid.

* **Parameters:**
  **device_data** – A dict with key/value pairs to verify.
* **Raises:**
  **ValueError** – 

### cros.factory.test.device_data.UpdateDeviceData(new_device_data)

Updates existing device data with given new dict data.

* **Parameters:**
  **new_device_data** – A dict with key/value pairs to update.  Old values
  are overwritten.
* **Returns:**
  The updated dictionary.

### cros.factory.test.device_data.GetAllSerialNumbers()

Returns all serial numbers available in device data as dict.

### cros.factory.test.device_data.ClearAllSerialNumbers()

Clears all serial numbers stored in device data.

### cros.factory.test.device_data.GetSerialNumber(name='serial_number')

Returns a serial number (default to device serial number).

### cros.factory.test.device_data.SetSerialNumber(name, value)

Sets a serial number to give nvalue.

* **Parameters:**
  * **name** – A string to indicate serial number name.
  * **value** – A string representing the serial number, or anything evaluated
    as False to delete the serial number.

### cros.factory.test.device_data.UpdateSerialNumbers(dict_)

Updates stored serial numbers by given dict.

* **Parameters:**
  **dict** – A mapping of serial number names and values to change.
  A value evaluated as False will delete the serial number from device
  data.

### cros.factory.test.device_data.GetOEMName()

Returns OEM name in device data.

### cros.factory.test.device_data.FlattenData(data, parent='')

An helper utility to flatten multiple layers of dict into one dict.

For example, {‘a’: {‘b’: ‘c’}} => {‘a.b’: ‘c’}

* **Parameters:**
  * **data** – The dict type data to be flattened.
  * **parent** – A string to encode as key prefix for recursion.
* **Returns:**
  A flattened dict.

### cros.factory.test.device_data.LoadConfig(config_name=None)

Helper utility to load a JSON config that represents device data.

* **Parameters:**
  **config_name** – A string for name to be passed to config_utils.LoadConfig.
* **Returns:**
  A dictionary as device data (already flattened).

### cros.factory.test.device_data.UpdateDeviceDataFromVPD(key_map, vpd_data)

Update device data from VPD data.

Please see pytest read_device_data_from_vpd for more details.
For both key_map and vpd_data, they should be a dictionary, with at most
two keys: ‘ro’ and ‘rw’ (NAME_RO and NAME_RW).  key_map[‘ro’] and
key_map[‘rw’] should follow the format of ro_key_map and rw_key_map in
read_device_data_from_vpd.  If key_map is None, a default key_map will be
used.

### *exception* cros.factory.test.device_data.InvalidFeatureData

Exception to raise when data is incorrect

### *exception* cros.factory.test.device_data.InconsistentFeatureData

Raised when data is not matching with existing device_data

### cros.factory.test.device_data.GetFeatureDeviceData() → Dict[str, int | bool]

Returns Feature Management

### cros.factory.test.device_data.VerifyFeatureData(data: dict) → bool

### cros.factory.test.device_data.SetFeatureDeviceData(new_data: Dict) → None

Sets the data of feature device.

### cros.factory.test.device_data.SetBrandedChassisData(branded: bool) → None

### cros.factory.test.device_data.SetHWComplianceVersionData(version: int) → None
