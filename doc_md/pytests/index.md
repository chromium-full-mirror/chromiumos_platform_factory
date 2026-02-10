# List of Factory Tests (pytests)

This document describes all tests available throughout the
factory code.

<!-- Include a hidden toctree so Sphinx won't complain about missing
documents.  We'll generate all the links ourselves in
generate_rst.py. -->

## Notes

The components here are AVL components. See this [link](../hwid/index.md) for
the mapping of HWID component and AVL components.

## Tests for [Accelerometer/IMU](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Accelerometer%2FIMU")

| pytest name                                                 | description                                                    |
|-------------------------------------------------------------|----------------------------------------------------------------|
| [accelerometers](accelerometers.md)                         | A factory test for reading accelerometers                      |
| [accelerometers_calibration](accelerometers_calibration.md) | A factory test for accelerometers calibration.                 |
| [accelerometers_lid_angle](accelerometers_lid_angle.md)     | This is a lid angle test based on accelerometers.              |
| [gyroscope](gyroscope.md)                                   | A factory test for gyroscopes.                                 |
| [gyroscope_angle](gyroscope_angle.md)                       | A factory test for gyroscopes.                                 |
| [gyroscope_calibration](gyroscope_calibration.md)           | A factory test for gyroscopes calibration.                     |
| [spatial_sensor_calibration](spatial_sensor_calibration.md) | Perform calibration on spatial sensors                         |
| [tablet_rotation](tablet_rotation.md)                       | Tests screen rotation through ChromeOS and accelerometer data. |

## Tests for [Ambient Light Sensor](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Ambient+Light+Sensor")

| pytest name                     | description                              |
|---------------------------------|------------------------------------------|
| [light_sensor](light_sensor.md) | A factory test for ambient light sensor. |

## Tests for [Audio Jack Codec](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Audio+Jack+Codec")

| pytest name                             | description                                               |
|-----------------------------------------|-----------------------------------------------------------|
| [audio](audio.md)                       | Tests audio playback.                                     |
| [audio_basic](audio_basic.md)           | Test basic audio record and playback.                     |
| [audio_diagnostic](audio_diagnostic.md) | Tests to manually test audio playback and record quality. |

## Tests for [Battery](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Battery")

| pytest name                           | description                                                             |
|---------------------------------------|-------------------------------------------------------------------------|
| [battery](battery.md)                 | A test to check if DUT can communicate with battery.                    |
| [battery_basic](battery_basic.md)     | A basic battery test.                                                   |
| [battery_current](battery_current.md) | A factory test to test battery charging/discharging current.            |
| [battery_cycle](battery_cycle.md)     | This test cycles the battery.                                           |
| [battery_sysfs](battery_sysfs.md)     | A hardware test for checking battery existence and its basic status.    |
| [bcic](bcic.md)                       | A test to set and check BC(battery config) in CBI(ChromeOS Board Info). |
| [blocking_charge](blocking_charge.md) | Test that waits the battery to be charged to specific level.            |
| [charger](charger.md)                 | Test if the charger can charge battery in time.                         |

## Tests for [CPU](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"CPU")

| pytest name                       | description                                                        |
|-----------------------------------|--------------------------------------------------------------------|
| [stressapptest](stressapptest.md) | A test to stress CPU, memory and disk.                             |
| [thermal_load](thermal_load.md)   | Tests thermal response under load.                                 |
| [thermal_slope](thermal_slope.md) | Determines how fast the processor heats/cools.                     |
| [urandom](urandom.md)             | A factory test to stress CPU, by generating pseudo random numbers. |

## Tests for [Camera - MIPI](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Camera+-+MIPI")

| pytest name         | description              |
|---------------------|--------------------------|
| [camera](camera.md) | Fixtureless camera test. |

## Tests for [Camera - USB](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Camera+-+USB")

| pytest name         | description              |
|---------------------|--------------------------|
| [camera](camera.md) | Fixtureless camera test. |
| [vsync](vsync.md)   | VSync pin test.          |

## Tests for [Card Reader](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Card+Reader")

| pytest name                               | description                             |
|-------------------------------------------|-----------------------------------------|
| [removable_storage](removable_storage.md) | Tests accessing to a removable storage. |

## Tests for [Display Panel](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Display+Panel")

| pytest name                                                                           | description                                                                |
|---------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| [backlight](backlight.md)                                                             | Test display backlight.                                                    |
| [brightness.lcd_backlight](brightness.lcd_backlight.md)                               | This is a factory test to check the functionality of LCD backlight module. |
| [display](display.md)                                                                 | Test display functionality.                                                |
| [display_images](display_images.md)                                                   | A station-based factory test to test the function of display.              |
| [display_interactive.display_interactive](display_interactive.display_interactive.md) | Test display functionality with interactive mode.                          |
| [display_point](display_point.md)                                                     | A factory test to test the function of display panel using some points.    |
| [edp_panel_timing](edp_panel_timing.md)                                               | Test eDP panel is supported with proper timing.                            |
| [privacy_screen](privacy_screen.md)                                                   | Test that sets privacy screen to specific state.                           |

## Tests for [EC](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"EC")

| pytest name                           | description                                                            |
|---------------------------------------|------------------------------------------------------------------------|
| [update_firmware](update_firmware.md) | Runs chromeos-firmwareupdate to force update Main(AP)/EC/PD firmwares. |

## Tests for [Ethernet controller](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Ethernet+controller")

| pytest name             | description                                     |
|-------------------------|-------------------------------------------------|
| [ethernet](ethernet.md) | A factory test for basic ethernet connectivity. |

## Tests for [Fingerprint Sensor](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Fingerprint+Sensor")

| pytest name                                           | description                                     |
|-------------------------------------------------------|-------------------------------------------------|
| [fingerprint_sensor_elan](fingerprint_sensor_elan.md) | A factory test for the Elan fingerprint sensor. |
| [fingerprint_sensor_fpc](fingerprint_sensor_fpc.md)   | A factory test for the FPC fingerprint sensor.  |
| [update_fpmcu_firmware](update_fpmcu_firmware.md)     | Update Fingerprint MCU firmware.                |

## Tests for [HPS (Human Presence Sensor)](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"HPS+%28Human+Presence+Sensor%29")

| pytest name   | description                                     |
|---------------|-------------------------------------------------|
| [hps](hps.md) | A factory test for HPS (Human Presence Sensor). |

## Tests for [Memory](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Memory")

| pytest name                       | description                                                       |
|-----------------------------------|-------------------------------------------------------------------|
| [memory_size](memory_size.md)     | Test if the memory size is correctly written in the firmware.     |
| [mrc_cache](mrc_cache.md)         | A factory test to initiate and verify memory re-training process. |
| [stressapptest](stressapptest.md) | A test to stress CPU, memory and disk.                            |

## Tests for [Proximity(SAR) Sensor](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Proximity%28SAR%29+Sensor")

| pytest name                             | description                                                       |
|-----------------------------------------|-------------------------------------------------------------------|
| [proximity_sensor](proximity_sensor.md) | A test to check if the proximity sensor triggers events properly. |

## Tests for [SPI Flash](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"SPI+Flash")

| pytest name                                       | description                                                            |
|---------------------------------------------------|------------------------------------------------------------------------|
| [get_intel_desc_status](get_intel_desc_status.md) | Gets the status of Intel SI_DESC and sets the status to device data.   |
| [update_firmware](update_firmware.md)             | Runs chromeos-firmwareupdate to force update Main(AP)/EC/PD firmwares. |

## Tests for [Secure Element](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Secure+Element")

| pytest name                                           | description                                                        |
|-------------------------------------------------------|--------------------------------------------------------------------|
| [check_cr50_board_id](check_cr50_board_id.md)         | Check the board ID of the Cr50 firmware.                           |
| [check_secdata_version](check_secdata_version.md)     | A factory test to check the secdata version.                       |
| [clear_inactive_gsc_slot](clear_inactive_gsc_slot.md) | Clears the inactive GSC RW slot.                                   |
| [cr50_ap_ro_hash](cr50_ap_ro_hash.md)                 | A test to set/clear AP RO hash.                                    |
| [cr50_ap_ro_verification](cr50_ap_ro_verification.md) | A test to ensure the AP RO verification works.                     |
| [ti50_ap_ro_verification](ti50_ap_ro_verification.md) | A test to ensure the AP RO verification works on Ti50.             |
| [tpm_clear_owner](tpm_clear_owner.md)                 | Requests that the firmware clear the TPM owner on the next reboot. |
| [tpm_diagnosis](tpm_diagnosis.md)                     | Runs tpm_selftest to perform TPM self-diagnosis.                   |
| [tpm_state](tpm_state.md)                             | A test to check the state of TPM die.                              |
| [tpm_verify_ek](tpm_verify_ek.md)                     | Verifies the TPM endorsement key.                                  |
| [update_cr50_firmware](update_cr50_firmware.md)       | Update Cr50 firmware.                                              |

## Tests for [Smart Speaker Amplifier](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Smart+Speaker+Amplifier")

| pytest name                             | description                                               |
|-----------------------------------------|-----------------------------------------------------------|
| [audio](audio.md)                       | Tests audio playback.                                     |
| [audio_basic](audio_basic.md)           | Test basic audio record and playback.                     |
| [audio_diagnostic](audio_diagnostic.md) | Tests to manually test audio playback and record quality. |
| [dsm_calibration](dsm_calibration.md)   | A factory test to calibrate the smart speaker amplifier.  |

## Tests for [Speaker Amplifier](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Speaker+Amplifier")

| pytest name                             | description                                               |
|-----------------------------------------|-----------------------------------------------------------|
| [audio](audio.md)                       | Tests audio playback.                                     |
| [audio_basic](audio_basic.md)           | Test basic audio record and playback.                     |
| [audio_diagnostic](audio_diagnostic.md) | Tests to manually test audio playback and record quality. |

## Tests for [Storage](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Storage")

| pytest name                                       | description                                                  |
|---------------------------------------------------|--------------------------------------------------------------|
| [bad_blocks](bad_blocks.md)                       | Tests a storage device by running the badblocks command.     |
| [storage_simple_stress](storage_simple_stress.md) | Performs consecutive read/write operations on a single file. |
| [stressapptest](stressapptest.md)                 | A test to stress CPU, memory and disk.                       |
| [verify_root_partition](verify_root_partition.md) | Verifies the integrity of the root partition.                |

## Tests for [Storage bridge (PCIE-eMMC)](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Storage+bridge+%28PCIE-eMMC%29")

| pytest name                                       | description                                                  |
|---------------------------------------------------|--------------------------------------------------------------|
| [bad_blocks](bad_blocks.md)                       | Tests a storage device by running the badblocks command.     |
| [storage_simple_stress](storage_simple_stress.md) | Performs consecutive read/write operations on a single file. |
| [stressapptest](stressapptest.md)                 | A test to stress CPU, memory and disk.                       |

## Tests for [TPM](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"TPM")

| pytest name                                       | description                                                        |
|---------------------------------------------------|--------------------------------------------------------------------|
| [check_secdata_version](check_secdata_version.md) | A factory test to check the secdata version.                       |
| [tpm_clear_owner](tpm_clear_owner.md)             | Requests that the firmware clear the TPM owner on the next reboot. |
| [tpm_diagnosis](tpm_diagnosis.md)                 | Runs tpm_selftest to perform TPM self-diagnosis.                   |
| [tpm_state](tpm_state.md)                         | A test to check the state of TPM die.                              |
| [tpm_verify_ek](tpm_verify_ek.md)                 | Verifies the TPM endorsement key.                                  |

## Tests for [Touch screen Controller (non stylus)](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Touch+screen+Controller+%28non+stylus%29")

| pytest name                                         | description                               |
|-----------------------------------------------------|-------------------------------------------|
| [touch_device_fw_update](touch_device_fw_update.md) | Checks and updates touch device firmware. |

## Tests for [Touch screen controller (EMR Stylus)](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Touch+screen+controller+%28EMR+Stylus%29")

| pytest name                                         | description                               |
|-----------------------------------------------------|-------------------------------------------|
| [touch_device_fw_update](touch_device_fw_update.md) | Checks and updates touch device firmware. |

## Tests for [Touch screen controller (USI Stylus)](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Touch+screen+controller+%28USI+Stylus%29")

| pytest name                                         | description                               |
|-----------------------------------------------------|-------------------------------------------|
| [touch_device_fw_update](touch_device_fw_update.md) | Checks and updates touch device firmware. |

## Tests for [Touchpad Controller](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Touchpad+Controller")

| pytest name                                         | description                                   |
|-----------------------------------------------------|-----------------------------------------------|
| [touch_device_fw_update](touch_device_fw_update.md) | Checks and updates touch device firmware.     |
| [touch_uniformity](touch_uniformity.md)             | A factory test for checking touch uniformity. |

## Tests for [USB Composite Integrated Component](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"USB+Composite+Integrated+Component")

| pytest name                               | description                                                  |
|-------------------------------------------|--------------------------------------------------------------|
| [battery_current](battery_current.md)     | A factory test to test battery charging/discharging current. |
| [removable_storage](removable_storage.md) | Tests accessing to a removable storage.                      |

## Tests for [WWAN](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"WWAN")

| pytest name                                   | description                                            |
|-----------------------------------------------|--------------------------------------------------------|
| [modem_security](modem_security.md)           | Verify and close modem access authority.               |
| [probe_sim_card_tray](probe_sim_card_tray.md) | Probes SIM card tray                                   |
| [vswr.vswr](vswr.vswr.md)                     | VSWR measures the efficiency of the transmission line. |

## Tests for [Wifi / Bluetooth](https://chromeos.google.com/partner/dlm/avl/component?q=componentType:"Wifi+%2F+Bluetooth")

| pytest name                                           | description                                                              |
|-------------------------------------------------------|--------------------------------------------------------------------------|
| [bluetooth](bluetooth.md)                             | A factory test to verify the functionality of bluetooth device.          |
| [bluetooth_host](bluetooth_host.md)                   | Station-based Bluetooth scan and pair test, using hciconfig and hcitool. |
| [probe_device_info](probe_device_info.md)             | A factory test for probing device information and updating device data.  |
| [rf_graphyte.rf_graphyte](rf_graphyte.rf_graphyte.md) | Tests RF chip’s transmitting and receiving capabilities using Graphyte.  |
| [vswr.vswr](vswr.vswr.md)                             | VSWR measures the efficiency of the transmission line.                   |
| [wireless_antenna](wireless_antenna.md)               | A factory test for basic Wifi.                                           |
| [wireless_connect](wireless_connect.md)               | Connect to an AP.                                                        |

## Tests for CHROMEBOOK_PlUS (Device feature component)

| pytest name                           | description                            |
|---------------------------------------|----------------------------------------|
| [branded_chassis](branded_chassis.md) | A test to check if chassis is branded. |

## Tests for FAN (Device feature component)

| pytest name               | description                                            |
|---------------------------|--------------------------------------------------------|
| [fan_speed](fan_speed.md) | A factory test to ensure the functionality of CPU fan. |

## Tests for HARDWARE_ID (Device feature component)

| pytest name                   | description                                                                  |
|-------------------------------|------------------------------------------------------------------------------|
| [hwid](hwid.md)               | Uses HWID v3 to generate, encode, and verify the device’s HWID.              |
| [probe.probe](probe.probe.md) | A factory test to check if the components can be probed successfully or not. |

## Tests for KEYBOARD (Device feature component)

| pytest name                                 | description                                        |
|---------------------------------------------|----------------------------------------------------|
| [keyboard_backlight](keyboard_backlight.md) | This is a factory test to test keyboard backlight. |

## Tests for LED (Device feature component)

| pytest name                                               | description                                         |
|-----------------------------------------------------------|-----------------------------------------------------|
| [brightness.led_brightness](brightness.led_brightness.md) | This is a factory test to check the LED brightness. |

## Tests for PSR (Device feature component)

| pytest name                                   | description                                         |
|-----------------------------------------------|-----------------------------------------------------|
| [setup_psr_feature](setup_psr_feature.md)     | A test to set/check PSR EOM NVAR and start PSR Log. |
| [update_psr_oem_data](update_psr_oem_data.md) | A test to update and verify PSR OEM Data.           |

## Tests for THERMAL_SENSOR (Device feature component)

| pytest name                           | description                                    |
|---------------------------------------|------------------------------------------------|
| [thermal_load](thermal_load.md)       | Tests thermal response under load.             |
| [thermal_sensors](thermal_sensors.md) | Test for temperature sensors control.          |
| [thermal_slope](thermal_slope.md)     | Determines how fast the processor heats/cools. |

## Tests for VPD (Device feature component)

| pytest name                                                 | description                                                            |
|-------------------------------------------------------------|------------------------------------------------------------------------|
| [accelerometers_lid_angle](accelerometers_lid_angle.md)     | This is a lid angle test based on accelerometers.                      |
| [check_serial_number](check_serial_number.md)               | Checks if serial number is set correctly on a device.                  |
| [dsm_calibration](dsm_calibration.md)                       | A factory test to calibrate the smart speaker amplifier.               |
| [read_device_data_from_vpd](read_device_data_from_vpd.md)   | Setup device data from VPD (Vital Product Data).                       |
| [scan](scan.md)                                             | Prompts the operator to input a string of data.                        |
| [spatial_sensor_calibration](spatial_sensor_calibration.md) | Perform calibration on spatial sensors                                 |
| [update_device_data](update_device_data.md)                 | Updates Device Data (manually or from predefined values in test list). |
| [verify_keybox](verify_keybox.md)                           | A test to check the correctness of widevine keybox.                    |
| [write_device_data_to_vpd](write_device_data_to_vpd.md)     | Writes device data to VPD (Vital Product Data).                        |

## Uncategorized pytests

| pytest name                                                               | description                                                                                                            |
|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| [ac_power](ac_power.md)                                                   | A test to ensure the power type and status of device under test.                                                       |
| [bft_fixture](bft_fixture.md)                                             | A generic interface to control the BFT fixture.                                                                        |
| [brightness.brightness](brightness.brightness.md)                         | This is a factory test to check the brightness of LCD backlight or LEDs.                                               |
| [buzzer](buzzer.md)                                                       | This is a buzzer test.                                                                                                 |
| [cec](cec.md)                                                             | Test and check cec power control feature on Chrome OS device.                                                          |
| [check_image_version](check_image_version.md)                             | Check release or test OS image version on internal storage.                                                            |
| [check_pdc_firmware](check_pdc_firmware.md)                               | A test to check PDC firmware information.                                                                              |
| [check_release_lvm_stateful](check_release_lvm_stateful.md)               | Check if release image has enabled LVM stateful partition.                                                             |
| [check_retimer_firmware](check_retimer_firmware.md)                       | Check the retimer firmware version.                                                                                    |
| [check_test_list](check_test_list.md)                                     | A step to check test list.                                                                                             |
| [compass](compass.md)                                                     | Compass test which requires operator place the DUT heading north and south.                                            |
| [copy_minios](copy_minios.md)                                             | Selectively copies the miniOS part that has the same recovery key ver as FW.                                           |
| [countdown](countdown.md)                                                 | A count down monitor for better user interface in run-in tests.                                                        |
| [download_from_factory_drive](download_from_factory_drive.md)             | Retrieve factory drive files from factory server.                                                                      |
| [exec_python](exec_python.md)                                             | A test to run arbitrary python scripts.                                                                                |
| [exec_shell](exec_shell.md)                                               | A test to invoke a list of shell commands.                                                                             |
| [factory_state](factory_state.md)                                         | A pytest helps you control FactoryStateLayer                                                                           |
| [flash_netboot](flash_netboot.md)                                         | Flash system main (AP) firmware to netboot firmware.                                                                   |
| [lightbar](lightbar.md)                                                   | Factory test for lightbar on A-case.                                                                                   |
| [line_check_item](line_check_item.md)                                     | A factory test to interactively check a sequence of shell commands on DUT.                                             |
| [message](message.md)                                                     | Displays a message.                                                                                                    |
| [model_sku](model_sku.md)                                                 | A test to confirm and set SKU information.                                                                             |
| [network_setup.network_setup](network_setup.network_setup.md)             | A pytest to wait operators setup network connection.                                                                   |
| [nop](nop.md)                                                             | An no-op test.                                                                                                         |
| [partition_table](partition_table.md)                                     | Checks that the partition table extends nearly to the end of the storage<br/>device.                                   |
| [pd_fw_min_version](pd_fw_min_version.md)                                 | Check firmware version of PD (TCPC) chip equal to or larger than minimum<br/>version noted in corresponding EC driver. |
| [ping_test](ping_test.md)                                                 | Ping connection test.                                                                                                  |
| [plankton_cc2_pull_test](plankton_cc2_pull_test.md)                       | Plankton USB type-C CC2 function test for Whale fixture.                                                               |
| [plankton_cc_flip_check](plankton_cc_flip_check.md)                       | USB type-C CC line polarity check and operation flip test w/ Plankton-Raiden.                                          |
| [plankton_charge](plankton_charge.md)                                     | Test USB type-C port charging function with Plankton-Raiden board.                                                     |
| [read_device_data_from_cros_config](read_device_data_from_cros_config.md) | Setup device data from ChromeOS Config.                                                                                |
| [record_csv_entry_example](record_csv_entry_example.md)                   | An example pytest to show case how to save a CSV entry.                                                                |
| [retrieve_config](retrieve_config.md)                                     | Retrieve JSON config file from either an USB stick or a factory server.                                                |
| [robot_movement](robot_movement.md)                                       | Control a robot to move a device for testing specific sensors.                                                         |
| [sample_customized_test](sample_customized_test.md)                       | This is the sample code of a board specific test.                                                                      |
| [select_for_sampling](select_for_sampling.md)                             | Decide if this device is selected for certain sampling tests.                                                          |
| [shopfloor_service](shopfloor_service.md)                                 | Invoke remote procedure call for interaction with shopfloor backend.                                                   |
| [shutdown](shutdown.md)                                                   | Shutdown/Reboot the device.                                                                                            |
| [station_entry](station_entry.md)                                         | Starts or ends a station-based test.                                                                                   |
| [station_setup](station_setup.md)                                         | Setup a station for station-based test.                                                                                |
| [summary](summary.md)                                                     | Displays a status summary for all tests in the current section.                                                        |
| [suspend_resume](suspend_resume.md)                                       | Suspend and resume device with given cycles.                                                                           |
| [suspend_stress](suspend_stress.md)                                       | Suspend and resume device with given cycles.                                                                           |
| [switch_test_list](switch_test_list.md)                                   | A step to switch test list.                                                                                            |
| [sync_time](sync_time.md)                                                 | Sync the clock of DUT with the clock of station.                                                                       |
| [thunderbolt_loopback](thunderbolt_loopback.md)                           | Tests thunderbolt port with a loopback card.                                                                           |
| [update_detachable_base](update_detachable_base.md)                       | Detachable base update test                                                                                            |
| [update_kernel](update_kernel.md)                                         | Applies new kernel to DUT (for testing).                                                                               |
| [update_plugin_firmware](update_plugin_firmware.md)                       | Update vendor plugin firmware using fwupdtool.                                                                         |
| [verify_component](verify_component.md)                                   | Verify peripheral components.                                                                                          |
| [video_playback](video_playback.md)                                       | A video playback test.                                                                                                 |
| [wait_external_test](wait_external_test.md)                               | A stub test waiting for external fixture to finish testing.                                                            |
| [wait_fixture_ready](wait_fixture_ready.md)                               | Waits Fixture until it’s ready.                                                                                        |
| [webgl_aquarium](webgl_aquarium.md)                                       | WebGL performance test that executes a set of WebGL operations.                                                        |
| [whale_check_voltage](whale_check_voltage.md)                             | Checks voltages.                                                                                                       |
| [whale_cover](whale_cover.md)                                             | Checks if Whale’s cover is opened / closed.                                                                            |
| [wireless_charge](wireless_charge.md)                                     | Test wireless charge port functionality.                                                                               |
| [write_protect_switch](write_protect_switch.md)                           | Verifies that the write-protect switch is on.                                                                          |
