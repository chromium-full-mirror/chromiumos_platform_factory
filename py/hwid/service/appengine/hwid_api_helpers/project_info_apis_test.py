#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for cros.hwid.service.appengine.hwid_api"""

import functools
import pathlib
import textwrap
from typing import Callable, Optional
import unittest
from unittest import mock

from packaging import version as version_module

from cros.factory.hwid.service.appengine.data import config_data
from cros.factory.hwid.service.appengine import feature_matching
from cros.factory.hwid.service.appengine import hwid_action
from cros.factory.hwid.service.appengine.hwid_api_helpers import bom_and_configless_helper as bc_helper_module
from cros.factory.hwid.service.appengine.hwid_api_helpers import project_info_apis
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import release_version_utils
from cros.factory.hwid.service.appengine import test_utils
from cros.factory.hwid.v3 import database
from cros.factory.test.l10n import regions


AVLInfoMsg = hwid_api_messages_pb2.AvlInfo
ComponentMsg = hwid_api_messages_pb2.Component
FieldMsg = hwid_api_messages_pb2.Field
StatusMsg = hwid_api_messages_pb2.Status
SupportStatus = hwid_api_messages_pb2.ComponentSupportStatus.Case
Region = hwid_api_messages_pb2.GetRegionListResponse.Region

_SoftBrandEligibilityMsg = hwid_api_messages_pb2.SoftBrandEligibility
_ImageVersionTypeMsg = _SoftBrandEligibilityMsg.ImageVersionType
_ImageVersionType = release_version_utils.ImageVersionType
_ImageVersion = release_version_utils.ImageVersion


def _MockMatchForSoftBrandWrapper(
    func: Callable[..., bool],
) -> Callable[[str], feature_matching.FeatureEnablementStatus]:

  @functools.wraps(func)
  def Wrapper(*args, **kwargs):
    ret = func(*args, **kwargs)
    if ret:
      return feature_matching.FeatureEnablementStatus(
          hw_compliance_version=1, enablement_type=(
              feature_matching.FeatureEnablementType.SOFT_BRANDED_LEGACY))
    return feature_matching.FeatureEnablementStatus(
        hw_compliance_version=1,
        enablement_type=feature_matching.FeatureEnablementType.DISABLED,
    )

  return Wrapper


class ProtoRPCServiceTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._modules = test_utils.FakeModuleCollection()
    self._bc_helper = mock.Mock(
        spec=bc_helper_module.BOMAndConfiglessHelper,
        wraps=bc_helper_module.BOMAndConfiglessHelper(
            self._modules.fake_decoder_data_manager,
            self._modules.fake_bom_data_cacher,
            self._modules.fake_vpg_targets_data_manager))
    self._release_version_manager = mock.create_autospec(
        release_version_utils.ReleaseVersionManager, instance=True)
    self.service = project_info_apis.ProjectInfoShard(
        self._modules.fake_hwid_action_manager,
        self._modules.fake_hwid_db_data_manager,
        self._bc_helper,
        self._release_version_manager,
    )

  def tearDown(self):
    super().tearDown()
    self._modules.ClearAll()

  def testGetProjects(self):
    self._modules.ConfigHWID('ALPHA', 2, 'db1')
    self._modules.ConfigHWID('BRAVO', 3, 'db2')
    self._modules.ConfigHWID('CHARLIE', 3, 'db3')

    req = hwid_api_messages_pb2.ProjectsRequest()
    msg = self.service.GetProjects(req)

    self.assertEqual(
        hwid_api_messages_pb2.ProjectsResponse(
            status=StatusMsg.SUCCESS,
            projects=sorted(['ALPHA', 'BRAVO', 'CHARLIE'])), msg)

  def testGetHwids_ProjectNotFound(self):
    # There's no project in the backend datastore by default.

    req = hwid_api_messages_pb2.HwidsRequest(project='no_such_project')
    msg = self.service.GetHwids(req)

    self.assertEqual(msg.status, StatusMsg.NOT_FOUND)

  def testGetHwids_InternalError(self):
    self._modules.ConfigHWID('FOO', 3, 'db data')

    req = hwid_api_messages_pb2.HwidsRequest(project='foo')
    msg = self.service.GetHwids(req)

    self.assertEqual(msg.status, StatusMsg.SERVER_ERROR)

  def testGetHwids_BadRequestError(self):
    hwid_action_inst = hwid_action.HWIDAction()
    with mock.patch.object(hwid_action_inst, '_EnumerateHWIDs') as method:
      method.return_value = ['alfa', 'bravo', 'charlie']
      self._modules.ConfigHWID('FOO', 3, 'db data',
                               hwid_action=hwid_action_inst)

      req = hwid_api_messages_pb2.HwidsRequest(project='foo',
                                               with_classes=['foo', 'bar'],
                                               without_classes=['bar', 'baz'])
      msg = self.service.GetHwids(req)

    self.assertEqual(msg.status, StatusMsg.BAD_REQUEST)

  def testGetHwids_Success(self):
    hwid_action_inst = hwid_action.HWIDAction()
    with mock.patch.object(hwid_action_inst, '_EnumerateHWIDs') as method:
      method.return_value = ['alfa', 'bravo', 'charlie']
      self._modules.ConfigHWID('FOO', 3, 'db data',
                               hwid_action=hwid_action_inst)

      req = hwid_api_messages_pb2.HwidsRequest(project='foo')
      msg = self.service.GetHwids(req)

    self.assertEqual(
        hwid_api_messages_pb2.HwidsResponse(
            status=StatusMsg.SUCCESS, hwids=['alfa', 'bravo', 'charlie']), msg)

  def testGetComponentClasses_ProjectNotFoundError(self):
    # There's no project in the backend datastore by default.

    req = hwid_api_messages_pb2.ComponentClassesRequest(project='nosuchproject')
    msg = self.service.GetComponentClasses(req)

    self.assertEqual(msg.status, StatusMsg.NOT_FOUND)

  def testGetComponentClasses_ProjectUnavailableError(self):
    self._modules.ConfigHWID('FOO', 3, 'db data')

    req = hwid_api_messages_pb2.ComponentClassesRequest(project='foo')
    msg = self.service.GetComponentClasses(req)

    self.assertEqual(msg.status, StatusMsg.SERVER_ERROR)

  def testGetComponentClasses_Success(self):
    fake_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    fake_hwid_action.GetComponentClasses.return_value = ['dram', 'storage']
    self._modules.ConfigHWID('FOO', 3, 'db data', hwid_action=fake_hwid_action)

    req = hwid_api_messages_pb2.ComponentClassesRequest(project='foo')
    msg = self.service.GetComponentClasses(req)

    self.assertEqual(msg.status, StatusMsg.SUCCESS)
    self.assertCountEqual(list(msg.component_classes), ['dram', 'storage'])

  def testGetComponents_ProjectNotFoundError(self):
    # There's no project in the backend datastore by default.

    req = hwid_api_messages_pb2.ComponentsRequest(project='nosuchproject')
    msg = self.service.GetComponents(req)

    self.assertEqual(msg.status, StatusMsg.NOT_FOUND)

  def testGetComponents_ProjectUnavailableError(self):
    self._modules.ConfigHWID('FOO', 3, 'db data')

    req = hwid_api_messages_pb2.ComponentsRequest(project='foo')
    msg = self.service.GetComponents(req)

    self.assertEqual(msg.status, StatusMsg.SERVER_ERROR)

  def testGetComponents_SuccessWithAllComponentClasses(self):
    sampled_components = {
        'dram': {
            'dram1': database.ComponentInfo({
                'key': 'value'
            }, 'supported')
        },
        'storage': {
            'storage1': database.ComponentInfo({
                'key': 'value'
            }, 'supported')
        },
    }

    def FakeGetComponents(with_classes=None):
      return {
          k: v
          for k, v in sampled_components.items()
          if with_classes is None or k in with_classes
      }

    fake_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    fake_hwid_action.GetComponents.side_effect = FakeGetComponents
    self._modules.ConfigHWID('FOO', 3, 'db data', hwid_action=fake_hwid_action)

    req = hwid_api_messages_pb2.ComponentsRequest(project='foo')
    msg = self.service.GetComponents(req)

    self.assertEqual(msg.status, StatusMsg.SUCCESS)
    self.assertCountEqual(msg.components, [
        ComponentMsg(component_class='dram', name='dram1',
                     status=SupportStatus.SUPPORTED),
        ComponentMsg(component_class='storage', name='storage1',
                     status=SupportStatus.SUPPORTED),
    ])

  def testGetComponents_SuccessWithLimitedComponentClasses(self):
    sampled_components = {
        'dram': {
            'dram1': database.ComponentInfo({'key': 'value'}, 'supported')
        },
        'storage': {
            'storage1': database.ComponentInfo({'key': 'value'}, 'supported')
        },
    }

    def FakeGetComponents(with_classes=None):
      return {
          k: v
          for k, v in sampled_components.items()
          if with_classes is None or k in with_classes
      }

    fake_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    fake_hwid_action.GetComponents.side_effect = FakeGetComponents
    self._modules.ConfigHWID('FOO', 3, 'db data', hwid_action=fake_hwid_action)

    req = hwid_api_messages_pb2.ComponentsRequest(project='foo',
                                                  with_classes=['dram'])
    msg = self.service.GetComponents(req)

    self.assertEqual(msg.status, StatusMsg.SUCCESS)
    self.assertCountEqual(msg.components, [
        ComponentMsg(component_class='dram', name='dram1',
                     status=SupportStatus.SUPPORTED),
    ])

  def testGetComponents_SuccessWithIncludeAVL(self):
    sampled_components = {
        'dram': {
            'dram_1_2': database.ComponentInfo({'key': 'value'}, 'supported')
        },
        'storage': {
            'storage1': database.ComponentInfo({'key': 'value'}, 'supported')
        },
    }

    def FakeGetComponents(with_classes=None):
      return {
          k: v
          for k, v in sampled_components.items()
          if with_classes is None or k in with_classes
      }

    fake_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    fake_hwid_action.GetComponents.side_effect = FakeGetComponents
    self._modules.ConfigHWID('FOO', 3, 'db data', hwid_action=fake_hwid_action)

    req = hwid_api_messages_pb2.ComponentsRequest(project='foo',
                                                  include_avl=True)
    msg = self.service.GetComponents(req)

    self.assertEqual(msg.status, StatusMsg.SUCCESS)
    self.assertCountEqual(msg.components, [
        ComponentMsg(
            component_class='dram', name='dram_1_2', avl_info=AVLInfoMsg(
                cid=1, qid=2), has_avl=True, status=SupportStatus.SUPPORTED),
        ComponentMsg(component_class='storage', name='storage1',
                     status=SupportStatus.SUPPORTED),
    ])

  def testGetComponents_SuccessWithIncludeFields(self):
    sampled_components = {
        'dram': {
            'dram_1_2': database.ComponentInfo({'key': 'value'}, 'supported')
        },
        'storage': {
            'storage1': database.ComponentInfo({'key': 'value'}, 'supported')
        },
    }

    def FakeGetComponents(with_classes=None):
      return {
          k: v
          for k, v in sampled_components.items()
          if with_classes is None or k in with_classes
      }

    fake_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    fake_hwid_action.GetComponents.side_effect = FakeGetComponents
    self._modules.ConfigHWID('FOO', 3, 'db data', hwid_action=fake_hwid_action)

    req = hwid_api_messages_pb2.ComponentsRequest(project='foo',
                                                  include_fields=True)
    msg = self.service.GetComponents(req)

    self.assertEqual(msg.status, StatusMsg.SUCCESS)
    self.assertCountEqual(msg.components, [
        ComponentMsg(component_class='dram', name='dram_1_2', fields=[
            FieldMsg(name='key', value='value')
        ], status=SupportStatus.SUPPORTED),
        ComponentMsg(component_class='storage', name='storage1', fields=[
            FieldMsg(name='key', value='value')
        ], status=SupportStatus.SUPPORTED),
    ])

  def testGetRegionList_Success(self):
    resp = self.service.GetRegionList(
        hwid_api_messages_pb2.GetRegionListRequest())
    expected_regions = [
        Region(region_code=r.region_code, description=r.description)
        for r in regions.REGIONS.values()
    ]
    self.assertCountEqual(resp.regions, expected_regions)

  def testGetPotentiallySoftBrandedHwidPrefixes_Success(self):

    def CreateMockHWIDAction(
        hwid_data: test_utils.FakeHWIDPreprocData,
    ) -> hwid_action.HWIDAction:
      action = mock.create_autospec(hwid_action.HWIDAction, instance=True)
      matcher_builder = feature_matching.HWIDFeatureMatcherBuilder()
      action.GetFeatureMatcher.return_value = (
          matcher_builder.CreateHWIDFeatureMatcher(
              db=mock.create_autospec(database.Database, instance=True),
              source=hwid_data.feature_matcher_source,
          ))
      return action

    self._modules.ConfigHWID(
        'PROJ1', 3, 'unused raw HWID DB contents',
        hwid_action_factory=CreateMockHWIDAction,
        feature_matcher_source=textwrap.dedent('''\
            feature_version: 1
            hwid_requirement_candidates {
              description: "unused-desc"
              encoding_requirements {
                description: "unused"
                bit_positions: 0
                required_values: "0"
              }
            }
            brand_code_permissions {
              key: "AAAA"
              value {
                allow_disabled_units: true
                allow_hard_branded_units: true
              }
            }
            brand_code_permissions {
              key: "BBBB"
              value {
                allow_disabled_units: true
                allow_soft_branded_legacy_units: true
              }
            }
            brand_code_permissions {
              key: "CCCC"
              value {
                allow_disabled_units: true
                allow_soft_branded_waiver_units: true
              }
            }
        '''))
    self._modules.ConfigHWID(
        'PROJ2', 3, 'unused raw HWID DB contents',
        hwid_action_factory=CreateMockHWIDAction,
        feature_matcher_source=textwrap.dedent('''\
            feature_version: 1
            hwid_requirement_candidates {
              description: "unused-desc"
              encoding_requirements {
                description: "unused"
                bit_positions: 0
                required_values: "0"
              }
            }
            brand_code_permissions {
              key: "DDDD"
              value {
                allow_disabled_units: true
                allow_hard_branded_units: true
              }
            }
            brand_code_permissions {
              key: "EEEE"
              value {
                allow_disabled_units: true
                allow_soft_branded_legacy_units: true
              }
            }
            brand_code_permissions {
              key: "FFFF"
              value {
                allow_disabled_units: true
                allow_soft_branded_waiver_units: true
              }
            }
        '''))

    msg = self.service.GetPotentiallySoftBrandedHwidPrefixes(
        hwid_api_messages_pb2.GetPotentiallySoftBrandedHwidPrefixesRequest())

    self.assertCountEqual(
        ['PROJ1-BBBB', 'PROJ1-CCCC', 'PROJ2-EEEE', 'PROJ2-FFFF'],
        msg.hwid_prefixes)

  def testGetPotentiallySoftBrandedHwidPrefixes_UnsupportedDBVersion(self):
    mock_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    mock_hwid_action.GetFeatureMatcher.side_effect = (
        hwid_action.NotSupportedError)
    self._modules.ConfigHWID('PROJ1', 2, 'unused raw HWID DB contents',
                             hwid_action=mock_hwid_action)

    with self.assertLogs() as cm:
      msg = self.service.GetPotentiallySoftBrandedHwidPrefixes(
          hwid_api_messages_pb2.GetPotentiallySoftBrandedHwidPrefixesRequest())

    self.assertIn(
        'INFO:root:Project PROJ1 does not support feature matcher, skipped',
        cm.output)
    self.assertEqual(
        hwid_api_messages_pb2.GetPotentiallySoftBrandedHwidPrefixesResponse(),
        msg)

  def testGetSoftBrandEligibility_NoMetadata(self):
    resp = self.service.GetSoftBrandEligibility(
        hwid_api_messages_pb2.GetSoftBrandEligibilityRequest(
            hwid_strings=['PROJ1-AAAA A2A-B2B-C2C']))

    self.assertEqual(
        hwid_api_messages_pb2.GetSoftBrandEligibilityResponse(
            error_on_checking_eligibility={
                'PROJ1-AAAA A2A-B2B-C2C':
                    hwid_api_messages_pb2.GetSoftBrandEligibilityResponse.Error(
                        message='Feature matcher not collected for PROJ1.')
            }), resp)

  def testGetSoftBrandEligibility_TOTOnly(self):

    @_MockMatchForSoftBrandWrapper
    def MockMatch(hwid_string: str) -> bool:
      return hwid_string in ('PROJ1-AAAA A2A-B2B-C2C', 'PROJ1-AAAA A3A-B3B-C3C')

    mock_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    mock_feature_matcher = mock.create_autospec(
        feature_matching.HWIDFeatureMatcher, instance=True)
    mock_feature_matcher.Match.side_effect = MockMatch
    mock_hwid_action.GetFeatureMatcher.return_value = mock_feature_matcher
    self._modules.ConfigHWID('PROJ1', 3, 'unused db data', board='BOARD1',
                             hwid_action=mock_hwid_action)
    self._release_version_manager.GetLatestPushedVersions.return_value = {}

    msg = self.service.GetSoftBrandEligibility(
        hwid_api_messages_pb2.GetSoftBrandEligibilityRequest(hwid_strings=[
            'PROJ1-AAAA A2A-B2B-C2C',
            'PROJ1-AAAA A3A-B3B-C3C',
            'PROJ1-AAAA A4A-B4B-C4C',
        ]))

    self.assertEqual(
        hwid_api_messages_pb2.GetSoftBrandEligibilityResponse(
            soft_brand_eligibility={
                'PROJ1-AAAA A2A-B2B-C2C':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            eligible=True,
                        )
                    ]),
                'PROJ1-AAAA A3A-B3B-C3C':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            eligible=True,
                        )
                    ]),
                'PROJ1-AAAA A4A-B4B-C4C':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            eligible=False,
                        )
                    ]),
            }), msg)

  @mock.patch.object(project_info_apis.feature_matching,
                     'HWIDFeatureMatcherBuilder')
  def testGetSoftBrandEligibility_PushedReleaseOnly(self,
                                                    mock_matcher_builder_cls):

    def MockGetCommitID(
        repo_name: str,
        image_version: release_version_utils.ImageVersion) -> str:
      # Customize a commit ID based on repo_name and image_version.
      return f'commit-{pathlib.Path(repo_name).name}-{image_version.version}'

    @_MockMatchForSoftBrandWrapper
    def MockMatch(commit: str, hwid_string: str) -> bool:
      # If the hwid_string contains the commit, regard it as soft-branded.
      return commit in hwid_string

    def MockCreateMatcherFromCommit(
        unused_payload_config: config_data.CLSetting,
        unused_db: database.Database,
        commit: str,
    ) -> Optional[feature_matching.HWIDFeatureMatcher]:
      mock_feature_matcher = mock.create_autospec(
          feature_matching.HWIDFeatureMatcher, instance=True)
      mock_feature_matcher.Match.side_effect = functools.partial(
          MockMatch, commit)
      return mock_feature_matcher

    mock_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    # Disable TOT matcher result.
    mock_hwid_action.GetFeatureMatcher.side_effect = (
        hwid_action.NotSupportedError)
    self._modules.ConfigHWID('PROJ1', 3, 'unused db data', board='BOARD1',
                             hwid_action=mock_hwid_action)
    self._release_version_manager.GetLatestPushedVersions.return_value = {
        _ImageVersionType.LATEST_PUSHED_STABLE:
            _ImageVersion(
                milestone=100,
                version=version_module.Version('12345.67.8'),
            ),
        _ImageVersionType.LATEST_PUSHED_LTS:
            _ImageVersion(
                milestone=90,
                version=version_module.Version('9999.99.9'),
            ),
    }
    self._release_version_manager.GetCommitID.side_effect = MockGetCommitID
    builder = mock_matcher_builder_cls.return_value
    builder.CreateHWIDFeatureMatcherFromPrivateOverlayCommit.side_effect = (
        MockCreateMatcherFromCommit)

    msg = self.service.GetSoftBrandEligibility(
        hwid_api_messages_pb2.GetSoftBrandEligibilityRequest(hwid_strings=[
            'PROJ1-AAAA commit-overlay-board1-private-12345.67.8',
            'PROJ1-AAAA commit-overlay-board1-private-9999.99.9',
            'PROJ1-AAAA this does not match any',
        ]))

    self.assertEqual(
        hwid_api_messages_pb2.GetSoftBrandEligibilityResponse(
            soft_brand_eligibility={
                'PROJ1-AAAA commit-overlay-board1-private-12345.67.8':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Cannot get feature matcher of TOT '
                                         'from project PROJ1.')),
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=(
                                _ImageVersionTypeMsg.LATEST_PUSHED_STABLE),
                            eligible=True,
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.LATEST_PUSHED_LTS,
                            eligible=False,
                        ),
                    ]),
                'PROJ1-AAAA commit-overlay-board1-private-9999.99.9':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Cannot get feature matcher of TOT '
                                         'from project PROJ1.')),
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=(
                                _ImageVersionTypeMsg.LATEST_PUSHED_STABLE),
                            eligible=False,
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.LATEST_PUSHED_LTS,
                            eligible=True,
                        ),
                    ]),
                'PROJ1-AAAA this does not match any':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Cannot get feature matcher of TOT '
                                         'from project PROJ1.')),
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=(
                                _ImageVersionTypeMsg.LATEST_PUSHED_STABLE),
                            eligible=False,
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.LATEST_PUSHED_LTS,
                            eligible=False,
                        ),
                    ]),
            }), msg)

  def testGetSoftBrandEligibility_RaisedAtGetHWIDAction(self):
    self._modules.ConfigHWID('PROJ1', 3, 'unused db data', board='BOARD1')

    msg = self.service.GetSoftBrandEligibility(
        hwid_api_messages_pb2.GetSoftBrandEligibilityRequest(hwid_strings=[
            'PROJ1-AAAA A2A-B2B-C2C',
        ]))

    self.assertEqual(
        hwid_api_messages_pb2.GetSoftBrandEligibilityResponse(
            soft_brand_eligibility={
                'PROJ1-AAAA A2A-B2B-C2C':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Unable to get hwid_action of project '
                                         'PROJ1.')),
                        )
                    ]),
            }), msg)

  def testGetSoftBrandEligibility_NotHWIDv3(self):
    mock_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    mock_hwid_action.GetFeatureMatcher.side_effect = (
        hwid_action.NotSupportedError)
    mock_hwid_action.GetDBV3.side_effect = hwid_action.NotSupportedError
    self._modules.ConfigHWID('PROJ1', 2, 'unused db data', board='BOARD1',
                             hwid_action=mock_hwid_action)
    self._release_version_manager.GetLatestPushedVersions.return_value = {
        _ImageVersionType.LATEST_PUSHED_STABLE:
            _ImageVersion(
                milestone=100,
                version=version_module.Version('12345.67.8'),
            ),
        _ImageVersionType.LATEST_PUSHED_LTS:
            _ImageVersion(
                milestone=90,
                version=version_module.Version('9999.99.9'),
            ),
    }

    msg = self.service.GetSoftBrandEligibility(
        hwid_api_messages_pb2.GetSoftBrandEligibilityRequest(hwid_strings=[
            'PROJ1-AAAA A2A-B2B-C2C',
        ]))

    self.assertEqual(
        hwid_api_messages_pb2.GetSoftBrandEligibilityResponse(
            soft_brand_eligibility={
                'PROJ1-AAAA A2A-B2B-C2C':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Cannot get feature matcher of TOT '
                                         'from project PROJ1.')),
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=(
                                _ImageVersionTypeMsg.LATEST_PUSHED_STABLE),
                            error=_SoftBrandEligibilityMsg.Error(
                                message='PROJ1 is not a HWIDv3 project.'),
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.LATEST_PUSHED_LTS,
                            error=_SoftBrandEligibilityMsg.Error(
                                message='PROJ1 is not a HWIDv3 project.'),
                        ),
                    ]),
            }), msg)

  def testGetSoftBrandEligibility_GetCommitIDFail(self):
    mock_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    # Disable TOT matcher result.
    mock_hwid_action.GetFeatureMatcher.side_effect = (
        hwid_action.NotSupportedError)
    self._modules.ConfigHWID('PROJ1', 3, 'unused db data', board='BOARD1',
                             hwid_action=mock_hwid_action)
    self._release_version_manager.GetLatestPushedVersions.return_value = {
        _ImageVersionType.LATEST_PUSHED_STABLE:
            _ImageVersion(
                milestone=100,
                version=version_module.Version('12345.67.8'),
            ),
    }
    self._release_version_manager.GetCommitID.side_effect = (
        release_version_utils.CommitUnavailableError)

    msg = self.service.GetSoftBrandEligibility(
        hwid_api_messages_pb2.GetSoftBrandEligibilityRequest(hwid_strings=[
            'PROJ1-AAAA A2A-B2B-C2C',
        ]))

    self.assertEqual(
        hwid_api_messages_pb2.GetSoftBrandEligibilityResponse(
            soft_brand_eligibility={
                'PROJ1-AAAA A2A-B2B-C2C':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Cannot get feature matcher of TOT '
                                         'from project PROJ1.')),
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=(
                                _ImageVersionTypeMsg.LATEST_PUSHED_STABLE),
                            error=_SoftBrandEligibilityMsg.Error(
                                message=(
                                    'Cannot get commit ID from ImageVersion('
                                    'milestone=100, version=<Version('
                                    "'12345.67.8')>) of chromeos/overlays/"
                                    'overlay-board1-private.'),
                            ),
                        ),
                    ]),
            }), msg)

  @mock.patch.object(project_info_apis.feature_matching,
                     'HWIDFeatureMatcherBuilder')
  def testGetSoftBrandEligibility_CannotGetFeatureMatcherFromPayload(
      self, mock_matcher_builder_cls):
    mock_hwid_action = mock.create_autospec(hwid_action.HWIDAction,
                                            instance=True)
    # Disable TOT matcher result.
    mock_hwid_action.GetFeatureMatcher.side_effect = (
        hwid_action.NotSupportedError)
    self._modules.ConfigHWID('PROJ1', 3, 'unused db data', board='BOARD1',
                             hwid_action=mock_hwid_action)
    self._release_version_manager.GetLatestPushedVersions.return_value = {
        _ImageVersionType.LATEST_PUSHED_STABLE:
            _ImageVersion(
                milestone=100,
                version=version_module.Version('12345.67.8'),
            ),
    }
    self._release_version_manager.GetCommitID.return_value = 'commit-id'
    builder = mock_matcher_builder_cls.return_value
    builder.CreateHWIDFeatureMatcherFromPrivateOverlayCommit.side_effect = (
        ValueError('err msg'))

    msg = self.service.GetSoftBrandEligibility(
        hwid_api_messages_pb2.GetSoftBrandEligibilityRequest(hwid_strings=[
            'PROJ1-AAAA A2A-B2B-C2C',
        ]))

    self.assertEqual(
        hwid_api_messages_pb2.GetSoftBrandEligibilityResponse(
            soft_brand_eligibility={
                'PROJ1-AAAA A2A-B2B-C2C':
                    _SoftBrandEligibilityMsg(eligibility_entries=[
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=_ImageVersionTypeMsg.TOT,
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Cannot get feature matcher of TOT '
                                         'from project PROJ1.')),
                        ),
                        _SoftBrandEligibilityMsg.Entry(
                            version_type=(
                                _ImageVersionTypeMsg.LATEST_PUSHED_STABLE),
                            error=_SoftBrandEligibilityMsg.Error(
                                message=('Cannot get feature matcher from '
                                         'commit-id of chromeos/overlays/'
                                         'overlay-board1-private: err msg.')),
                        ),
                    ]),
            }), msg)


if __name__ == '__main__':
  unittest.main()
