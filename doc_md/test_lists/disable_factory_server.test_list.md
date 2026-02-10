# disable_factory_server

## Inherit

- [generic_common.test_list](generic_common.test_list.md)

## GetDeviceInfo

### pytest_name

[update_device_data](../pytests/update_device_data.md)

### args

`fields`
: ```default
  [
    [
      "component.has_cellular",
      null,
      "i18n! Has Cellular",
      [
        true,
        false
      ]
    ],
    [
      "component.has_lte",
      null,
      "i18n! Has LTE",
      [
        true,
        false
      ]
    ],
    [
      "component.has_touchscreen",
      null,
      "i18n! Has Touchscreen",
      [
        true,
        false
      ]
    ],
    "vpd.ro.region"
  ]
  ```

## ShopfloorNotifyEnd

### pytest_name

[update_device_data](../pytests/update_device_data.md)

### args

`manual_input`
: ```default
  false
  ```

`fields`
: ```default
  [
    [
      "eval! 'factory.end_' + locals.station",
      true
    ]
  ]
  ```

## ShopfloorNotifyStart

### pytest_name

[update_device_data](../pytests/update_device_data.md)

### args

`manual_input`
: ```default
  false
  ```

`fields`
: ```default
  [
    [
      "eval! 'factory.start_' + locals.station",
      true
    ]
  ]
  ```
