#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import unittest
from unittest import mock

from cros.factory.hwid.service.appengine.data import cl_upload_config
from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import test_utils
from cros.factory.hwid.service.appengine import vpg_config_manager
from cros.factory.utils import file_utils


_DlmProduct = hwid_api_messages_pb2.DlmProduct

_TEST_VPG_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), 'testdata', 'test_vpg_config.yaml')
_TEST_VPG_TARGETS_PATH = os.path.join(
    os.path.dirname(__file__), 'testdata', 'test_vpg_targets.yaml')
_TEST_VPG_CONFIG_DATA = file_utils.ReadFile(_TEST_VPG_CONFIG_PATH,
                                            encoding=None)
_TEST_VPG_TARGETS_DATA = file_utils.ReadFile(_TEST_VPG_TARGETS_PATH)


class VPGConfigManagerTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._modules = test_utils.FakeModuleCollection()
    self._ndb_connector = self._modules.ndb_connector
    self._mock_cl_upload_manager = mock.create_autospec(
        cl_upload_config.CLUploadManager, instance=True)
    self._vpg_config_manager = vpg_config_manager.VPGConfigManager(
        self._modules.fake_dlm_product_manager, self._mock_cl_upload_manager)

    self.addCleanup(mock.patch.stopall)
    self._mock_get_gerrit_auth_cookie = mock.patch.object(
        vpg_config_manager.git_util, 'GetGerritAuthCookie',
        autospec=True).start()
    self._mock_get_gerrit_credentials = mock.patch.object(
        vpg_config_manager.git_util, 'GetGerritCredentials',
        autospec=True).start()
    self._mock_get_file_content = mock.patch.object(
        vpg_config_manager.git_util, 'GetFileContent', autospec=True).start()
    self._mock_get_current_branch = mock.patch.object(
        vpg_config_manager.git_util, 'GetCurrentBranch', autospec=True).start()

  def tearDown(self):
    super().tearDown()
    self._modules.ClearAll()

  def _CreateDLMProduct(self, **kwargs) -> dlm_product_data.DLMProduct:
    entity = dlm_product_data.DLMProduct()

    with self._ndb_connector.CreateClientContext():
      entity.populate(**kwargs)
      entity.put()
    return entity

  def testUpdate(self):
    self._mock_get_file_content.return_value = _TEST_VPG_CONFIG_DATA
    # None of MODEL3 products are shipped. Generate encrypted payload.
    self._CreateDLMProduct(id=1, board='BOARD1', model='MODEL3',
                           product_status=_DlmProduct.APPROVED, device_id=1)
    # One of MODEL4 products is shipped. Generate normal payload.
    self._CreateDLMProduct(id=2, board='BOARD1', model='MODEL4',
                           product_status=_DlmProduct.APPROVED, device_id=2)
    self._CreateDLMProduct(id=3, board='BOARD1', model='MODEL4',
                           product_status=_DlmProduct.SHIPPED, device_id=2)
    # One of MODEL3 products is not canceled. Generate encrypted payload.
    self._CreateDLMProduct(id=4, board='BOARD2', model='MODEL5',
                           product_status=_DlmProduct.APPROVED, device_id=3)
    self._CreateDLMProduct(id=5, board='BOARD2', model='MODEL5',
                           product_status=_DlmProduct.CANCELED, device_id=3)
    # All MODEL3 products are canceled. No payload is generated.
    self._CreateDLMProduct(id=6, board='BOARD2', model='MODEL6',
                           product_status=_DlmProduct.CANCELED, device_id=4)
    # Overridden by models_force_vp_on. Generate encrypted payload.
    self._CreateDLMProduct(id=7, board='BOARD1', model='MODEL7',
                           product_status=_DlmProduct.SHIPPED, device_id=5)
    # Overridden by models_force_vp_off. No payload is generated.
    self._CreateDLMProduct(id=8, board='BOARD2', model='MODEL8',
                           product_status=_DlmProduct.SHIPPED, device_id=6)

    self._vpg_config_manager.Update(True)

    self._mock_cl_upload_manager.CreateCL.assert_called_with(
        True, 'https://chrome-internal.googlesource.com/'
        'chromeos/platform/factory-private', mock.ANY, mock.ANY,
        [('config/hwid/service/appengine/vpg_targets.yaml', 0o100644,
          _TEST_VPG_TARGETS_DATA)], mock.ANY, mock.ANY,
        'vpg_targets: Update the list of model to generate payloads',
        topic='vpg-targets-automated-sync', auto_submit=True, hashtags=None)


if __name__ == '__main__':
  unittest.main()
