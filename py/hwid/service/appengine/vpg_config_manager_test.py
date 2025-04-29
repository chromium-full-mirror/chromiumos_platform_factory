#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import unittest
from unittest import mock

from cros.factory.hwid.service.appengine.data import cl_upload_config
from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine import git_util
from cros.factory.hwid.service.appengine import hwid_action
from cros.factory.hwid.service.appengine import hwid_action_manager as hwid_action_manager_module
from cros.factory.hwid.service.appengine import hwid_repo
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import test_utils
from cros.factory.hwid.service.appengine import vpg_config_manager
from cros.factory.hwid.v3 import database as v3_database
from cros.factory.utils import file_utils


_DeviceType = hwid_api_messages_pb2.DeviceType
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
        cl_upload_config.VPGTargetsCLUploadManager, instance=True)
    self._mock_hwid_action_manager = mock.create_autospec(
        hwid_action_manager_module.HWIDActionManager, instance=True)
    self._vpg_config_manager = vpg_config_manager.VPGConfigManager(
        self._modules.fake_dlm_product_manager, self._mock_cl_upload_manager,
        self._mock_hwid_action_manager, False)

    fake_repo = git_util.MemoryRepo('')
    self._fake_live_hwid_repo = hwid_repo.HWIDRepo(fake_repo, 'test_repo',
                                                   'test_branch', None)

    non_empty_db = mock.create_autospec(v3_database.Database, instance=True)
    empty_db = mock.create_autospec(v3_database.Database, instance=True)
    non_empty_db.GetComponents.return_value = {
        'foo': 'bar'
    }
    empty_db.GetComponents.return_value = {}
    self._mock_non_empty_db_hwid_action = mock.create_autospec(
        hwid_action.HWIDAction, instance=True)
    self._mock_empty_db_hwid_action = mock.create_autospec(
        hwid_action.HWIDAction, instance=True)
    self._mock_non_empty_db_hwid_action.GetDBV3.side_effect = (
        lambda: non_empty_db)
    self._mock_empty_db_hwid_action.GetDBV3.side_effect = lambda: empty_db

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

  @mock.patch(
      'cros.factory.hwid.service.appengine.hwid_repo.HWIDRepoView'
      '.hwid_db_metadata_of_name', new_callable=mock.PropertyMock)
  def testUpdate(self, mock_hwid_db_metadata_of_name):
    self._mock_get_file_content.return_value = _TEST_VPG_CONFIG_DATA
    self._mock_cl_upload_manager.ShouldGenerateContent.return_value = True
    self._mock_cl_upload_manager.ShouldCreateCL.return_value = True
    hwid_db_metadata_of_name = {
        'MODEL3': hwid_repo.HWIDDBMetadata('MODEL3', 'BOARD1', 3, 'MODEL3'),
        'MODEL4': hwid_repo.HWIDDBMetadata('MODEL4', 'BOARD1', 3, 'MODEL4'),
        'MODEL5': hwid_repo.HWIDDBMetadata('MODEL5', 'BOARD2', 3, 'MODEL5'),
        'MODEL6': hwid_repo.HWIDDBMetadata('MODEL6', 'BOARD2', 3, 'MODEL6'),
        'MODEL7': hwid_repo.HWIDDBMetadata('MODEL7', 'BOARD1', 3, 'MODEL7'),
        'MODEL8': hwid_repo.HWIDDBMetadata('MODEL8', 'BOARD2', 3, 'MODEL8'),
        'MODEL9': hwid_repo.HWIDDBMetadata('MODEL9', 'BOARD1', 3, 'MODEL9'),
        'MODEL11': hwid_repo.HWIDDBMetadata('MODEL11', 'BOARD3', 3, 'MODEL11'),
        'MODEL12': hwid_repo.HWIDDBMetadata('MODEL12', 'BOARD1', 3, 'MODEL12'),
        'MODEL13': hwid_repo.HWIDDBMetadata('MODEL13', 'BOARD1', 3, 'MODEL13'),
        'MODEL14': hwid_repo.HWIDDBMetadata('MODEL14', 'BOARD1', 3, 'MODEL14'),
    }
    mock_hwid_db_metadata_of_name.return_value = hwid_db_metadata_of_name

    def _MockGetHWIDAction(model, *args, **kwargs) -> mock.Mock:
      del args, kwargs  # Unused.

      if model == 'MODEL14':
        return self._mock_empty_db_hwid_action
      return self._mock_non_empty_db_hwid_action

    self._mock_hwid_action_manager.GetHWIDAction.side_effect = (
        _MockGetHWIDAction)

    # None of MODEL3 products are shipped. Generate encrypted payload.
    self._CreateDLMProduct(id=1, board='BOARD1', model='MODEL3',
                           product_status=_DlmProduct.APPROVED, device_id=1,
                           device_type=_DeviceType.DEVICE)
    # One of MODEL4 products is shipped. Generate normal payload.
    self._CreateDLMProduct(id=2, board='BOARD1', model='MODEL4',
                           product_status=_DlmProduct.APPROVED, device_id=2,
                           device_type=_DeviceType.DEVICE)
    self._CreateDLMProduct(id=3, board='BOARD1', model='MODEL4',
                           product_status=_DlmProduct.SHIPPED, device_id=2,
                           device_type=_DeviceType.DEVICE)
    # One of MODEL3 products is not canceled. Generate encrypted payload.
    self._CreateDLMProduct(id=4, board='BOARD2', model='MODEL5',
                           product_status=_DlmProduct.APPROVED, device_id=3,
                           device_type=_DeviceType.DEVICE)
    self._CreateDLMProduct(id=5, board='BOARD2', model='MODEL5',
                           product_status=_DlmProduct.CANCELED, device_id=3,
                           device_type=_DeviceType.DEVICE)
    # All MODEL3 products are canceled. No payload is generated.
    self._CreateDLMProduct(id=6, board='BOARD2', model='MODEL6',
                           product_status=_DlmProduct.CANCELED, device_id=4,
                           device_type=_DeviceType.DEVICE)
    # Overridden by models_force_vp_on. Generate encrypted payload.
    self._CreateDLMProduct(id=7, board='BOARD1', model='MODEL7',
                           product_status=_DlmProduct.SHIPPED, device_id=5,
                           device_type=_DeviceType.DEVICE)
    # Overridden by models_force_vp_off. No payload is generated.
    self._CreateDLMProduct(id=8, board='BOARD2', model='MODEL8',
                           product_status=_DlmProduct.SHIPPED, device_id=6,
                           device_type=_DeviceType.DEVICE)
    # Model name is null. No payload is generated.
    self._CreateDLMProduct(id=9, board='BOARD1',
                           product_status=_DlmProduct.APPROVED, device_id=7,
                           device_type=_DeviceType.DEVICE)
    # Status is unknown. No payload is generated.
    self._CreateDLMProduct(id=10, board='BOARD1', model='MODEL9',
                           product_status=_DlmProduct.UNKNOWN, device_id=8,
                           device_type=_DeviceType.DEVICE)
    # MODEL10 has no HWID DB. No payload is generated.
    self._CreateDLMProduct(id=11, board='BOARD1', model='MODEL10',
                           product_status=_DlmProduct.SHIPPED, device_id=9,
                           device_type=_DeviceType.DEVICE)
    # BOARD3 is not in vpg_config. No payload is generated.
    self._CreateDLMProduct(id=12, board='BOARD3', model='MODEL11',
                           product_status=_DlmProduct.SHIPPED, device_id=10,
                           device_type=_DeviceType.DEVICE)
    # MODEL12 is a reference board. No payload is generated.
    self._CreateDLMProduct(id=13, board='BOARD1', model='MODEL12',
                           product_status=_DlmProduct.APPROVED, device_id=11,
                           device_type=_DeviceType.REFERENCE_BOARD)
    # Status is on-hold. No payload is generated.
    self._CreateDLMProduct(id=14, board='BOARD1', model='MODEL13',
                           product_status=_DlmProduct.ON_HOLD, device_id=12,
                           device_type=_DeviceType.DEVICE)
    # The HWID DB is empty. No payload is generated.
    self._CreateDLMProduct(id=14, board='BOARD1', model='MODEL14',
                           product_status=_DlmProduct.DEVELOPMENT, device_id=13,
                           device_type=_DeviceType.DEVICE)

    self._vpg_config_manager.Update(True, self._fake_live_hwid_repo)

    self._mock_cl_upload_manager.CreateCL.assert_called_with(
        True, 'https://chrome-internal.googlesource.com/'
        'chromeos/platform/factory-private', mock.ANY, mock.ANY,
        [('config/hwid/service/appengine/vpg_targets.yaml', 0o100644,
          _TEST_VPG_TARGETS_DATA)], mock.ANY, mock.ANY,
        'vpg_targets: Update the list of model to generate payloads', False,
        topic='vpg-targets-automated-sync', auto_submit=True, hashtags=None)
    self._mock_cl_upload_manager.SetLatestVPGTargetsHash.assert_called_with(
        '36f5209b029355fec53071c7c5063297bdcc6e4c')

  def testUpdate_ShouldNotCreateCL_ShouldNotCreateCL(self):
    self._mock_get_file_content.return_value = _TEST_VPG_CONFIG_DATA
    self._mock_cl_upload_manager.ShouldGenerateContent.return_value = True
    self._mock_cl_upload_manager.ShouldCreateCL.return_value = False

    self._vpg_config_manager.Update(True, self._fake_live_hwid_repo)

    self._mock_cl_upload_manager.CreateCL.assert_not_called()
    self._mock_cl_upload_manager.SetLatestVPGTargetsHash.assert_not_called()

  def testUpdate_ShouldNotGenerateContent_ShouldNotCreateCL(self):
    self._mock_get_file_content.return_value = _TEST_VPG_CONFIG_DATA
    self._mock_cl_upload_manager.ShouldGenerateContent.return_value = False

    self._vpg_config_manager.Update(True, self._fake_live_hwid_repo)

    self._mock_cl_upload_manager.CreateCL.assert_not_called()
    self._mock_cl_upload_manager.SetLatestVPGTargetsHash.assert_not_called()


if __name__ == '__main__':
  unittest.main()
