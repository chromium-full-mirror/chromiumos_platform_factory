# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Checks and updates touch device firmware.

Description
-----------
This test only works for legacy devices. The name and usage of the
scripts under /opt/google/touch/scripts/* were changed.

The current touch firmware in factory is updated at boot time by
`boot-update-firmware.conf`_. If the fw version on factory branch test image and
FSI image are different then the fw is updated again on the first boot out of
factory.

.. _boot-update-firmware.conf: https://chromium.googlesource.com/chromiumos/\
platform2/+/main/init/upstart/boot-update-firmware.conf

Test Procedure
--------------
The test runs automatically.

Dependency
----------
- /opt/google/touch/scripts/*

Examples
--------
To check touchpad hover with default parameters without calibration, add this
in test list:

.. test_list::

  generic_touchscreen_examples:TouchscreenTests.TouchDeviceFWUpdate

"""

import glob
import logging
import os
import unittest

from cros.factory.test import session
from cros.factory.test import test_tags
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import file_utils
from cros.factory.utils import process_utils


FIRMWARE_UPDATER = '/opt/google/touch/scripts/chromeos-touch-firmware-update.sh'
CONFIG_UPDATER = '/opt/google/touch/scripts/chromeos-touch-config-update.sh'


class UpdateTouchDeviceFWTest(unittest.TestCase):
  related_components = (
      test_tags.TestCategory.EMR_IC,
      test_tags.TestCategory.TOUCHCONTROLLER,
      test_tags.TestCategory.TRACKPAD,
      test_tags.TestCategory.USI_CONTROLLER,
  )
  ARGS = [
      Arg('device_name', str, 'Name of the touch device as in'
          '/sys/bus/i2c/devices/\\*/name)'),
      Arg('fw_name', str, 'Expected firmware file name (in /lib/firmware)'),
      Arg('fw_version', str, 'Expected firmware version'),
  ]

  def run_updater_command(self, command):
    session.console.info('Running: %s', command)
    updater = process_utils.Spawn(command,
                                  log=True, read_stdout=True, shell=True)
    updater.wait()
    if updater.returncode != 0:
      # yapf: disable
      error_message = f'Touch device {self.args.device_name} update failed.'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      logging.error(error_message)
      logging.error('  stdout: %s', updater.stdout_data)
      logging.error('  stderr: %s', updater.stderr_data)
      raise ValueError(error_message)

  def runTest(self):
    # Find the appropriate device sysfs file.
    devices = [
        x for x in glob.glob('/sys/bus/i2c/devices/*/name')
        # yapf: disable
        if file_utils.ReadFile(x).strip() == self.args.device_name  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
    ]
    self.assertEqual(1, len(devices),
                     f'Expected to find one device but found {devices}')
    device_path = os.path.dirname(devices[0])

    # yapf: disable
    expected_ver = getattr(self.args, 'fw_version')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    actual_ver = file_utils.ReadFile(os.path.join(device_path,
                                                  'fw_version')).strip()
    if expected_ver != actual_ver:
      logging.info('Updating firmware from version %s to version %s',
                   actual_ver, expected_ver)
      firmware_updater_cmd = (
          # yapf: disable
          f'{FIRMWARE_UPDATER} -f -d {self.args.device_name} -n '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          f'{self.args.fw_name}')
      self.run_updater_command(firmware_updater_cmd)

    # Always force-update the device configuration
    logging.info('Updating device configuration.')
    # yapf: disable
    config_updater_cmd = f'{CONFIG_UPDATER} -f -d {self.args.device_name}'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.run_updater_command(config_updater_cmd)
