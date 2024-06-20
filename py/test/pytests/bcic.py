# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A test to set and check BC(battery config) in CBI(ChromeOS Board Info).

Description
-----------
This test updates the battery config into CBI(BCIC).


Test Procedure
--------------
This is an automated test without user interaction.

1. Retrieve the OEM name and model number of battery from ectool.
2. (Optional) Connect to the factory server to update the HWID bundle.
3. Retrieve the required information from the battery configuration in the
   HWID bundle.
4. Search for the specific battery config in the JSON file:

- If found, clear and write the information to the CBI.
- If not found, check if the active battery config is valid or not. Pass the
  test if it's valid else fail the test.

  Note that since the JSON file might contain an updated config for a battery,
  we try to update from the JSON file whenever possible, even if the active
  battery config is already valid.

5. Check the information in the CBI to ensure that battery config saved in CBI
   is identical to the active battery config.


Dependency
----------
- ``ectool``


Examples
--------
To update BCIC from the latest hwid bundle::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "SET",
      "use_latest_hwid_bundle": true
    }
  }

To update BCIC from the local hwid bundle::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "SET",
      "use_latest_hwid_bundle": false
    }
  }


To update BCIC from a local battert config::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "SET",
      "use_latest_hwid_bundle": false
      "file_path": "/usr/share/bcic/rex.battery_config.json"
    }
  }

To check BCIC::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "CHECK",
      "use_latest_hwid_bundle": false
    }
  }

"""

import enum
import logging
import subprocess

from cros.factory.device import device_utils
from cros.factory.hwid.v3 import hwid_utils
from cros.factory.test import device_data
from cros.factory.test import test_case
from cros.factory.test import test_tags
from cros.factory.test.utils import cbi_utils
from cros.factory.test.utils import update_utils
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import json_utils


KEY_BCIC_UPDATE_NEED_REBOOT = device_data.JoinKeys(device_data.KEY_FACTORY,
                                                   'bcic_update_need_reboot')


class EnumAction(str, enum.Enum):
  SET = 'SET'
  CHECK = 'CHECK'


class BCICTest(test_case.TestCase):
  """Factory Test for setting and checking BCIC"""

  related_components = (test_tags.TestCategory.BATTERY, )
  ARGS = [
      Arg('action', EnumAction, "Which action to do."),
      Arg(
          'use_latest_hwid_bundle', bool,
          'Whether to update the HWID bundle first and load the battery config'
          'from it.'),
      Arg('file_path', str, 'The path to the battery config file.', default=''),
  ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    # yapf: disable
    if self.args.action == EnumAction.SET:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      if self.args.use_latest_hwid_bundle and self.args.file_path:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        raise ValueError('Conflicting options: Cannot use both latest HWID'
                         'bundle and a specified file path. Please choose one.')
      if not self.args.use_latest_hwid_bundle and not self.args.file_path:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        logging.warning('No HWID bundle source specified. Using the current'
                        'HWID bundle on DUT.')

  def runTest(self):
    # yapf: disable
    if self.args.use_latest_hwid_bundle:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      try:
        update_utils.UpdateHWIDDatabase(self._dut)
      except Exception as e:
        self.FailTask(f'Cannot update HWID database due to: {e}.')

    # yapf: disable
    if self.args.action == EnumAction.SET:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      file_path = (
          # yapf: disable
          self.args.file_path or  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          hwid_utils.LoadBatteryConfigIntoFile(self._dut))
      manufacturer = self._dut.power.GetBatteryManufacturer()
      device_name = self._dut.power.GetBatteryDeviceName()

      if self.IsBatteryConfigExisting(file_path, manufacturer, device_name):
        # Always save battery config in CBI if a valid battery config file
        # exists. More details at b/337226198#comment9.
        device_data.UpdateDeviceData({KEY_BCIC_UPDATE_NEED_REBOOT: True})
        self.ClearExistingBatteryConfig()
        self.ApplyNewBatteryConfig(file_path, manufacturer, device_name)
      elif self.IsActiveBatteryConfigValid(manufacturer, device_name):
        device_data.UpdateDeviceData({KEY_BCIC_UPDATE_NEED_REBOOT: False})
        logging.info('Pass the test without setting BCIC since the active'
                     'battery config is valid.')
      else:
        self.FailTask('Active battery config is invalid and there is no valid'
                      'battery config to load and update.')
    else:
      self.CheckBCIC()

  def _ExecuteBatteryConfigCmd(self, action, file_path, manufacturer,
                               device_name):
    """Executes a battery config command using `ectool` with a specified file.

    Args:
      action: The action to perform (e.g., 'search', 'set').
      file_path: The path to the battery configuration file.
      manufacturer: The manufacturer of the battery.
      device_name:  The name of the battery device.

    Raises:
      FailTask: If the command execution fails, indicating an error occurred
        during the battery configuration operation.
      """

    cmd = ['ectool', 'bcfg', action, file_path, manufacturer, device_name]
    process = self._dut.Popen(cmd, log=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    unused_stdout, stderr = process.communicate()

    if stderr:
      self.FailTask(f'Unable to {action} BCIC due to error: {stderr}')

  def IsBatteryConfigExisting(self, file_path, manufacturer,
                              device_name) -> bool:
    """Checks if a valid battery configuration file exists.

    Returns:
      True if the configuration file:
        * Exists
        * Contains a valid JSON payload
        * Includes the expected key within the JSON data
      False otherwise.
    """
    try:
      self._ExecuteBatteryConfigCmd('search', file_path, manufacturer,
                                    device_name)
    except Exception as e:
      logging.info('There is no valid battery config. Error message: %s', e)
      return False
    return True

  def ApplyNewBatteryConfig(self, file_path, manufacturer, device_name):
    """Applies a new battery configuration to CBI.

    Performs the following when applying the configuration:
      * Verifies that the configuration file contains a valid JSON payload.
      * Checks that the JSON data includes the expected keys.
    """

    self._ExecuteBatteryConfigCmd('set', file_path, manufacturer, device_name)

  def ClearExistingBatteryConfig(self):
    cbi_battery_config_hex = cbi_utils.GetCbiData(
        self._dut, cbi_utils.CbiDataName.BATTERY_CONFIG)
    logging.info('The battery config saved in CBI before clearing is: %s',
                 cbi_battery_config_hex)
    if cbi_battery_config_hex:
      size = len(cbi_battery_config_hex)
      cbi_utils.SetCbiData(self._dut, cbi_utils.CbiDataName.BATTERY_CONFIG,
                           '0' * size)
      logging.info('Battery config in CBI is cleared. Now it is all 0s.')

  def CheckBCIC(self):
    """Checks between the active and a stored battery configuration.

    Compares the active battery configuration to the configuration indexed as
    '0'. Identifies missing keys and value mismatches between the two.

    Raises:
      ValueError: If inconsistencies exist between the active and stored
        configurations. The error message details the mismatches.
    """

    active_battery_config = self.GetBatteryConfig('')
    cbi_stored_battery_config = self.GetBatteryConfig('0')
    mismatches = []
    for key in active_battery_config:
      if key not in cbi_stored_battery_config:
        mismatches.append(f'Key: {key} missing in stored config')
      elif active_battery_config[key] != cbi_stored_battery_config[key]:
        mismatches.append(f'Value for {key} differs: (active: '
                          f'{active_battery_config[key]}, stored: '
                          f'{cbi_stored_battery_config[key]})')
    for key in cbi_stored_battery_config:
      if key not in active_battery_config:
        mismatches.append(f'Key {key} missing in active config')

    if mismatches:
      error_message = 'Battery configurations differ:\n'
      error_message += '\n'.join(mismatches)
      raise ValueError(error_message)

  def GetBatteryConfig(self, index: str, flatten: bool = True) -> dict:
    """Retrieves battery configuration information from the device.

    Args:
      index: To specify the battery configuration you want:
        * Leave it empty ('') to get the active configuration.
        * Set it to '0' to get the first available configuration.
      flatten: (Optional) Determines the format of the returned dictionary:
        * True (default): Flattens the dictionary using '.' as a separator.
        * False: Returns the dictionary in its original nested structure.

    Returns:
      dict: A dictionary containing battery configuration data.
        * If `flatten` is True: Keys are flattened (e.g., 'aa.bbb.c').
        * If `flatten` is False: Keys reflect the original structure.

    Raises:
      ValueError: If an error occurs while retrieving the configuration
        information.
    """

    battery_config_get_cmd = ['ectool', 'bcfg', 'get']
    if index:
      battery_config_get_cmd.append(index)
    process = self._dut.Popen(battery_config_get_cmd, log=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
      raise ValueError(f'Unable to get battery config due to error: {stderr}.')
    battery_config_dict = json_utils.LoadStr(stdout)
    if flatten:
      battery_config_dict = self.FlattenDict(battery_config_dict, '.')
      logging.info('Got config in flatten dict form: %s', battery_config_dict)
    return battery_config_dict

  def FlattenDict(self, nested_dict, separator):
    """Flattens a nested dictionary using the specified separator."""

    return dict(self._flatten_generator(nested_dict, '', separator))

  def _flatten_generator(self, item, prefix, separator):
    """Generator yielding flattened key-value pairs."""

    if isinstance(item, dict):
      for key, value in item.items():
        new_prefix = key if not prefix else prefix + separator + key
        yield from self._flatten_generator(value, new_prefix, separator)
    else:
      yield prefix, item

  def IsActiveBatteryConfigValid(self, probed_manufacturer: str,
                                 probed_device_name: str) -> bool:
    """Validates if the probed battery info matches the active config.

    This function fetches the active battery configuration from the device,
    extracts the manufacturer and device name, and then compares them to the
    provided `probed_manufacturer` and `probed_device_name`.

    Args:
      probed_manufacturer: The manufacturer name probed from the device.
      probed_device_name: The device name probed from the device.

    Returns:
      bool: True if IDs match, False otherwise.
    """

    active_battery_config = self.GetBatteryConfig('', flatten=False)
    active_manufacturer, active_device_name = next(
        iter(active_battery_config.keys())).split(',')
    return (probed_manufacturer == active_manufacturer and
            probed_device_name == active_device_name)
