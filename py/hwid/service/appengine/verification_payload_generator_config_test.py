# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.hwid.service.appengine import verification_payload_generator_config as vpg_config_module


class VerificationPayloadGeneratorConfigTest(unittest.TestCase):

  def testCreate_WithDefaultValue(self):
    vpg_config = vpg_config_module.VerificationPayloadGeneratorConfig.Create()
    self.assertCountEqual(vpg_config.ignore_error, [])
    self.assertCountEqual(vpg_config.waived_comp_categories, [])
    self.assertFalse(vpg_config.encrypted)

  def testCreate_WithConfig(self):
    config = {
        'waived_comp_categories': ['battery'],
        'ignore_error': ['stylus'],
        'encrypted': True
    }
    vpg_config = vpg_config_module.VerificationPayloadGeneratorConfig.Create(
        # yapf: disable
        **config)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.assertCountEqual(vpg_config.ignore_error, ['stylus'])
    self.assertCountEqual(vpg_config.waived_comp_categories, ['battery'])
    self.assertTrue(vpg_config.encrypted)

  def testBatchCreate(self):
    models_vp_on = {
        'BOARD1': {
            'MODEL1': {
                'waived_comp_categories': ['battery'],
                'ignore_error': ['stylus'],
            },
            'MODEL2': {
                'waived_comp_categories': ['memory'],
            },
        },
        'BOARD2': {
            'MODEL3': {
                'encrypted': True,
            },
        },
    }

    # yapf: disable
    vpg_configs = (
        vpg_config_module.VerificationPayloadGeneratorConfig
        .BatchCreate(models_vp_on))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertEqual(len(vpg_configs), 3)
    self.assertCountEqual(vpg_configs['MODEL1'].waived_comp_categories,
                          ['battery'])
    self.assertCountEqual(vpg_configs['MODEL1'].ignore_error, ['stylus'])
    self.assertFalse(vpg_configs['MODEL1'].encrypted)
    self.assertCountEqual(vpg_configs['MODEL2'].waived_comp_categories,
                          ['memory'])
    self.assertCountEqual(vpg_configs['MODEL2'].ignore_error, [])
    self.assertFalse(vpg_configs['MODEL2'].encrypted)
    self.assertCountEqual(vpg_configs['MODEL3'].waived_comp_categories, [])
    self.assertCountEqual(vpg_configs['MODEL3'].ignore_error, [])
    self.assertTrue(vpg_configs['MODEL3'].encrypted)

if __name__ == '__main__':
  unittest.main()
