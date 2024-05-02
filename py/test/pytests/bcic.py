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
4. Clear and write the information to the CBI.
5. Check the information in the CBI to ensure that battery config saved in CBI
   is identical to the active battery config.


Dependency
----------
- ``ectool``


Examples
--------
To update BCIC::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "SET",
      "update_hwid_bundle": true
    }
  }

To check BCIC::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "CHECK",
      "update_hwid_bundle": false
    }
  }

"""

import enum
import logging
import subprocess

from cros.factory.device import device_utils
from cros.factory.hwid.v3 import hwid_utils
from cros.factory.test import test_case
from cros.factory.test import test_tags
from cros.factory.test.utils import cbi_utils
from cros.factory.test.utils import update_utils
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import json_utils


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
    if self.args.action == EnumAction.SET:  # type: ignore #TODO(b/338318729) Fixit!
      self.assertTrue(
          self.args.use_latest_hwid_bundle != bool(self.args.file_path),  # type: ignore #TODO(b/338318729) Fixit!
          'Provide either a `file_path` or enable `use_latest_hwid_bundle`'
          'to indicate the battery config source')

  def runTest(self):
    if self.args.use_latest_hwid_bundle:  # type: ignore #TODO(b/338318729) Fixit!
      update_utils.UpdateHWIDDatabase(self._dut)

    if self.args.action == EnumAction.SET:  # type: ignore #TODO(b/338318729) Fixit!
      file_path = (
          self.args.file_path or  # type: ignore #TODO(b/338318729) Fixit!
          hwid_utils.LoadBatteryConfigIntoFile(self._dut))
      manufacturer = self._dut.power.GetBatteryManufacturer()
      device_name = self._dut.power.GetBatteryDeviceName()

      self.VerifyBatteryConfigExists(file_path, manufacturer, device_name)
      self.ClearExistingBatteryConfig()
      self.ApplyNewBatteryConfig(file_path, manufacturer, device_name)
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

  def VerifyBatteryConfigExists(self, file_path, manufacturer, device_name):
    """Verifies the existence of a battery configuration file.

    Ensures that the configuration file:
        * Exists
        * Contains a valid JSON payload
        * Includes the expected key within the JSON data
    """

    self._ExecuteBatteryConfigCmd('search', file_path, manufacturer,
                                  device_name)

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
      logging.info('Battery config is cleared. Now it is all 0s.')

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

  def GetBatteryConfig(self, index: str) -> dict:
    """Retrieves battery configuration information from the device.

    Args:
      index: To specify the battery configuration you want:
        * Leave it empty ('') to get the active configuration.
        * Set it to '0' to get the first available configuration.

    Returns:
      dict: A dictionary containing flattened battery configuration data.

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
    battery_config_dict = self.FlattenDict(json_utils.LoadStr(stdout), '.')
    logging.info('Got config in flatten dict form: %s', battery_config_dict)
    return battery_config_dict

  def FlattenDict(self, nested_dict, separator):

    def _flatten(item, prefix):
      if isinstance(item, dict):
        for key, value in item.items():
          yield from _flatten(value, prefix + separator + key)
      else:
        yield prefix, item

    return dict(_flatten(nested_dict, ''))
