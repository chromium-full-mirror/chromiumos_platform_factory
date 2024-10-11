# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A factory test to initiate and verify memory re-training process.

Description
-----------
The test either requests memory re-training on next boot (if ``mode`` is
``'create'``), or verifies the MRC cache. (if ``mode`` is ``'verify_update'``
or ``'verify_no_update'``).

Please refer to py/tools/mrc_cache.py for more details.

Test Procedure
--------------
This is an automated test without user interaction.

Dependency
----------
``flashrom``

Examples
--------
To run the complete memory training and verification flow described in
py/tools/mrc_cache.py, add this to test list:

.. test_list::

  generic_dram_examples:DRAMTests.MRCCache

"""

import enum
import unittest

from cros.factory.device import device_utils
from cros.factory.test import test_tags
from cros.factory.tools import mrc_cache
from cros.factory.utils.arg_utils import Arg


class TestMode(str, enum.Enum):
  CREATE = 'create'
  VERIFY_UPDATE = 'verify_update'
  VERIFY_NO_UPDATE = 'verify_no_update'


class MrcCacheTestArgs:
  mode: str


class MrcCacheTest(unittest.TestCase):
  related_components = (test_tags.TestCategory.DRAM, )
  ARGS = [
      Arg(
          'mode', str, 'Specify the phase of the test, valid values are:\n'
          '- "create": erase MRC cache and request memory retraining on the'
          ' next boot.\n'
          '- "verify_update": verify the MRC cache update result and request'
          ' memory retraining on next boot.\n'
          '- "verify_no_update": verify the MRC cache is not updated.\n')
  ]
  args: MrcCacheTestArgs

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()

  def runTest(self):
    valid_modes = {mode.value
                   for mode in TestMode}
    if self.args.mode not in valid_modes:
      raise KeyError(
          f"Invalid mode '{self.args.mode}'.  Valid modes are: {valid_modes}")

    mode = TestMode(self.args.mode)
    if mode == TestMode.CREATE:
      mrc_cache.EraseTrainingData(self.dut)
      mrc_cache.SetRecoveryRequest(self.dut)
      mrc_cache.CacheEventLog(self.dut)
    elif mode == TestMode.VERIFY_UPDATE:
      mrc_cache.VerifyTrainingData(self.dut, mrc_cache.Result.Success)
      # Though `VERIFY_UPDATE` requests memory retraining, coreboot won't
      # retrain the memory if the cache is valid.
      mrc_cache.SetRecoveryRequest(self.dut)
      mrc_cache.CacheEventLog(self.dut)
    elif mode == TestMode.VERIFY_NO_UPDATE:
      mrc_cache.VerifyTrainingData(self.dut, mrc_cache.Result.NoUpdate)
      mrc_cache.ClearEventlogCache()
