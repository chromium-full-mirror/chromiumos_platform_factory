#!/usr/bin/env python3
# Copyright 2018 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for ingestion."""

import unittest
from unittest import mock

from cros.factory.hwid.service.appengine import app
from cros.factory.hwid.service.appengine import config as config_module
from cros.factory.hwid.service.appengine.data import cl_upload_config
from cros.factory.hwid.service.appengine.data import config_data
from cros.factory.hwid.service.appengine.data import hwid_db_data
from cros.factory.hwid.service.appengine.data import vpg_targets_data
from cros.factory.hwid.service.appengine import hwid_action
from cros.factory.hwid.service.appengine import hwid_action_manager
from cros.factory.hwid.service.appengine import hwid_repo
from cros.factory.hwid.service.appengine import ingestion
from cros.factory.hwid.service.appengine.proto import ingestion_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import test_utils
from cros.factory.probe_info_service.app_engine import protorpc_utils


def _CreateMockConfig(fake_modules: test_utils.FakeModuleCollection):
  mock_config = mock.Mock(
      spec=config_module._Config,  # pylint: disable=protected-access
      wraps=config_module.CONFIG)
  mock_config.hwid_action_manager = fake_modules.fake_hwid_action_manager
  mock_config.vp_cl_upload_manager = mock.create_autospec(
      cl_upload_config.VerificationPayloadCLUploadManager, instance=True)
  mock_config.hsp_cl_upload_manager = mock.create_autospec(
      cl_upload_config.HWIDSelectionPayloadCLUploadManager, instance=True)
  mock_config.rmad_payload_cl_upload_manager = mock.create_autospec(
      cl_upload_config.RMADFeatureEnabledDevicesPayloadCLUploadManager,
      instance=True)
  mock_config.hwid_db_data_manager = mock.create_autospec(
      hwid_db_data.HWIDDBDataManager, instance=True)
  mock_config.decoder_data_manager = fake_modules.fake_decoder_data_manager
  mock_config.hwid_repo_manager = mock.create_autospec(
      hwid_repo.HWIDRepoManager, instance=True)
  mock_config.goldeneye_filesystem = fake_modules.fake_goldeneye_memcache
  mock_config.hwid_data_cachers = [
      mock.create_autospec(hwid_action_manager.IHWIDDataCacher, instance=True),
  ]
  mock_config.dlm_product_manager = fake_modules.fake_dlm_product_manager
  mock_config.vpg_config_cl_upload_manager = mock.create_autospec(
      cl_upload_config.VPGTargetsCLUploadManager, instance=True)
  mock_config.vpg_targets_data_manager = mock.create_autospec(
      vpg_targets_data.VPGTargetsDataManager, instance=True)
  return mock_config


class IngestionRPCProviderTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._modules = test_utils.FakeModuleCollection()
    self._config = _CreateMockConfig(self._modules)
    self._mock_task_enqueuer = mock.Mock()
    self.service = ingestion.IngestionRPCProvider.CreateInstance(
        self._config, config_data.CONFIG,
        task_enqueuer=self._mock_task_enqueuer)

  def tearDown(self):
    super().tearDown()
    self._modules.ClearAll()

  def testRefresh(self):
    hwid_db_metadata_list = [
        hwid_repo.HWIDDBMetadata('KBOARD', 'KBOARD', 2, 'KBOARD'),
        hwid_repo.HWIDDBMetadata('KBOARD.old', 'KBOARD', 2, 'KBOARD.old'),
        hwid_repo.HWIDDBMetadata('SBOARD', 'SBOARD', 3, 'SBOARD'),
        hwid_repo.HWIDDBMetadata('BETTERCBOARD', 'BETTERCBOARD', 3,
                                 'BETTERCBOARD'),
    ]
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.return_value = hwid_db_metadata_list

    request = ingestion_pb2.IngestHwidDbRequest()
    response = self.service.IngestHwidDb(request)

    self.assertEqual(
        response,
        ingestion_pb2.IngestHwidDbResponse(
            msg='Board ingestion tasks dispatched.'))
    data_manager = self._config.hwid_db_data_manager
    data_manager.DeleteMissingProjects.assert_called_once_with(
        hwid_db_metadata_list)
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_called_once()
    self._mock_task_enqueuer.assert_called_once()
    enqueued_req = ingestion_pb2.IngestHwidDbRequest.FromString(
        self._mock_task_enqueuer.call_args.kwargs['body'])
    self.assertEqual(
        list(enqueued_req.limit_boards), ['BETTERCBOARD', 'KBOARD', 'SBOARD'])
    self.assertTrue(enqueued_req.is_board_batch_task)

  def testRefreshWithLimitedModels(self):
    hwid_db_metadata_list = [
        hwid_repo.HWIDDBMetadata('KBOARD', 'KBOARD', 2, 'KBOARD'),
        hwid_repo.HWIDDBMetadata('KBOARD.old', 'KBOARD', 2, 'KBOARD.old'),
        hwid_repo.HWIDDBMetadata('SBOARD', 'SBOARD', 3, 'SBOARD'),
        hwid_repo.HWIDDBMetadata('BETTERCBOARD', 'BETTERCBOARD', 3,
                                 'BETTERCBOARD'),
    ]
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.return_value = hwid_db_metadata_list

    request = ingestion_pb2.IngestHwidDbRequest(
        limit_models=['KBOARD', 'SBOARD', 'COOLBOARD'])
    response = self.service.IngestHwidDb(request)

    self.assertEqual(
        response, ingestion_pb2.IngestHwidDbResponse(msg='Skip for local env'))
    self._config.hwid_db_data_manager.UpdateProjectsByRepo.assert_has_calls([
        mock.call(self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value, [
            hwid_repo.HWIDDBMetadata('KBOARD', 'KBOARD', 2, 'KBOARD'),
            hwid_repo.HWIDDBMetadata('SBOARD', 'SBOARD', 3, 'SBOARD'),
        ])
    ])
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_not_called()

  def testRefreshWithLimitedBoards(self):
    hwid_db_metadata_list = [
        hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1'),
        hwid_repo.HWIDDBMetadata('KPROJ2', 'KBOARD', 3, 'KPROJ2'),
        hwid_repo.HWIDDBMetadata('KPROJ3', 'KBOARD', 3, 'KPROJ3'),
        hwid_repo.HWIDDBMetadata('SPROJ1', 'SBOARD', 3, 'SPROJ1'),
    ]
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.return_value = hwid_db_metadata_list

    request = ingestion_pb2.IngestHwidDbRequest(limit_boards=['KBOARD'])
    response = self.service.IngestHwidDb(request)

    self.assertEqual(
        response, ingestion_pb2.IngestHwidDbResponse(msg='Skip for local env'))
    self._config.hwid_db_data_manager.UpdateProjectsByRepo.assert_has_calls([
        mock.call(self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value, [
            hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1'),
            hwid_repo.HWIDDBMetadata('KPROJ2', 'KBOARD', 3, 'KPROJ2'),
            hwid_repo.HWIDDBMetadata('KPROJ3', 'KBOARD', 3, 'KPROJ3'),
        ])
    ])
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_not_called()

  def testRefreshWithInvalidLimitedBoards(self):
    hwid_db_metadata_list = [
        hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1'),
        hwid_repo.HWIDDBMetadata('KPROJ2', 'KBOARD', 3, 'KPROJ2'),
        hwid_repo.HWIDDBMetadata('KPROJ3', 'KBOARD', 3, 'KPROJ3'),
        hwid_repo.HWIDDBMetadata('SPROJ1', 'SBOARD', 3, 'SPROJ1'),
    ]
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.return_value = hwid_db_metadata_list

    request = ingestion_pb2.IngestHwidDbRequest(limit_boards=['ZBOARD'])
    with self.assertRaises(protorpc_utils.ProtoRPCException) as ex:
      self.service.IngestHwidDb(request)
    self.assertEqual(ex.exception.detail, 'No model meets the limit.')
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_not_called()

  def testRefreshWithLimitedBoardsAndModels(self):
    hwid_db_metadata_list = [
        hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1'),
        hwid_repo.HWIDDBMetadata('KPROJ2', 'KBOARD', 3, 'KPROJ2'),
        hwid_repo.HWIDDBMetadata('KPROJ3', 'KBOARD', 3, 'KPROJ3'),
        hwid_repo.HWIDDBMetadata('SPROJ1', 'SBOARD', 3, 'SPROJ1'),
    ]
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.return_value = hwid_db_metadata_list

    request = ingestion_pb2.IngestHwidDbRequest(
        limit_boards=['KBOARD'], limit_models=['KPROJ1', 'SPROJ1'])
    response = self.service.IngestHwidDb(request)

    self.assertEqual(
        response, ingestion_pb2.IngestHwidDbResponse(msg='Skip for local env'))
    self._config.hwid_db_data_manager.UpdateProjectsByRepo.assert_has_calls([
        mock.call(self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value, [
            hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1'),
        ])
    ])
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_not_called()

  def testRefreshWithInvalidLimitedBoardsAndModels(self):
    hwid_db_metadata_list = [
        hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1'),
        hwid_repo.HWIDDBMetadata('KPROJ2', 'KBOARD', 3, 'KPROJ2'),
        hwid_repo.HWIDDBMetadata('KPROJ3', 'KBOARD', 3, 'KPROJ3'),
        hwid_repo.HWIDDBMetadata('SPROJ1', 'SBOARD', 3, 'SPROJ1'),
    ]
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.return_value = hwid_db_metadata_list

    request = ingestion_pb2.IngestHwidDbRequest(
        limit_boards=['SBOARD'], limit_models=['KPROJ1', 'KPROJ2'])
    with self.assertRaises(protorpc_utils.ProtoRPCException) as ex:
      self.service.IngestHwidDb(request)
    self.assertEqual(ex.exception.detail, 'No model meets the limit.')
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_not_called()

  def testRefreshWithoutBoardsInfo(self):
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.side_effect = hwid_repo.HWIDRepoError

    request = ingestion_pb2.IngestHwidDbRequest()
    with self.assertRaises(protorpc_utils.ProtoRPCException) as ex:
      self.service.IngestHwidDb(request)
    self.assertEqual(ex.exception.detail, 'Got exception from HWID repo.')
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_not_called()

  def testIngestHwidDb_BoardBatchTask(self):
    mock_config_data = mock.create_autospec(config_data.Config(), instance=True)
    mock_config_data.env = 'prod'
    mock_config_data.is_prod_env.return_value = True
    mock_config_data.dryrun_upload = False
    service = ingestion.IngestionRPCProvider.CreateInstance(
        self._config, mock_config_data)

    all_metadata = [
        hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1'),
        hwid_repo.HWIDDBMetadata('SPROJ1', 'SBOARD', 3, 'SPROJ1'),
    ]
    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    live_hwid_repo.ListHWIDDBMetadata.return_value = all_metadata

    with mock.patch.object(service, '_UpdatePayloads',
                           return_value={}) as mock_update:
      request = ingestion_pb2.IngestHwidDbRequest(
          limit_boards=['KBOARD'],
          is_board_batch_task=True,
      )
      response = service.IngestHwidDb(request)

    self.assertEqual(response, ingestion_pb2.IngestHwidDbResponse())
    data_manager = self._config.hwid_db_data_manager
    data_manager.DeleteMissingProjects.assert_not_called()
    data_manager.UpdateProjectsByRepo.assert_called_once_with(
        live_hwid_repo,
        [hwid_repo.HWIDDBMetadata('KPROJ1', 'KBOARD', 3, 'KPROJ1')],
    )
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_not_called()
    self.assertEqual(mock_update.call_count, 3)
    for call in mock_update.call_args_list:
      self.assertFalse(call.args[3])  # force_update is False

  def testCronJobHandler_RoutesToDedicatedQueue(self):
    queue_path = 'projects/p/locations/l/queues/hwid-payload-ingestion'
    mock_client = mock.MagicMock()
    mock_client.queue_path.return_value = queue_path

    with (
        mock.patch.object(app.tasks, 'CloudTasksClient',
                          return_value=mock_client),
        mock.patch.multiple(
            config_data.CONFIG,
            cloud_project='p',
            project_region='l',
            queue_name='ingestion',
            dedicated_queue_name={
                'IngestHwidDb': 'hwid-payload-ingestion'
            },
        ),
    ):
      client = app.hwid_service.test_client()
      resp = client.get(
          '/cron/HwidIngestion.IngestHwidDb',
          headers={
              'X-AppEngine-Cron': 'true'
          },
      )

    self.assertEqual(resp.status_code, 200)
    mock_client.queue_path.assert_called_once_with('p', 'l',
                                                   'hwid-payload-ingestion')
    mock_client.create_task.assert_called_once_with(
        parent=queue_path,
        task={
            'app_engine_http_request': {
                'http_method': 'POST',
                'relative_uri': '/_ah/stubby/HwidIngestion.IngestHwidDb',
            }
        },
    )

  def testIngestHwidDb_DispatchesBatchedBoardTasks(self):
    mock_config_data = mock.create_autospec(config_data.Config(), instance=True)
    mock_config_data.cloud_project = 'p'
    mock_config_data.project_region = 'l'
    mock_config_data.queue_name = 'ingestion'
    mock_config_data.dedicated_queue_name = {
        'IngestHwidDb': 'hwid-payload-ingestion'
    }
    mock_enqueuer = mock.Mock()
    service = ingestion.IngestionRPCProvider.CreateInstance(
        self._config, mock_config_data, task_enqueuer=mock_enqueuer)

    live_hwid_repo = self._config.hwid_repo_manager.GetLiveHWIDRepo.return_value
    all_metadata = [
        hwid_repo.HWIDDBMetadata(f'PROJ_{i}', f'BOARD_{i:02d}', 3, f'PROJ_{i}')
        for i in range(7)
    ]
    live_hwid_repo.ListHWIDDBMetadata.return_value = all_metadata

    resp = service.IngestHwidDb(ingestion_pb2.IngestHwidDbRequest())
    self.assertEqual(
        resp,
        ingestion_pb2.IngestHwidDbResponse(
            msg='Board ingestion tasks dispatched.'))
    data_manager = self._config.hwid_db_data_manager
    data_manager.DeleteMissingProjects.assert_called_once_with(all_metadata)
    self._config.vpg_targets_data_manager.RefreshVpgTargets.assert_called_once()
    self.assertEqual(mock_enqueuer.call_count, 2)

    call_0 = mock_enqueuer.call_args_list[0]
    self.assertEqual(call_0.kwargs['queue_name'], 'hwid-payload-ingestion')
    req_0 = ingestion_pb2.IngestHwidDbRequest.FromString(call_0.kwargs['body'])
    self.assertEqual(
        list(req_0.limit_boards),
        ['BOARD_00', 'BOARD_01', 'BOARD_02', 'BOARD_03', 'BOARD_04'],
    )
    self.assertTrue(req_0.is_board_batch_task)

    call_1 = mock_enqueuer.call_args_list[1]
    self.assertEqual(call_1.kwargs['queue_name'], 'hwid-payload-ingestion')
    req_1 = ingestion_pb2.IngestHwidDbRequest.FromString(call_1.kwargs['body'])
    self.assertEqual(list(req_1.limit_boards), ['BOARD_05', 'BOARD_06'])
    self.assertTrue(req_1.is_board_batch_task)


class SyncNameMappingRPCProviderTest(unittest.TestCase):

  class _FakeHWIDAction(hwid_action.HWIDAction):

    def __init__(self, comps):
      self.comps = comps

    def GetComponents(self, with_classes=None):
      return self.comps

  def setUp(self):
    super().setUp()
    self.fixtures = test_utils.FakeModuleCollection()
    self._config = _CreateMockConfig(self.fixtures)
    self.service = ingestion.SyncNameMappingRPCProvider.CreateInstance(
        self._config)
    self._hwid_data_cacher = self._config.hwid_data_cachers[0]

    self.init_mapping_data = {
        2: "name1",
        4: "name2",
        6: "name3",
    }
    self.update_mapping_data = {
        2: "name4",
        3: "name5",
        4: "name6",
    }

  def tearDown(self):
    super().tearDown()
    self.fixtures.ClearAll()

  @mock.patch(
      'cros.factory.hwid.service.appengine.api_connector.HWIDAPIConnector'
      '.GetAVLNameMapping')
  def testSyncNameMapping(self, get_avl_name_mapping):
    """Perform two round sync and check the consistency."""
    all_comps = {
        'cls1': ['cls1_1', 'cls1_2', 'cls1_3'],
        'cls2': ['cls2_4', 'notcls2_5', 'cls2_6']
    }
    fake_hwid_action = self._FakeHWIDAction(all_comps)
    self.fixtures.ConfigHWID('PROJ1', 3, 'unused_raw_db',
                             hwid_action=fake_hwid_action)

    # Initialize mapping
    get_avl_name_mapping.return_value = self.init_mapping_data
    expected_mapping = {
        'cls1_1': 'cls1_1',
        'cls1_2': 'name1',
        'cls1_3': 'cls1_3',
        'cls2_4': 'name2',
        'notcls2_5': 'notcls2_5',
        'cls2_6': 'name3'
    }

    request = ingestion_pb2.SyncNameMappingRequest()
    response = self.service.SyncNameMapping(request)
    self.assertEqual(response, ingestion_pb2.SyncNameMappingResponse())

    mapping = {}
    for cls, comps in all_comps.items():
      for comp in comps:
        mapping[comp] = self.service.decoder_data_manager.GetAVLName(cls, comp)
    self.assertDictEqual(mapping, expected_mapping)

    # Update mapping
    get_avl_name_mapping.return_value = self.update_mapping_data
    expected_mapping = {
        'cls1_1': 'cls1_1',
        'cls1_2': 'name4',
        'cls1_3': 'name5',
        'cls2_4': 'name6',
        'notcls2_5': 'notcls2_5',
        'cls2_6': 'cls2_6'
    }

    request = ingestion_pb2.SyncNameMappingRequest()
    response = self.service.SyncNameMapping(request)
    self.assertEqual(response, ingestion_pb2.SyncNameMappingResponse())

    mapping = {}
    for cls, comps in all_comps.items():
      for comp in comps:
        mapping[comp] = self.service.decoder_data_manager.GetAVLName(cls, comp)
    self.assertDictEqual(mapping, expected_mapping)

  @mock.patch(
      'cros.factory.hwid.service.appengine.api_connector.HWIDAPIConnector'
      '.GetAVLNameMapping')
  def testSyncNameMapping_HWIDDataCacheInvalidate(self, get_avl_name_mapping):
    # Arrange.
    all_comps1 = {
        'cls1': ['cls1_1', 'cls1_3'],
    }
    all_comps2 = {
        'cls1': ['cls1_2', 'cls1_3']
    }
    fake_hwid_action1 = self._FakeHWIDAction(all_comps1)
    fake_hwid_action2 = self._FakeHWIDAction(all_comps2)
    self.fixtures.ConfigHWID('PROJ1', 3, 'unused_raw_db',
                             hwid_action=fake_hwid_action1)
    self.fixtures.ConfigHWID('PROJ2', 3, 'unused_raw_db',
                             hwid_action=fake_hwid_action2)
    get_avl_name_mapping.return_value = {
        1: 'name1',
        2: 'name2',
    }
    self.service.SyncNameMapping(ingestion_pb2.SyncNameMappingRequest())
    self._hwid_data_cacher.ClearCache.reset_mock()

    # Act: Change AVL name of CID:2.
    get_avl_name_mapping.return_value = {
        1: 'name1',
        2: 'name2-changed',
    }
    self.service.SyncNameMapping(ingestion_pb2.SyncNameMappingRequest())

    # Assert: HWID DB cacher of PROJ2 should trigger a cache invalidation.
    actual_calls = self._hwid_data_cacher.ClearCache.call_args_list
    # Only PROJ2 is affected.
    self.assertCountEqual([mock.call('PROJ2')], actual_calls)

    # Arrange: Reset mock.
    self._hwid_data_cacher.ClearCache.reset_mock()

    # Act: Remove AVL name of CID:1.
    get_avl_name_mapping.return_value = {
        2: 'name2-changed',
    }
    self.service.SyncNameMapping(ingestion_pb2.SyncNameMappingRequest())

    # Assert: HWID DB cacher of PROJ1 should trigger a cache invalidation.
    actual_calls = self._hwid_data_cacher.ClearCache.call_args_list
    # Only PROJ1 is affected.
    self.assertCountEqual([mock.call('PROJ1')], actual_calls)

    # Arrange: Reset mock.
    self._hwid_data_cacher.ClearCache.reset_mock()

    # Act: Add new AVL name of CID:3.
    get_avl_name_mapping.return_value = {
        2: 'name2-changed',
        3: 'name3',
    }
    self.service.SyncNameMapping(ingestion_pb2.SyncNameMappingRequest())

    # Assert: HWID DB cacher of both PROJ1 and PROJ2 should trigger cache
    # invalidations.
    actual_calls = self._hwid_data_cacher.ClearCache.call_args_list
    # Both PROJ1 and PROJ2 are affected.
    self.assertCountEqual(
        [mock.call('PROJ1'), mock.call('PROJ2')], actual_calls)


if __name__ == '__main__':
  unittest.main()
