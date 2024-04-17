#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import hashlib
import os
import os.path
import shutil
import tempfile
import unittest

from cros.factory.hwid.v3 import battery_config_bundle
from cros.factory.hwid.v3 import common
from cros.factory.utils import file_utils
from cros.factory.utils import sys_interface


class PackBatteryConfigContentsTest(unittest.TestCase):

  def testSuccess(self):
    battery_config_contents = '{\n  ...\n}'

    actual = battery_config_bundle.PackBatteryConfigContents(
        battery_config_contents, 'v1.0')

    expected_checksum = hashlib.sha1(
        battery_config_contents.encode('utf-8')).hexdigest()
    expected_lines = [
        f'// checksum: {expected_checksum}',
        '// version: v1.0',
        '',
        battery_config_contents,
    ]
    self.assertEqual(actual, '\n'.join(expected_lines))


class LoadBatteryConfigFileTest(unittest.TestCase):

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
    battery_config_file_name = battery_config_bundle.GetBatteryConfigFileName(
        'the_model')
    os.makedirs(os.path.join(self._bundle_base_dir, battery_config_file_name))

    with self.assertRaises(common.HWIDException):
      battery_config_bundle.UnpackBatteryConfigContents(
          self._bundle_base_dir, 'the_model', sys_interface.SystemInterface())

  def testInvalidChecksumThenRaise(self):
    battery_config_file_name = battery_config_bundle.GetBatteryConfigFileName(
        'the_model')
    original_contents = battery_config_bundle.PackBatteryConfigContents(
        '{\n ...\n}', 'v1.0')
    file_utils.WriteFile(
        os.path.join(self._bundle_base_dir, battery_config_file_name),
        original_contents + '\nsome extra modification')

    with self.assertRaises(common.HWIDException):
      battery_config_bundle.UnpackBatteryConfigContents(
          self._bundle_base_dir, 'the_model', sys_interface.SystemInterface())

  def testSuccess(self):
    battery_config_file_name = battery_config_bundle.GetBatteryConfigFileName(
        'the_model')
    contents = battery_config_bundle.PackBatteryConfigContents(
        '{\n  ...\n}', 'v1.0')
    file_utils.WriteFile(
        os.path.join(self._bundle_base_dir, battery_config_file_name), contents)

    loaded_battery_config = battery_config_bundle.UnpackBatteryConfigContents(
        self._bundle_base_dir, 'the_model', sys_interface.SystemInterface())

    self.assertEqual(loaded_battery_config, '{\n  ...\n}')


if __name__ == '__main__':
  unittest.main()
