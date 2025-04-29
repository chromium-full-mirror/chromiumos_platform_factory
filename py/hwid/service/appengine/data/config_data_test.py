#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for config."""

import os
import unittest


_TEST_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'testdata', 'test_config.yaml')


class ConfigTest(unittest.TestCase):
  """Test for AppEngine config file."""

  def testConfigSwitchingDev(self):
    # Have to patch os.enviorn before importing config module
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'unknown project id'
    from cros.factory.hwid.service.appengine.data import config_data
    self.assertEqual('dev', config_data.Config(_TEST_CONFIG_PATH).env)
    self.assertFalse(config_data.Config(_TEST_CONFIG_PATH).is_prod_env())

  def testConfigSwitchingProd(self):
    # Have to patch os.enviorn before importing config module
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'prod-project-name'
    from cros.factory.hwid.service.appengine.data import config_data
    self.assertEqual('prod', config_data.Config(_TEST_CONFIG_PATH).env)
    self.assertTrue(config_data.Config(_TEST_CONFIG_PATH).is_prod_env())


if __name__ == '__main__':
  unittest.main()
