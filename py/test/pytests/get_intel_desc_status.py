# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Gets the status of Intel SI_DESC and sets the status to device data.

Description
-----------
This pytest gets the status of Intel SI_DESC (lock/unlock) and sets the device
data `factory.intel_desc_locked` accordingly.

Test Procedure
--------------
This is an automatic test that doesn't need any user interaction.

Dependency
----------
- flashrom and ifdtool

Examples
--------
To get the status of Intel SI_DESC, add this in test list::

  {
    "pytest_name": "get_intel_desc_status"
  }
"""

import logging

from cros.factory.gooftool import crosfw
from cros.factory.test import device_data
from cros.factory.test import test_case


class GetIntelDescStatusTest(test_case.TestCase):

  def runTest(self):
    main_fw = crosfw.LoadIntelMainFirmware()
    fw_image = main_fw.GetFirmwareImage()
    if not fw_image.has_section(crosfw.IntelLayout.DESC.value):
      self.FailTask('Cannot find descriptor from the firmware image layout. '
                    'Is this an Intel project?')
    logging.info('Generate locked descriptor...')
    _, is_locked = main_fw.GenerateAndCheckLockedDescriptor()
    logging.info('Is descriptor already locked: %r', is_locked)
    device_data.UpdateDeviceData({device_data.KEY_INTEL_DESC_LOCKED: is_locked})
