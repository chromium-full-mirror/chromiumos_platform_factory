# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import abc
import logging
from typing import Collection, NamedTuple, Optional

from cros.factory.hwid.service.appengine import auth
from cros.factory.hwid.service.appengine.data import config_data
from cros.factory.hwid.service.appengine.data import hwid_db_data
from cros.factory.hwid.service.appengine import feature_matching
from cros.factory.hwid.service.appengine import hwid_action
from cros.factory.hwid.service.appengine import hwid_action_manager as hwid_action_mngr_module
from cros.factory.hwid.service.appengine.hwid_api_helpers import bom_and_configless_helper as bc_helper_module
from cros.factory.hwid.service.appengine.hwid_api_helpers import common_helper
from cros.factory.hwid.service.appengine import hwid_preproc_data
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import release_version_utils
from cros.factory.hwid.v3 import database as db_module
from cros.factory.probe_info_service.app_engine import protorpc_utils
from cros.factory.test.l10n import regions


_Region = hwid_api_messages_pb2.GetRegionListResponse.Region

GET_REGION_LIST_RESPONSE = hwid_api_messages_pb2.GetRegionListResponse(
    region_codes=list(regions.REGIONS.keys()), regions=[
        _Region(region_code=r.region_code, description=r.description)
        for r in regions.REGIONS.values()
    ])

_ImageVersionType = release_version_utils.ImageVersionType
_SoftBrandEligibilityMsg = hwid_api_messages_pb2.SoftBrandEligibility
_ImageVersionTypeMsg = _SoftBrandEligibilityMsg.ImageVersionType


def _ConvertImageVersionTypeToMsg(
    image_version_type: _ImageVersionType,
    # yapf: disable
) -> _ImageVersionTypeMsg.ValueType:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  if image_version_type == _ImageVersionType.LATEST_PUSHED_STABLE:
    return _ImageVersionTypeMsg.LATEST_PUSHED_STABLE
  if image_version_type == _ImageVersionType.LATEST_PUSHED_LTS:
    return _ImageVersionTypeMsg.LATEST_PUSHED_LTS
  raise ValueError(f'Unexpected image version type {image_version_type!r}')


def _ExtractProjectName(hwid: str) -> str:
  project_and_brand, unused_sep, unused_part = hwid.partition(' ')
  project, unused_sep, unused_part = project_and_brand.partition('-')
  return project


def _NormalizeProjectString(string: str) -> Optional[str]:
  """Normalizes a string to account for things like case."""
  return string.strip().upper() if string else None


class _SoftBrandEligibilityChecker(abc.ABC):

  @abc.abstractmethod
  def CheckEligibility(self, hwid: str) -> _SoftBrandEligibilityMsg.Entry:
    """Check soft-brand eligibility of a given HWID string."""


class _ErrorSoftBrandEligibilityChecker(_SoftBrandEligibilityChecker):
  """An implementation of eligibility checker which always generate errors."""

  def __init__(
      self,
      # yapf: disable
      version_type: _ImageVersionTypeMsg.ValueType,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      error: _SoftBrandEligibilityMsg.Error,
  ):
    super().__init__()
    self._version_type = version_type
    self._error = error

  def CheckEligibility(self, hwid: str) -> _SoftBrandEligibilityMsg.Entry:
    """See base class."""
    del hwid
    return _SoftBrandEligibilityMsg.Entry(
        version_type=self._version_type,
        error=self._error,
    )


class _NormalSoftBrandEligibilityChecker(_SoftBrandEligibilityChecker):
  """An implementation of eligibility checker based on given feature_matcher."""

  _SOFT_BRAND_ELIGIBLE_STATUSES = (
      feature_matching.FeatureEnablementType.SOFT_BRANDED_LEGACY,
      feature_matching.FeatureEnablementType.SOFT_BRANDED_WAIVER,
  )

  def __init__(
      self,
      # yapf: disable
      version_type: _ImageVersionTypeMsg.ValueType,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      feature_matcher: feature_matching.HWIDFeatureMatcher,
  ):
    super().__init__()
    self._version_type = version_type
    self._feature_matcher = feature_matcher

  def CheckEligibility(self, hwid: str) -> _SoftBrandEligibilityMsg.Entry:
    """See base class."""
    try:
      match_status = self._feature_matcher.Match(hwid)
    except ValueError:
      return _SoftBrandEligibilityMsg.Entry(
          version_type=self._version_type,
          error=_SoftBrandEligibilityMsg.Error(
              message=f'Invalid HWID string: {hwid!r}.'),
      )
    return _SoftBrandEligibilityMsg.Entry(
        version_type=self._version_type,
        eligible=(match_status.enablement_type
                  in self._SOFT_BRAND_ELIGIBLE_STATUSES),
    )


class _SoftBrandEligibilityCheckerSpec(NamedTuple):
  # yapf: disable
  version_type: _ImageVersionTypeMsg.ValueType  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  image_version: release_version_utils.ImageVersion
  db: db_module.Database
  repo_name: str
  payload_config: config_data.CLSetting


# yapf: disable
class ProjectInfoShard(common_helper.HWIDServiceShardBase):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable

  def __init__(
      self,
      hwid_action_manager: hwid_action_mngr_module.HWIDActionManager,
      hwid_db_data_manager: hwid_db_data.HWIDDBDataManager,
      bc_helper: bc_helper_module.BOMAndConfiglessHelper,
      release_version_manager: release_version_utils.ReleaseVersionManager,
  ):
    self._hwid_action_manager = hwid_action_manager
    self._hwid_db_data_manager = hwid_db_data_manager
    self._bc_helper = bc_helper
    self._release_version_manager = release_version_manager

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def GetProjects(self, request):
    """Return all of the supported projects in sorted order."""
    versions = list(request.versions) if request.versions else None
    metadata_list = self._hwid_db_data_manager.ListHWIDDBMetadata(
        versions=versions)
    projects = [m.project for m in metadata_list]

    response = hwid_api_messages_pb2.ProjectsResponse(
        status=hwid_api_messages_pb2.Status.SUCCESS, projects=sorted(projects))
    return response

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def GetHwids(self, request):
    """Return a filtered list of HWIDs for the given project."""
    project = _NormalizeProjectString(request.project)
    # yapf: disable
    parse_filter_field = lambda value: set(filter(None, value)) or None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    try:
      # yapf: disable
      action = self._hwid_action_manager.GetHWIDAction(project)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      hwids = action.EnumerateHWIDs(
          with_classes=parse_filter_field(request.with_classes),
          without_classes=parse_filter_field(request.without_classes),
          with_components=parse_filter_field(request.with_components),
          without_components=parse_filter_field(request.without_components))
    except (KeyError, ValueError, RuntimeError) as ex:
      return hwid_api_messages_pb2.HwidsResponse(
          status=common_helper.ConvertExceptionToStatus(ex), error=str(ex))

    return hwid_api_messages_pb2.HwidsResponse(
        status=hwid_api_messages_pb2.Status.SUCCESS, hwids=hwids)

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def GetComponentClasses(self, request):
    """Return a list of all component classes for the given project."""
    project = _NormalizeProjectString(request.project)
    try:
      # yapf: disable
      action = self._hwid_action_manager.GetHWIDAction(project)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      classes = action.GetComponentClasses()
    except (KeyError, ValueError, RuntimeError) as ex:
      return hwid_api_messages_pb2.ComponentClassesResponse(
          status=common_helper.ConvertExceptionToStatus(ex), error=str(ex))

    return hwid_api_messages_pb2.ComponentClassesResponse(
        status=hwid_api_messages_pb2.Status.SUCCESS, component_classes=classes)

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def GetComponents(self, request):
    """Return a filtered list of components for the given project."""
    project = _NormalizeProjectString(request.project)
    try:
      # yapf: disable
      action = self._hwid_action_manager.GetHWIDAction(project)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      components = action.GetComponents(
          # yapf: disable
          with_classes=set(filter(None, request.with_classes)) or None)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    except (KeyError, ValueError, RuntimeError) as ex:
      return hwid_api_messages_pb2.ComponentsResponse(
          status=common_helper.ConvertExceptionToStatus(ex), error=str(ex))

    components_list = []
    for cls, comps in components.items():
      # yapf: disable
      for comp, comp_info in comps.items():  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        status = (
            common_helper.SUPPORT_STATUS_CASE_OF_HWID_STRING[comp_info.status])
        # yapf: disable
        avl_info, fields = None, []  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        if request.include_avl:
          avl_info = self._bc_helper.GetAVLInfo(cls, comp)
        if request.include_fields and not comp_info.value_is_none:
          # yapf: disable
          fields = bc_helper_module.GenerateFieldsMessage(comp_info.values)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable

        components_list.append(
            hwid_api_messages_pb2.Component(
                component_class=cls, name=comp, avl_info=avl_info,
                fields=fields, has_avl=bool(avl_info), status=status))

    return hwid_api_messages_pb2.ComponentsResponse(
        status=hwid_api_messages_pb2.Status.SUCCESS, components=components_list)

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def GetRegionList(self, unused_request):
    return GET_REGION_LIST_RESPONSE

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def GetPotentiallySoftBrandedHwidPrefixes(self, unused_request):
    # yapf: disable
    hwid_prefixes = set()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    for project in self._hwid_action_manager.ListProjects():
      action = self._hwid_action_manager.GetHWIDAction(project)
      try:
        matcher = action.GetFeatureMatcher()
      except hwid_action.NotSupportedError:
        logging.info('Project %s does not support feature matcher, skipped',
                     project)
        continue
      hwid_prefixes.update(
          f'{project}-{brand_code}'
          for brand_code in matcher.soft_branded_brand_code_set)
    return hwid_api_messages_pb2.GetPotentiallySoftBrandedHwidPrefixesResponse(
        hwid_prefixes=hwid_prefixes)

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def GetSoftBrandEligibility(self, request):
    hwid_proj_mapping = {
        hwid: _ExtractProjectName(hwid)
        for hwid in request.hwid_strings
    }
    proj_board_mapping = {}
    for proj in set(hwid_proj_mapping.values()):
      try:
        metadata = self._hwid_db_data_manager.GetHWIDDBMetadataOfProject(proj)
      except (hwid_db_data.HWIDDBNotFoundError,
              hwid_db_data.TooManyHWIDDBError):
        logging.exception('Invalid project %s', proj)
      else:
        proj_board_mapping[proj] = metadata.board

    eligibility_checkers = {
        proj: self._CollectEligibilityCheckers(proj, board)
        for proj, board in proj_board_mapping.items()
    }

    resp = hwid_api_messages_pb2.GetSoftBrandEligibilityResponse()
    eligibilities = resp.soft_brand_eligibility
    error_on_checking_eligibility = resp.error_on_checking_eligibility
    for hwid in request.hwid_strings:
      logging.info('Collecting soft-brand eligibility for hwid: %s', hwid)
      proj = hwid_proj_mapping[hwid]
      if proj not in eligibility_checkers:
        error_on_checking_eligibility[hwid].CopyFrom(
            hwid_api_messages_pb2.GetSoftBrandEligibilityResponse.Error(
                message=f'Feature matcher not collected for {proj}.'))
        continue
      for eligibility_checker in eligibility_checkers[proj]:
        eligibilities[hwid].eligibility_entries.append(
            eligibility_checker.CheckEligibility(hwid))
    return resp

  def _CollectEligibilityCheckers(
      self, proj: str, board: str) -> Collection[_SoftBrandEligibilityChecker]:
    """Collects eligibility checkers of certain project.

    Args:
      proj: A string of project.
      board: The corresponding board of the project.

    Returns:
      A sequence of eligibility checkers of the given project.

    Raises:
      protorpc_utils.ProtoRPCException: if unexpected image type is returned
        from ReleaseVersionManager.GetLatestPushedVersions.
    """
    checkers = []
    # Collect feature matcher from TOT.
    try:
      action = self._hwid_action_manager.GetHWIDAction(proj)
    except (
        hwid_action_mngr_module.ProjectNotFoundError,
        hwid_action_mngr_module.ProjectNotSupportedError,
        hwid_action_mngr_module.ProjectUnavailableError,
    ):
      checkers.append(
          _ErrorSoftBrandEligibilityChecker(
              version_type=_ImageVersionTypeMsg.TOT,
              error=_SoftBrandEligibilityMsg.Error(
                  message=f'Unable to get hwid_action of project {proj}.')))
      return checkers
    try:
      feature_matcher = action.GetFeatureMatcher()
    except (hwid_preproc_data.PreprocHWIDError, hwid_action.NotSupportedError):
      logging.exception('Cannot get feature matcher from project %s', proj)
      checkers.append(
          _ErrorSoftBrandEligibilityChecker(
              version_type=_ImageVersionTypeMsg.TOT,
              error=_SoftBrandEligibilityMsg.Error(
                  message=('Cannot get feature matcher of TOT from project '
                           f'{proj}.'))))
    else:
      checkers.append(
          # yapf: disable
          _NormalSoftBrandEligibilityChecker(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
              version_type=_ImageVersionTypeMsg.TOT,
              feature_matcher=feature_matcher,
          ))

    # Collect pushed version by project.
    pushed_versions = self._release_version_manager.GetLatestPushedVersions(
        proj)
    payload_config = config_data.CreateHWIDSelectionPayloadSettings(board=board)
    repo_name = payload_config.project
    try:
      db = action.GetDBV3()
    except hwid_action.NotSupportedError:
      error = f'{proj} is not a HWIDv3 project.'
      for image_version_type, image_version in pushed_versions.items():
        converted_version_type_msg = _ConvertImageVersionTypeToMsg(
            image_version_type)
        checkers.append(
            _ErrorSoftBrandEligibilityChecker(
                version_type=converted_version_type_msg,
                error=_SoftBrandEligibilityMsg.Error(message=error)))
      return checkers

    # Collect feature matcher per Stable/LTS version.
    for image_version_type, image_version in pushed_versions.items():
      try:
        converted_version_type_msg = _ConvertImageVersionTypeToMsg(
            image_version_type)
      except ValueError as ex:
        logging.exception('Cannot convert image version type')
        raise common_helper.ConvertExceptionToProtoRPCException(ex)
      checker = self._CreateEligibilityCheckerBySpec(
          _SoftBrandEligibilityCheckerSpec(
              converted_version_type_msg,
              image_version,
              db,
              repo_name,
              payload_config,
          ))
      if checker is not None:
        # yapf: disable
        checkers.append(checker)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
    return checkers

  def _CreateEligibilityCheckerBySpec(
      self, spec: _SoftBrandEligibilityCheckerSpec
  ) -> Optional[_SoftBrandEligibilityChecker]:
    """Create eligibility checker by given spec.

    Args:
      spec: A _SoftBrandEligibilityCheckerSpec describing the requirements.

    Returns:
      A _SoftBrandEligibilityChecker instance generated by the spec, or None if
        not applicable.
    """
    matcher_builder = feature_matching.HWIDFeatureMatcherBuilder()
    try:
      commit = self._release_version_manager.GetCommitID(
          spec.repo_name, spec.image_version)
    except release_version_utils.CommitUnavailableError:
      logging.exception('GetCommitID fail')
      return _ErrorSoftBrandEligibilityChecker(
          version_type=spec.version_type, error=_SoftBrandEligibilityMsg.Error(
              message=(f'Cannot get commit ID from {spec.image_version} of '
                       f'{spec.repo_name}.')))
    try:
      matcher = (
          matcher_builder.CreateHWIDFeatureMatcherFromPrivateOverlayCommit(
              spec.payload_config, spec.db, commit))
    except ValueError as ex:
      logging.exception('Cannot get feature matcher')
      return _ErrorSoftBrandEligibilityChecker(
          version_type=spec.version_type, error=_SoftBrandEligibilityMsg.Error(
              message=(f'Cannot get feature matcher from {commit} of '
                       f'{spec.repo_name}: {ex}.')))
    return None if matcher is None else _NormalSoftBrandEligibilityChecker(
        version_type=spec.version_type,
        feature_matcher=matcher,
    )
