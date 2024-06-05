#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
from typing import Any, Mapping
import unittest
from unittest import mock

from cros.factory.hwid.service.appengine.data import vpg_targets_data
from cros.factory.hwid.service.appengine import test_utils
from cros.factory.hwid.service.appengine import verification_payload_generator_config as vpg_config_module
from cros.factory.hwid.service.appengine import vpg_config_manager
from cros.factory.utils import file_utils


_TEST_VPG_TARGETS_PATH = os.path.join(
    os.path.dirname(__file__), '../testdata', 'test_vpg_targets.yaml')
_TEST_VPG_TARGETS_DATA = file_utils.ReadFile(_TEST_VPG_TARGETS_PATH,
                                             encoding=None)
_TEST_VPG_TARGETS = {
    'MODEL1':
        vpg_config_module.VerificationPayloadGeneratorConfig.Create(
            ignore_error=['stylus']),
    'MODEL2':
        vpg_config_module.VerificationPayloadGeneratorConfig.Create(),
    'MODEL3':
        vpg_config_module.VerificationPayloadGeneratorConfig.Create(
            waived_comp_categories=['dram'], encrypted=True),
    'MODEL4':
        vpg_config_module.VerificationPayloadGeneratorConfig.Create(
            waived_comp_categories=['dram']),
    'MODEL5':
        vpg_config_module.VerificationPayloadGeneratorConfig.Create(
            encrypted=True),
    'MODEL7':
        vpg_config_module.VerificationPayloadGeneratorConfig.Create(
            encrypted=True),
}


class VPGTargetsDataManager(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._modules = test_utils.FakeModuleCollection()
    self._fake_vpg_targets_memcache = self._modules.fake_vpg_targets_memcache
    # yapf: disable
    self._manager = vpg_targets_data.VPGTargetsDataManager(
        self._fake_vpg_targets_memcache)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.addCleanup(mock.patch.stopall)
    self._mock_get_gerrit_auth_cookie = mock.patch.object(
        vpg_config_manager.git_util, 'GetGerritAuthCookie',
        autospec=True).start()
    self._mock_get_gerrit_credentials = mock.patch.object(
        vpg_config_manager.git_util, 'GetGerritCredentials',
        autospec=True).start()
    self._mock_get_file_content = mock.patch.object(
        vpg_config_manager.git_util, 'GetFileContent', autospec=True).start()

  def tearDown(self):
    super().tearDown()
    self._modules.ClearAll()

  def testGetVpgTargets(self):
    vpg_targets: Mapping[str, Any] = {
        'models_vp_on': {
            'BOARD': {
                'MODEL': {}
            }
        }
    }
    self._fake_vpg_targets_memcache.Put('raw_content', vpg_targets)

    res = self._manager.GetVpgTargets()

    self.assertEqual(
        res, {
            'MODEL':
                vpg_config_module.VerificationPayloadGeneratorConfig(
                    ignore_error=[], waived_comp_categories=[], encrypted=False)
        })

  def testGetVpgTargets_NoDataInMemcache_ShouldRefreshVpgTargets(self):
    self._mock_get_file_content.return_value = _TEST_VPG_TARGETS_DATA

    res = self._manager.GetVpgTargets()

    self.assertEqual(res, _TEST_VPG_TARGETS)

  def testSetVpgTargets(self):
    vpg_targets: Mapping[str, Any] = {
        'models_vp_on': {
            'BOARD': {
                'MODEL': {}
            }
        }
    }

    self._manager.SetVpgTargets(vpg_targets)

    res = self._fake_vpg_targets_memcache.Get('raw_content')
    self.assertEqual(res, vpg_targets)

  def testRefreshVpgTargets(self):
    self._mock_get_file_content.return_value = _TEST_VPG_TARGETS_DATA

    res = self._manager.RefreshVpgTargets()

    self.assertEqual(
        self._fake_vpg_targets_memcache.Get('raw_content'), {
            'models_vp_on': {
                'BOARD1': {
                    'MODEL1': {
                        'ignore_error': ['stylus']
                    },
                    'MODEL2': {},
                    'MODEL3': {
                        'encrypted': True,
                        'waived_comp_categories': ['dram']
                    },
                    'MODEL4': {
                        'waived_comp_categories': ['dram']
                    },
                    'MODEL7': {
                        'encrypted': True
                    }
                },
                'BOARD2': {
                    'MODEL5': {
                        'encrypted': True
                    }
                }
            }
        })
    self.assertEqual(res, _TEST_VPG_TARGETS)


if __name__ == '__main__':
  unittest.main()
