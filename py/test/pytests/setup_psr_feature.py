# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A test to set/check PSR EOM NVAR and start PSR Log.

Description
-----------
This test does one of these action: set EOM NVAR(close manufacturing), check
EOM NVAR value equals 1 or start PSR log.

Test Procedure
--------------
This pytest does not require operator interaction.

Dependency
----------
- `intel-psrtool`

Examples
--------
To set PSR EOM NVAR, add this to test list::

  {
    "pytest_name": "setup_psr_feature",
    "args": {
      "action": "set"
    }
  }


To start PSR log, add this to test list::

  {
    "pytest_name": "setup_psr_feature",
    "args": {
      "action": "start"
    }
  }

"""
import enum

from cros.factory.test import device_data
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg

from cros.factory.external.chromeos_cli import intel_psrtool


KEY_PSR_UPDATE_NEED_REBOOT = device_data.JoinKeys(device_data.KEY_FACTORY,
                                                  'psr_update_need_reboot')

class EnumAction(str, enum.Enum):
  set = 'set'
  start = 'start'

  def __str__(self):
    return self.name


class PSRToolTest(test_case.TestCase):
  related_components = (test_case.TestCategory.PSR, )
  ARGS = [Arg('action', EnumAction, 'Which action to do.')]

  def setUp(self):
    self._intel_psr_tool = intel_psrtool.IntelPSRTool()

  def runTest(self):
    action = self.args.action  # type: ignore #TODO(b/338318729) Fixit!
    if action == EnumAction.set:
      self._intel_psr_tool.CloseManufacturing()
      device_data.UpdateDeviceData({KEY_PSR_UPDATE_NEED_REBOOT: True})
    else:
      EOM_NVAR = self._intel_psr_tool.GetManufacturingNVAR()
      self.assertEqual(
          1, EOM_NVAR, f'Current EOM NVAR value is {EOM_NVAR}. But it should '
          'be 1 after closing manufacturing and reboot')
      if self._intel_psr_tool.IsPSRSupported():
        self._intel_psr_tool.StartPSREventLog()
