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

1. Retrieve the OEM name and model number of battery from runtime probe.
2. Retrieve the required information from the battery configuration in the
   release image.
3. Clear and write the information to the CBI.
4. Check the information in the CBI to ensure that battery config saved in CBI
   is identical to the active battery config.


Dependency
----------
- ``ectool``
- cros_config


Examples
--------
To update BCIC::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "SET"
    }
  }

To check BCIC::

  {
    "pytest_name": "bcic",
    "args": {
      "action": "CHECK"
    }
  }

"""

import enum
import logging
import os
import subprocess

from cros.factory.device import device_utils
from cros.factory.test import test_case
from cros.factory.test import test_tags
from cros.factory.test.utils import cbi_utils
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import json_utils

from cros.factory.external.chromeos_cli import cros_config


CONFIG_DIR = '/usr/share/bcic'


class EnumAction(str, enum.Enum):
  SET = 'SET'
  CHECK = 'CHECK'


class BCICTest(test_case.TestCase):
  """Factory Test for setting and checking BCIC"""

  related_components = (test_tags.TestCategory.BATTERY, )
  ARGS = [Arg('action', EnumAction, "Which action to do.")]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()

  def runTest(self):
    if self.args.action == EnumAction.SET:
      self.ClearAndSetBCIC()
    else:
      self.CheckBCIC()

  def ClearAndSetBCIC(self):
    # Always clears the battery config saved in CBI before setting it.
    self.ClearBCIC()
    self.SetBCIC()

  def ClearBCIC(self):
    cbi_battery_config_hex = cbi_utils.GetCbiData(
        self._dut, cbi_utils.CbiDataName.BATTERY_CONFIG)
    logging.info('The battery config saved in CBI before clearing is: %s',
                 cbi_battery_config_hex)
    if cbi_battery_config_hex:
      size = len(cbi_battery_config_hex)
      cbi_utils.SetCbiData(self._dut, cbi_utils.CbiDataName.BATTERY_CONFIG,
                           '0' * size)
      logging.info('Battery config is cleared. Now it is all 0s.')

  def SetBCIC(self):
    model_name = cros_config.CrosConfig().GetModelName().lower()
    file_path = os.path.join(CONFIG_DIR, f'{model_name}.battery_config.json')
    battery_config_set_cmd = [
        'ectool', 'bcfg', 'set', file_path,
        self._dut.power.GetBatteryManufacturer(),
        self._dut.power.GetBatteryDeviceName()
    ]
    process = self._dut.Popen(battery_config_set_cmd, log=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    unused_stdout, stderr = process.communicate()
    if stderr:
      self.FailTask(f'Unable to set BCIC due to error: {stderr}')

  def CheckBCIC(self):
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

  def GetBatteryConfig(self, index) -> dict:
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
