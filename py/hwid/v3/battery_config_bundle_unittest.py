#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import os.path
import shutil
import tempfile
import unittest

from cros.factory.hwid.v3 import battery_config_bundle
from cros.factory.hwid.v3 import common
from cros.factory.utils import file_utils
from cros.factory.utils import sys_interface


class PackAndLoadBatteryConfigFileTest(unittest.TestCase):

  def setUp(self):
    self._bundle_base_dir = tempfile.mkdtemp()

  def tearDown(self):
    if os.path.exists(self._bundle_base_dir):
      shutil.rmtree(self._bundle_base_dir)

  def testNotFoundThenReturnNone(self):
    # Noop arrange, leave the bundle directory empty.

    actual = battery_config_bundle.UnpackBatteryConfigContents(
        self._bundle_base_dir, 'the_model_name',
        sys_interface.SystemInterface())

    self.assertIsNone(actual)

  def testInvalidDataThenRaise(self):
    battery_config_file_name, unused_contents = (
        battery_config_bundle.PackBatteryConfigContents('the_model', '{}',
                                                        'v1.0'))
    os.makedirs(os.path.join(self._bundle_base_dir, battery_config_file_name))

    with self.assertRaises(common.HWIDException):
      battery_config_bundle.UnpackBatteryConfigContents(
          self._bundle_base_dir, 'the_model', sys_interface.SystemInterface())

  def testInvalidChecksumThenRaise(self):
    battery_config_file_name, original_contents = (
        battery_config_bundle.PackBatteryConfigContents('the_model',
                                                        '{\n ...\n}', 'v1.0'))
    file_utils.WriteFile(
        os.path.join(self._bundle_base_dir, battery_config_file_name),
        original_contents + '\nsome extra modification')

    with self.assertRaises(common.HWIDException):
      battery_config_bundle.UnpackBatteryConfigContents(
          self._bundle_base_dir, 'the_model', sys_interface.SystemInterface())

  def testRenameFileThenRaise(self):
    # arrange, bundle two battery configs for 2 models, but swap the file names
    shared_battery_config_contents = '{\n ...\n}'
    shared_version = 'v1.0'
    battery_config_file_name_1, original_contents_1 = (
        battery_config_bundle.PackBatteryConfigContents(
            'the_model_1', shared_battery_config_contents, shared_version))
    battery_config_file_name_2, original_contents_2 = (
        battery_config_bundle.PackBatteryConfigContents(
            'the_model_2', shared_battery_config_contents, shared_version))
    file_utils.WriteFile(
        os.path.join(self._bundle_base_dir, battery_config_file_name_1),
        original_contents_2)
    file_utils.WriteFile(
        os.path.join(self._bundle_base_dir, battery_config_file_name_2),
        original_contents_1)

    with self.assertRaises(common.HWIDException):
      battery_config_bundle.UnpackBatteryConfigContents(
          self._bundle_base_dir, 'the_model_1', sys_interface.SystemInterface())

    with self.assertRaises(common.HWIDException):
      battery_config_bundle.UnpackBatteryConfigContents(
          self._bundle_base_dir, 'the_model_2', sys_interface.SystemInterface())

  def testSuccess(self):
    battery_config_file_name, contents = (
        battery_config_bundle.PackBatteryConfigContents('the_model',
                                                        '{\n  ...\n}', 'v1.0'))
    file_utils.WriteFile(
        os.path.join(self._bundle_base_dir, battery_config_file_name), contents)

    loaded_battery_config = battery_config_bundle.UnpackBatteryConfigContents(
        self._bundle_base_dir, 'the_model', sys_interface.SystemInterface())

    self.assertEqual(loaded_battery_config, '{\n  ...\n}')


if __name__ == '__main__':
  unittest.main()
