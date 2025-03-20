# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines available actions for HWIDv3 DB."""

import collections
import logging
from typing import DefaultDict, List, Mapping, Optional, Sequence

from cros.factory.hwid.service.appengine.data import avl_metadata_util
from cros.factory.hwid.service.appengine.data.converter import converter_utils
from cros.factory.hwid.service.appengine.data import hwid_db_data
from cros.factory.hwid.service.appengine.data import vpg_targets_data
from cros.factory.hwid.service.appengine import feature_matching
from cros.factory.hwid.service.appengine import hwid_action
from cros.factory.hwid.service.appengine.hwid_action_helpers import v3_self_service_helper as ss_helper_module
from cros.factory.hwid.service.appengine import hwid_preproc_data
from cros.factory.hwid.service.appengine.proto import bundles_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import runtime_hwid_utils
from cros.factory.hwid.service.appengine import verification_payload_generator_config as vpg_config_module
from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import database
from cros.factory.hwid.v3 import hwid_utils


UNIDENTIFIED_COMPONENT_SUFFIX = 'unidentified'


class HWIDV3Action(hwid_action.HWIDAction):
  HWID_VERSION = 3

  def __init__(self, hwid_v3_preproc_data: hwid_preproc_data.HWIDV3PreprocData):
    self._preproc_data = hwid_v3_preproc_data
    self._ss_helper = (
        ss_helper_module.HWIDV3SelfServiceActionHelper(self._preproc_data))

  def _RuntimeHWIDToComponents(
      self, runtime_hwid_comps: runtime_hwid_utils.RuntimeHWIDComponents
  ) -> Mapping[str, Sequence[str]]:
    runtime_components: DefaultDict[str,
                                    List[str]] = collections.defaultdict(list)
    valid_comp_cls = self._preproc_data.database.GetComponentClasses()
    for comp_cls, comp_list in runtime_hwid_comps.component_positions.items():
      if comp_cls == 'camera':
        comp_cls = self._preproc_data.database.GetCameraComponentClass()

      if comp_cls not in valid_comp_cls:
        # Not a component position.
        continue
      if comp_cls == 'dram':
        # Always uses dram from Factory HWID.
        continue
      if comp_list == ['#']:
        # No component of this category is probed, and the RACC payload does not
        # contain components of this category. Uses components from Factory HWID
        # instead.
        continue
      if comp_list == ['X']:
        # No component of this category is probed, but the RACC payload contains
        # components of this category.
        runtime_components[comp_cls] = []
        continue

      for position in comp_list:
        if position == '?':
          # An unidentified component.
          runtime_components[comp_cls].append(
              f'{comp_cls}_{UNIDENTIFIED_COMPONENT_SUFFIX}')
        elif position.isdigit():
          pos = int(position)
          try:
            comp_name = self._preproc_data.database.GetComponentNameByPosition(
                comp_cls, pos)
            runtime_components[comp_cls].append(comp_name)
          except KeyError as e:
            raise runtime_hwid_utils.InvalidRuntimeHWIDError(
                f'Component position {pos} does not exist in {comp_cls} '
                'components') from e
        else:
          raise runtime_hwid_utils.InvalidRuntimeHWIDError(
              f'Component position contains unknown character: "{position}"')

    return runtime_components

  def GetBOMAndConfigless(
      self, hwid_string: str, verbose: Optional[bool] = False,
      vpg_config: Optional[
          vpg_config_module.VerificationPayloadGeneratorConfig] = None,
      require_vp_info: Optional[bool] = False):
    runtime_comps: Mapping[str, Sequence[str]] = {}
    try:
      hwid_v3_string, runtime_hwid_comps = (
          runtime_hwid_utils.ExtractRuntimeHWID(hwid_string))
      if runtime_hwid_comps:
        runtime_comps = self._RuntimeHWIDToComponents(runtime_hwid_comps)
    except runtime_hwid_utils.InvalidRuntimeHWIDError as e:
      logging.info('Unable to decode invalid Runtime HWID: %s', hwid_string)
      raise hwid_action.InvalidHWIDError(
          f'Invalid Runtime HWID: {hwid_string}') from e

    try:
      hwid, _bom, configless = hwid_utils.DecodeHWID(
          self._preproc_data.database, hwid_v3_string)
    except common.HWIDException as e:
      logging.info('Unable to decode a valid HWID. %s', hwid_string)
      raise hwid_action.InvalidHWIDError(f'HWID not found {hwid_string}', e)

    for comp_cls, comps in runtime_comps.items():
      _bom.SetComponent(comp_cls, comps)

    bom = hwid_action.BOM()

    bom.AddAllComponents(_bom.components, self._preproc_data.database,
                         verbose=verbose, vpg_config=vpg_config,
                         require_vp_info=require_vp_info)
    bom.phase = self._preproc_data.database.GetImageName(hwid.image_id)
    bom.project = hwid.project

    return bom, configless

  def GetDBV3(self):
    return self._preproc_data.database

  def GetDBEditableSection(self, suppress_support_status: bool = False,
                           internal: bool = False) -> hwid_db_data.HWIDDBData:
    return self._ss_helper.GetDBEditableSection(
        suppress_support_status=suppress_support_status, internal=internal)

  def AnalyzeDBEditableSection(
      self,
      draft_db_editable_section: Optional[hwid_db_data.HWIDDBData],
      derive_fingerprint_only: bool,
      require_hwid_db_lines: bool,
      vpg_targets_data_manager: vpg_targets_data.VPGTargetsDataManager,
      internal: bool = False,
      avl_converter: Optional[converter_utils.AVLConverter] = None,
      hwid_bundle_checksum: Optional[str] = None,
      avl_metadata_manager: Optional[
          avl_metadata_util.AVLMetadataManager] = None,
      device_metadata: Optional[hwid_api_messages_pb2.DeviceMetadata] = None,
  ) -> hwid_action.DBEditableSectionAnalysisReport:
    return self._ss_helper.AnalyzeDBEditableSection(
        draft_db_editable_section, derive_fingerprint_only,
        require_hwid_db_lines, vpg_targets_data_manager, internal,
        avl_converter, hwid_bundle_checksum, avl_metadata_manager,
        device_metadata)

  def GetHWIDBundleResourceInfo(self, fingerprint_only=False):
    return self._ss_helper.GetHWIDBundleResourceInfo(fingerprint_only)

  def BundleHWIDDB(self,
                   battery_config_fetcher: hwid_action.IBatteryConfigFetcher):
    return self._ss_helper.BundleHWIDDB(battery_config_fetcher)

  def RemoveHeader(self, hwid_db_contents):
    return self._ss_helper.RemoveHeader(hwid_db_contents)

  def PatchHeader(self, hwid_db_content: hwid_db_data.HWIDDBData):
    return self._ss_helper.PatchHeader(hwid_db_content)

  def GetComponents(
      self, with_classes: Optional[List[str]] = None
  ) -> Mapping[str, Mapping[str, database.ComponentInfo]]:
    comps = {}
    db = self.GetDBV3()
    with_classes = with_classes or db.GetComponentClasses()
    for comp_cls in with_classes:
      if comp_cls == common.REGION_CLS:
        comps[comp_cls] = db.GetActiveRegionComponents()
      else:
        comps[comp_cls] = db.GetComponents(comp_cls)
    return comps

  def ConvertToInternalHWIDDB(self, avl_converter: converter_utils.AVLConverter,
                              hwid_db: database.WritableDatabase) -> None:
    self._ss_helper.ConvertToInternalHWIDDB(avl_converter, hwid_db)

  def GetFeatureEnablementStatus(
      self, hwid_string: str) -> feature_matching.FeatureEnablementStatus:
    """See base class."""
    return self._preproc_data.feature_matcher.Match(hwid_string)

  def GetFeatureMatcher(self) -> feature_matching.HWIDFeatureMatcher:
    """See base class."""
    return self._preproc_data.feature_matcher

  def GenerateBatteryConfigMetadata(
      self, battery_config_fetcher: hwid_action.IBatteryConfigFetcher
  ) -> Optional[bundles_pb2.BundleMetadata.BatteryConfig]:
    """See base class."""
    return self._ss_helper.GenerateBatteryConfigMetadata(battery_config_fetcher)
