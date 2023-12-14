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
3. Write the information to the CBI.
4. Check the information in the CBI to ensure that it is not empty.



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
import os
import subprocess

from cros.factory.device import device_utils
from cros.factory.test import test_case
from cros.factory.test import test_tags
from cros.factory.utils.arg_utils import Arg

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
      self.SetBCIC()
    else:
      self.CheckBCIC()

  def SetBCIC(self):
    model_name = cros_config.CrosConfig().GetModelName().lower()
    file_path = os.path.join(CONFIG_DIR, f'{model_name}_battery_config.json')
    battery_config_set_cmd = [
        'ectool', 'bcfg', 'set', file_path,
        self._dut.power.GetBatteryManufacturer(),
        self._dut.power.GetBatteryModelNumber()
    ]

    process = self._dut.Popen(battery_config_set_cmd, log=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    unused_stdout, stderr = process.communicate()
    if stderr:
      self.FailTask(stderr)

  def CheckBCIC(self):
    #TODO(b/297307194) add the check flow after EC reset
    pass
