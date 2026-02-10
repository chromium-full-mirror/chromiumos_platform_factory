# generic_common

## Inherit

- [base.test_list](base.test_list.md)

## ActivateRegCode

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[shopfloor_service](../pytests/shopfloor_service.md)

### args

`method`
: ```default
  "ActivateRegCode"
  ```

## AllCheckPoint

### pytest_name

[summary](../pytests/summary.md)

### args

`disable_input_on_fail`
: ```default
  true
  ```

`pass_without_prompt`
: ```default
  false
  ```

`accessibility`
: ```default
  true
  ```

`include_parents`
: ```default
  true
  ```

## Barrier

### pytest_name

[summary](../pytests/summary.md)

### args

`disable_input_on_fail`
: ```default
  true
  ```

`pass_without_prompt`
: ```default
  true
  ```

`accessibility`
: ```default
  true
  ```

## BrandedChassis

### pytest_name

[branded_chassis](../pytests/branded_chassis.md)

### args

`rma_mode`
: ```default
  "eval! constants.factory_process == 'RMA'"
  ```

## Button

### pytest_name

[button](../pytests/button.md)

### args

`timeout_secs`
: ```default
  120
  ```

## Buzzer

### pytest_name

[buzzer](../pytests/buzzer.md)

### args

`gpio_index`
: ```default
  "eval! constants.buzzer.gpio_index"
  ```

`beep_duration_secs`
: ```default
  0.3
  ```

`mute_duration_secs`
: ```default
  0.5
  ```

## CEC

### pytest_name

[cec](../pytests/cec.md)

### args

`power_on`
: ```default
  false
  ```

`power_off`
: ```default
  false
  ```

## ChargeDischargeCurrent

### pytest_name

[battery_current](../pytests/battery_current.md)

### args

`min_charging_current`
: ```default
  150
  ```

`min_discharging_current`
: ```default
  400
  ```

`timeout_secs`
: ```default
  30
  ```

`max_battery_level`
: ```default
  90
  ```

## ChargerTypeDetection

### pytest_name

[ac_power](../pytests/ac_power.md)

## CheckDisplay

### pytest_name

[external_display](../pytests/external_display.md)

### args

`display_info`
: ```default
  "eval! locals.display.display_info"
  ```

`start_output_only`
: ```default
  false
  ```

`stop_output_only`
: ```default
  false
  ```

`connect_only`
: ```default
  true
  ```

`drm_sysfs_path`
: ```default
  "/sys/class/drm/card0"
  ```

## CheckFeatureCompliance

### pytest_name

[feature_compliance_version](../pytests/feature_compliance_version.md)

### args

`hwid_need_vpd`
: ```default
  "eval! constants.hwid_need_vpd"
  ```

`rma_mode`
: ```default
  "eval! constants.factory_process == 'RMA'"
  ```

## CheckPDCFirmware

### pytest_name

[check_pdc_firmware](../pytests/check_pdc_firmware.md)

### args

`min_fw_version_dec`
: ```default
  "0.0.0.0.0.0.27.0"
  ```

## CheckPoint

### pytest_name

[summary](../pytests/summary.md)

### args

`disable_input_on_fail`
: ```default
  true
  ```

`pass_without_prompt`
: ```default
  false
  ```

`accessibility`
: ```default
  true
  ```

## CheckReleaseImage

### pytest_name

[check_image_version](../pytests/check_image_version.md)

### args

`check_release_image`
: ```default
  true
  ```

`use_netboot`
: ```default
  false
  ```

## CheckReleaseLVMStateful

### pytest_name

[check_release_lvm_stateful](../pytests/check_release_lvm_stateful.md)

## CheckRetimerFirmware

### pytest_name

[check_retimer_firmware](../pytests/check_retimer_firmware.md)

### args

`controller_ports`
: ```default
  "eval! constants.retimer.controller_ports"
  ```

`usb_ports`
: ```default
  "eval! constants.retimer.usb_ports"
  ```

`min_retimer_version`
: ```default
  "eval! constants.retimer.min_retimer_version"
  ```

## CheckSerialNumber

### pytest_name

[check_serial_number](../pytests/check_serial_number.md)

## ClearUnknownRWVPD

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "gooftool clear_unknown_vpd_entries"
  ```

## CopyMiniOS

### pytest_name

[copy_minios](../pytests/copy_minios.md)

## Cr50SMTWriteFlashInfo

Make old definition as an alias of the new definition for backward compatibility

### run_if

```default
constants.factory_process != 'FULL'
```

### pytest_name

[finalize](../pytests/finalize.md)

### args

`upload_method`
: ```default
  "eval! 'factory_server' if constants.enable_factory_server else 'none'"
  ```

`mode`
: ```default
  "eval! 'SHIMLESS_MLB' if constants.boot_to_shimless else 'MLB'"
  ```

`factory_process`
: ```default
  "eval! constants.factory_process"
  ```

## Cr50WriteCustomlabelFlags

Make old definition as an alias of the new definition for backward compatibility

### run_if

```default
constants.factory_process != 'FULL'
```

### pytest_name

[finalize](../pytests/finalize.md)

### args

`upload_method`
: ```default
  "eval! 'factory_server' if constants.enable_factory_server else 'none'"
  ```

`mode`
: ```default
  "eval! 'SHIMLESS_MLB' if constants.boot_to_shimless else 'MLB'"
  ```

`factory_process`
: ```default
  "eval! constants.factory_process"
  ```

## DeprovisionCBI

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  [
    "ectool cbi set 2 0x7fffffff 4",
    "ectool cbi remove 6"
  ]
  ```

## DisableLidSwitch

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "ectool forcelidopen 1"
  ```

## EnableLidSwitch

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "ectool forcelidopen 0"
  ```

## ExecShell

### pytest_name

[exec_shell](../pytests/exec_shell.md)

## ExternalDisplay

### pytest_name

[external_display](../pytests/external_display.md)

### args

`display_info`
: ```default
  [
    {
      "display_id": "HDMI",
      "display_label": "HDMI External Display",
      "usbpd_spec": {
        "port": 0
      }
    }
  ]
  ```

## Fan

### run_if

```default
constants.has_fan
```

### pytest_name

[fan_speed](../pytests/fan_speed.md)

### args

`probe_interval_secs`
: ```default
  0.2
  ```

`target_rpm`
: ```default
  [
    3000,
    4500,
    6000
  ]
  ```

`error_margin`
: ```default
  300
  ```

## FinalizeMLB

### run_if

```default
constants.factory_process != 'FULL'
```

### pytest_name

[finalize](../pytests/finalize.md)

### args

`upload_method`
: ```default
  "eval! 'factory_server' if constants.enable_factory_server else 'none'"
  ```

`mode`
: ```default
  "eval! 'SHIMLESS_MLB' if constants.boot_to_shimless else 'MLB'"
  ```

`factory_process`
: ```default
  "eval! constants.factory_process"
  ```

## Finish

### pytest_name

[message](../pytests/message.md)

## FlashNetboot

### pytest_name

[flash_netboot](../pytests/flash_netboot.md)

## FlushTestlog

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! constants.default_factory_server_url"
  ```

`sync_event_logs`
: ```default
  false
  ```

`update_toolkit`
: ```default
  false
  ```

`upload_report`
: ```default
  false
  ```

`upload_reg_codes`
: ```default
  false
  ```

`flush_testlog`
: ```default
  true
  ```

## GetDeviceInfo

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[shopfloor_service](../pytests/shopfloor_service.md)

### args

`method`
: ```default
  "GetDeviceInfo"
  ```

## HPS

### run_if

```default
device.component.has_hps
```

### pytest_name

[hps](../pytests/hps.md)

### args

`timeout_secs`
: ```default
  3600
  ```

## Idle

### pytest_name

[nop](../pytests/nop.md)

## Keyboard

### pytest_name

[keyboard](../pytests/keyboard.md)

### args

`allow_multi_keys`
: ```default
  true
  ```

`has_numpad`
: ```default
  "eval! device.component.has_numeric_pad or False"
  ```

## KeyboardBacklight

### run_if

```default
not constants.has_device_data or device.component.has_keyboard_backlight
```

### pytest_name

[keyboard_backlight](../pytests/keyboard_backlight.md)

## LED

### pytest_name

[led](../pytests/led.md)

### args

`challenge`
: ```default
  true
  ```

## LidSwitch

### pytest_name

[lid_switch](../pytests/lid_switch.md)

## LoadECButtonDriver

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "sleep 3 && echo GOOG0007:00 > /sys/bus/platform/drivers/cros-ec-keyb/bind || true"
  ```

## Message

### pytest_name

[message](../pytests/message.md)

## ModelSKU

### pytest_name

[model_sku](../pytests/model_sku.md)

### args

`config_name`
: ```default
  "model_sku"
  ```

## Mouse

### pytest_name

[mouse](../pytests/mouse.md)

## NotifyOverlordTrackConnection

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "ghost --track-connection y"
  ```

## NotifyOverlordUntrackConnection

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "ghost --track-connection n"
  ```

## PartitionTable

### pytest_name

[partition_table](../pytests/partition_table.md)

## Placeholder

### pytest_name

[nop](../pytests/nop.md)

## Probe

### pytest_name

[probe.probe](../pytests/probe.probe.md)

### args

`config_file`
: ```default
  "probe.json"
  ```

## ProximitySensor

### run_if

```default
not constants.has_device_data or device.component.has_proximity_sensor
```

### pytest_name

[proximity_sensor](../pytests/proximity_sensor.md)

## ReSignReleaseKernel

### run_if

```default
constants.phase != 'PVT' and constants.grt.re_sign_release_kernel
```

### pytest_name

[update_kernel](../pytests/update_kernel.md)

### args

`to_release`
: ```default
  true
  ```

## ReadDeviceDataFromCrosConfig

### pytest_name

[read_device_data_from_cros_config](../pytests/read_device_data_from_cros_config.md)

## ReadDeviceDataFromVPD

### pytest_name

[read_device_data_from_vpd](../pytests/read_device_data_from_vpd.md)

## RemovableStorage

### pytest_name

[removable_storage](../pytests/removable_storage.md)

### args

`block_size`
: ```default
  524288
  ```

`perform_random_test`
: ```default
  false
  ```

`perform_sequential_test`
: ```default
  true
  ```

`sequential_block_count`
: ```default
  8
  ```

## SDPerformance

### run_if

```default
constants.sd.sysfs_path != ''
```

### pytest_name

[removable_storage](../pytests/removable_storage.md)

### args

`block_size`
: ```default
  524288
  ```

`perform_random_test`
: ```default
  false
  ```

`perform_sequential_test`
: ```default
  true
  ```

`sequential_block_count`
: ```default
  8
  ```

`media`
: ```default
  "SD"
  ```

`sysfs_path`
: ```default
  "eval! constants.sd.sysfs_path"
  ```

`timeout_secs`
: ```default
  60
  ```

## Scan

### pytest_name

[scan](../pytests/scan.md)

## SetWidevineKeybox

### run_if

```default
constants.has_keybox
```

### pytest_name

[provision_drm_key](../pytests/provision_drm_key.md)

## ShopfloorNotifyEnd

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[shopfloor_service](../pytests/shopfloor_service.md)

### args

`method`
: ```default
  "NotifyEnd"
  ```

`args`
: ```default
  [
    "eval! locals.station"
  ]
  ```

## ShopfloorNotifyStart

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[shopfloor_service](../pytests/shopfloor_service.md)

### args

`method`
: ```default
  "NotifyStart"
  ```

`args`
: ```default
  [
    "eval! locals.station"
  ]
  ```

## ShopfloorService

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[shopfloor_service](../pytests/shopfloor_service.md)

## SpatialSensorCalibration

### pytest_name

[spatial_sensor_calibration](../pytests/spatial_sensor_calibration.md)

## Start

### pytest_name

[start](../pytests/start.md)

## StationEndSyncFactoryServer

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! constants.default_factory_server_url"
  ```

`upload_report`
: ```default
  "eval! locals.station_end_upload_report"
  ```

`report_stage`
: ```default
  "eval! locals.station"
  ```

## SuspendResume

### pytest_name

[suspend_resume](../pytests/suspend_resume.md)

## SuspendStress

### pytest_name

[suspend_stress](../pytests/suspend_stress.md)

## SyncFactoryServer

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! constants.default_factory_server_url"
  ```

## SyncFactoryServerUploadReport

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! constants.default_factory_server_url"
  ```

`upload_report`
: ```default
  true
  ```

`report_stage`
: ```default
  "eval! locals.station"
  ```

## TBTLoopback

### run_if

```default
False
```

### pytest_name

[thunderbolt_loopback](../pytests/thunderbolt_loopback.md)

## ThermalSensors

### pytest_name

[thermal_sensors](../pytests/thermal_sensors.md)

## ThermalSlope

### pytest_name

[thermal_slope](../pytests/thermal_slope.md)

## URandom

### pytest_name

[urandom](../pytests/urandom.md)

## USBPerformance

### pytest_name

[removable_storage](../pytests/removable_storage.md)

### args

`block_size`
: ```default
  524288
  ```

`perform_random_test`
: ```default
  false
  ```

`perform_sequential_test`
: ```default
  true
  ```

`sequential_block_count`
: ```default
  8
  ```

`media`
: ```default
  "USB"
  ```

## USBTypeCManualCharge

### pytest_name

[battery_current](../pytests/battery_current.md)

### args

`min_charging_current`
: ```default
  150
  ```

`min_discharging_current`
: ```default
  400
  ```

`timeout_secs`
: ```default
  30
  ```

`max_battery_level`
: ```default
  90
  ```

`usbpd_info`
: ```default
  [
    "eval! locals.usb.usbpd_id",
    "eval! int(locals.voltage * 1000 * 0.9)",
    "eval! int(locals.voltage * 1000 * 1.1)"
  ]
  ```

`usbpd_prompt`
: ```default
  "eval! locals.usb_label"
  ```

## USBTypeCManualExternalDisplay

### pytest_name

[external_display](../pytests/external_display.md)

### args

`display_info`
: ```default
  [
    "eval! locals.usb.display_info"
  ]
  ```

## UnloadECButtonDriver

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  "echo GOOG0007:00 > /sys/bus/platform/drivers/cros-ec-keyb/unbind || true"
  ```

## UpdateCBI

### pytest_name

[update_cbi](../pytests/update_cbi.md)

### args

`cbi_data_names`
: ```default
  [
    "SKU_ID",
    "DRAM_PART_NUM",
    "PCB_SUPPLIER",
    "SSFC"
  ]
  ```

## UpdateDeviceData

### pytest_name

[update_device_data](../pytests/update_device_data.md)

## UpdateSKUID

### pytest_name

[update_cbi](../pytests/update_cbi.md)

### args

`cbi_data_names`
: ```default
  [
    "SKU_ID"
  ]
  ```

## UploadRegCodes

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! constants.default_factory_server_url"
  ```

`sync_event_logs`
: ```default
  false
  ```

`sync_time`
: ```default
  true
  ```

`update_toolkit`
: ```default
  false
  ```

`upload_report`
: ```default
  false
  ```

`upload_reg_codes`
: ```default
  true
  ```

`flush_testlog`
: ```default
  false
  ```

## UploadSerialNumberForAuditing

### run_if

```default
constants.enable_factory_server
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! constants.default_factory_server_url"
  ```

`sync_event_logs`
: ```default
  false
  ```

`sync_time`
: ```default
  true
  ```

`update_toolkit`
: ```default
  false
  ```

`upload_report`
: ```default
  false
  ```

`upload_reg_codes`
: ```default
  false
  ```

`upload_sn`
: ```default
  true
  ```

`flush_testlog`
: ```default
  false
  ```

## UploadZeroTouchIds

### run_if

```default
constants.grt.enable_zero_touch and constants.grt.collect_zero_touch_ids
```

### pytest_name

[sync_factory_server](../pytests/sync_factory_server.md)

### args

`server_url`
: ```default
  "eval! constants.default_factory_server_url"
  ```

`sync_event_logs`
: ```default
  false
  ```

`sync_time`
: ```default
  true
  ```

`update_toolkit`
: ```default
  false
  ```

`upload_report`
: ```default
  false
  ```

`upload_reg_codes`
: ```default
  false
  ```

`upload_zero_touch_ids`
: ```default
  true
  ```

`flush_testlog`
: ```default
  false
  ```

## VerifyWidevineKeybox

### run_if

```default
constants.has_keybox
```

### pytest_name

[verify_keybox](../pytests/verify_keybox.md)

## WebGLAquarium

### pytest_name

[webgl_aquarium](../pytests/webgl_aquarium.md)

## WirelessCharger

### run_if

```default
not constants.has_device_data or device.component.has_wireless_charger
```

### pytest_name

[wireless_charge](../pytests/wireless_charge.md)

### args

`occupy_instruction`
: ```default
  "i18n! Attach peripheral to charging port"
  ```

`release_instruction`
: ```default
  "i18n! Remove peripheral from charging port"
  ```

## WriteDeviceDataToVPD

### pytest_name

[write_device_data_to_vpd](../pytests/write_device_data_to_vpd.md)

## WriteHWID

### pytest_name

[hwid](../pytests/hwid.md)

### args

`enable_factory_server`
: ```default
  "eval! constants.enable_factory_server"
  ```

`run_vpd`
: ```default
  "eval! constants.hwid_need_vpd"
  ```

`rma_mode`
: ```default
  "eval! constants.factory_process == 'RMA'"
  ```

## WriteProtectSwitch

### pytest_name

[write_protect_switch](../pytests/write_protect_switch.md)

## WriteRMAHWID

### pytest_name

[hwid](../pytests/hwid.md)

### args

`enable_factory_server`
: ```default
  "eval! constants.enable_factory_server"
  ```

`run_vpd`
: ```default
  "eval! constants.hwid_need_vpd"
  ```

`rma_mode`
: ```default
  true
  ```

## WriteTestHWID

### pytest_name

[exec_shell](../pytests/exec_shell.md)

### args

`commands`
: ```default
  [
    "hwid read",
    "hwid write \"$(hwid generate_test)\""
  ]
  ```

## CECHDMI1

### Serial subtests

- ```default
  {
    "inherit": "CheckDisplay",
    "locals": {
      "display": "eval! constants.hdmi1"
    }
  }
  ```
- ```default
  {
    "args": {
      "index": 1
    },
    "inherit": "CEC"
  }
  ```

## CECHDMI2

### Serial subtests

- ```default
  {
    "inherit": "CheckDisplay",
    "locals": {
      "display": "eval! constants.hdmi2"
    }
  }
  ```
- [CEC]()

## CECUSBTypeCHDMI

### Serial subtests

- ```default
  {
    "args": {
      "connect_only": true,
      "start_output_only": false,
      "stop_output_only": false
    },
    "inherit": "USBTypeCManualExternalDisplay"
  }
  ```
- ```default
  {
    "args": {
      "index": 1
    },
    "inherit": "CEC"
  }
  ```

## ClearFactoryVPDEntries

### Serial subtests

- ```default
  {
    "args": {
      "commands": "gooftool clear_factory_vpd_entries"
    },
    "inherit": "ExecShell",
    "label": "Clear factory VPD entries",
    "related_components": [
      "test_tags.TestCategory.VPD"
    ]
  }
  ```
- RebootStep

## ColdReset

### Serial subtests

- ```default
  {
    "args": {
      "commands": "ectool reboot_ec cold at-shutdown"
    },
    "inherit": "ExecShell",
    "label": "EC Cold Reset"
  }
  ```
- HaltStep

## EnableECWriteProtect

This test group explicitly disables factory mode and enables EC write protection after rebooting. Run this test group before finalization if the project uses STM32 chips for EC, otherwise finalization may fail. STM32 chips are likely to be used in ARM projects, and they require an EC reboot to let write protect settings take effect. Note that this disables the factory mode in advance, usually we disable the factory mode in finalize step. So it’s better to run this test as close to finalize step.

### Serial subtests

- ```default
  {
    "args": {
      "commands": [
        "gsctool -a -F disable | true",
        "ectool flashprotect enable",
        "ectool reboot_ec RO at-shutdown"
      ]
    },
    "pytest_name": "exec_shell"
  }
  ```
- RebootStep

## HWButton

### Serial subtests

- ```default
  {
    "args": {
      "button_key_name": "KEY_VOLUMEDOWN",
      "button_name": "i18n! Volume Down"
    },
    "inherit": "Button",
    "label": "Volume Down"
  }
  ```
- ```default
  {
    "args": {
      "button_key_name": "KEY_VOLUMEUP",
      "button_name": "i18n! Volume Up"
    },
    "inherit": "Button",
    "label": "Volume Up"
  }
  ```
- ```default
  {
    "args": {
      "button_key_name": "KEY_POWER",
      "button_name": "i18n! Power Button"
    },
    "inherit": "Button",
    "label": "Power Button"
  }
  ```

## RecoveryButtonGroup

### Serial subtests

- [UnloadECButtonDriver]()
- ```default
  {
    "args": {
      "button_key_name": "ectool:-H1_EC_RECOVERY_BTN_ODL",
      "button_name": "i18n! Recovery Button"
    },
    "inherit": "Button",
    "label": "Recovery Button"
  }
  ```
- [LoadECButtonDriver]()

## SetWidevineKeyboxGroup

### run_if

```default
constants.has_keybox
```

### Serial subtests

- ```default
  {
    "args": {
      "commands": "vpd -d widevine_keybox; rm /var/lib/oemcrypto/wrapped_amd_keybox || true"
    },
    "inherit": "ExecShell",
    "label": "Reset Widevine keyboxes"
  }
  ```
- RebootStep
- [SetWidevineKeybox]()

## StationEnd

### Serial subtests

- [StationEndSyncFactoryServer]()
- [Barrier]()
- [ShopfloorNotifyEnd]()
- [Barrier]()
- [WriteDeviceDataToVPD]()

## StationStart

### Serial subtests

- [SyncFactoryServer]()
- [Barrier]()
- [ShopfloorNotifyStart]()

## USBTypeAManualLeft

### Serial subtests

- ```default
  {
    "args": {
      "sysfs_path": "eval! constants.typea_usb.left.usb2_sysfs_path"
    },
    "inherit": "USBPerformance",
    "label": "USB2 TypeA Performance",
    "run_if": "constants.typea_usb.left.usb2_sysfs_path != ''"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! constants.typea_usb.left.usb3_sysfs_path"
    },
    "inherit": "USBPerformance",
    "label": "USB3 TypeA Performance",
    "run_if": "constants.typea_usb.left.usb3_sysfs_path != ''"
  }
  ```

## USBTypeAManualRight

### Serial subtests

- ```default
  {
    "args": {
      "sysfs_path": "eval! constants.typea_usb.right.usb2_sysfs_path"
    },
    "inherit": "USBPerformance",
    "label": "USB2 TypeA Performance",
    "run_if": "constants.typea_usb.right.usb2_sysfs_path != ''"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! constants.typea_usb.right.usb3_sysfs_path"
    },
    "inherit": "USBPerformance",
    "label": "USB3 TypeA Performance",
    "run_if": "constants.typea_usb.right.usb3_sysfs_path != ''"
  }
  ```

## USBTypeAManualTest

### Serial subtests

- [USBTypeAManualLeft]()
- [USBTypeAManualRight]()

## USBTypeATest

### Serial subtests

- [USBTypeAManualLeft]()
- [USBTypeAManualRight]()

## USBTypeCManualBase

### Serial subtests

- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb3_sysfs_path",
      "usbpd_port_polarity": [
        "eval! locals.usb.usbpd_id",
        1
      ]
    },
    "inherit": "USBPerformance",
    "label": "USB3 CC1 Performance"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb3_sysfs_path",
      "usbpd_port_polarity": [
        "eval! locals.usb.usbpd_id",
        2
      ]
    },
    "inherit": "USBPerformance",
    "label": "USB3 CC2 Performance"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb2_sysfs_path"
    },
    "inherit": "USBPerformance",
    "label": "USB2 Performance"
  }
  ```
- ```default
  {
    "args": {
      "controller_port": "eval! locals.usb.tbt_controller_port",
      "usbpd_spec": {
        "port": "eval! locals.usb.usbpd_id"
      }
    },
    "inherit": "TBTLoopback"
  }
  ```
- [USBTypeCManualChargeItems]()
- [USBTypeCManualExternalDisplay]()
- [Barrier]()

## USBTypeCManualChargeItems

### Serial subtests

- ```default
  {
    "inherit": "USBTypeCManualCharge",
    "label": "20V Charging",
    "locals": {
      "voltage": 20
    }
  }
  ```
- ```default
  {
    "inherit": "USBTypeCManualCharge",
    "label": "5V Charging",
    "locals": {
      "voltage": 5
    }
  }
  ```

## USBTypeCManualLeft

### Serial subtests

- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb3_sysfs_path",
      "usbpd_port_polarity": [
        "eval! locals.usb.usbpd_id",
        1
      ]
    },
    "inherit": "USBPerformance",
    "label": "USB3 CC1 Performance"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb3_sysfs_path",
      "usbpd_port_polarity": [
        "eval! locals.usb.usbpd_id",
        2
      ]
    },
    "inherit": "USBPerformance",
    "label": "USB3 CC2 Performance"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb2_sysfs_path"
    },
    "inherit": "USBPerformance",
    "label": "USB2 Performance"
  }
  ```
- ```default
  {
    "args": {
      "controller_port": "eval! locals.usb.tbt_controller_port",
      "usbpd_spec": {
        "port": "eval! locals.usb.usbpd_id"
      }
    },
    "inherit": "TBTLoopback"
  }
  ```
- [USBTypeCManualChargeItems]()
- [USBTypeCManualExternalDisplay]()
- [Barrier]()

## USBTypeCManualRight

### Serial subtests

- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb3_sysfs_path",
      "usbpd_port_polarity": [
        "eval! locals.usb.usbpd_id",
        1
      ]
    },
    "inherit": "USBPerformance",
    "label": "USB3 CC1 Performance"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb3_sysfs_path",
      "usbpd_port_polarity": [
        "eval! locals.usb.usbpd_id",
        2
      ]
    },
    "inherit": "USBPerformance",
    "label": "USB3 CC2 Performance"
  }
  ```
- ```default
  {
    "args": {
      "sysfs_path": "eval! locals.usb.usb2_sysfs_path"
    },
    "inherit": "USBPerformance",
    "label": "USB2 Performance"
  }
  ```
- ```default
  {
    "args": {
      "controller_port": "eval! locals.usb.tbt_controller_port",
      "usbpd_spec": {
        "port": "eval! locals.usb.usbpd_id"
      }
    },
    "inherit": "TBTLoopback"
  }
  ```
- [USBTypeCManualChargeItems]()
- [USBTypeCManualExternalDisplay]()
- [Barrier]()

## USBTypeCManualTest

### Serial subtests

- [USBTypeCManualLeft]()
- [USBTypeCManualRight]()

## USBTypeCTest

### Serial subtests

- [USBTypeCManualLeft]()
- [USBTypeCManualRight]()

## UpdateFirmware

### Serial subtests

- ```default
  {
    "pytest_name": "update_firmware"
  }
  ```
- [Barrier]()
- ```default
  {
    "args": {
      "operation": "eval! constants.update_firmware.reboot_type"
    },
    "inherit": "ShutdownStep",
    "label": "Reboot"
  }
  ```
