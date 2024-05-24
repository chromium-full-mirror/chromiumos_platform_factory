# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Manager for operations on verification payload generator config files."""

import collections
import hashlib
import logging
import os
from typing import Any, Mapping, NamedTuple, Sequence, Set

from cros.factory.hwid.service.appengine.data import cl_upload_config
from cros.factory.hwid.service.appengine.data import config_data as config_data_module
from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine import git_util
from cros.factory.hwid.service.appengine import hwid_repo
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3 import yaml_wrapper as yaml


class VPGConfig:

  def __init__(self, boards_vp_on: Mapping[str, Any],
               models_force_vp_on: Mapping[str, Any],
               models_force_vp_off: Mapping[str, Set]):
    self._boards_vp_on = boards_vp_on
    self._models_force_vp_on = models_force_vp_on
    self._models_force_vp_off = models_force_vp_off

  @property
  def target_boards(self) -> Sequence[str]:
    return list(self._boards_vp_on)

  @property
  def models_force_vp_on(self) -> Mapping[str, Any]:
    return self._models_force_vp_on

  def ShouldSkipProductStatus(self, board: str, model: str) -> bool:
    return (board not in self._boards_vp_on or
            model in self._models_force_vp_on.get(board, {}) or
            model in self._models_force_vp_off.get(board, set()))

  def GetBoardLevelConfig(self, board) -> Mapping[str, Any]:
    return self._boards_vp_on[board]

  @classmethod
  def Create(cls, raw_config: Mapping[str, Any]):
    raw_models_force_vp_off = raw_config.get('models_force_vp_off', {})
    models_force_vp_off = {
        board: set(model_list)
        for board, model_list in raw_models_force_vp_off.items()
    }

    return cls(
        raw_config.get('boards_vp_on', {}),
        raw_config.get('models_force_vp_on', {}), models_force_vp_off)


class VPGTargets(NamedTuple):
  """Holds the generated vpg_targets.yaml content and hash value.

  Attributes:
    content: The generated vpg_targets.yaml content in form of string.
    hash_value: The hash value of content.
  """
  content: str
  hash_value: str

  # yapf: disable
  _VPG_TARGETS_HEADER = ('# This file is updated automatically. Do not edit '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
                         'this file manually.\n\n')

  @classmethod
  def Create(cls, models_vp_on: Mapping[str, Any]):
    vpg_targets_content = cls._VPG_TARGETS_HEADER + yaml.safe_dump(
        models_vp_on, default_flow_style=False)
    content_hash = hashlib.sha1(vpg_targets_content.encode('utf-8')).hexdigest()
    # yapf: disable
    return cls(content=vpg_targets_content, hash_value=content_hash)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable


class VPGConfigGenerationException(Exception):
  """Exception to group similar exceptions for error reporting."""


def _ToSortedDict(target: Mapping[Any, Any]) -> collections.OrderedDict:
  """Returns a sorted copy of `target`."""
  sorted_dict = collections.OrderedDict()
  for key, val in sorted(target.items()):
    if isinstance(val, dict):
      sorted_dict[key] = _ToSortedDict(val)
    elif isinstance(val, list):
      # yapf: disable
      sorted_dict[key] = list(sorted(val))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    else:
      sorted_dict[key] = val
  return sorted_dict


class VPGConfigManager:
  """Manager for updating verification payload generator config file."""

  _INVALID_PRODUCT_STATUS = {
      hwid_api_messages_pb2.DlmProduct.UNKNOWN,
      hwid_api_messages_pb2.DlmProduct.CANCELED,
  }

  def __init__(self, dlm_product_manager: dlm_product_data.DLMProductManager,
               cl_upload_manager: cl_upload_config.VPGTargetsCLUploadManager):
    self._logger = logging.getLogger(self.__class__.__name__)
    self._dlm_product_manager = dlm_product_manager
    self._cl_upload_manager = cl_upload_manager

    self._cl_setting = config_data_module.CreateVPGTargetsSettings()
    self._gerrit_credentials = None
    self._auth_cookie = None

  @property
  def _author(self) -> str:
    # yapf: disable
    service_account_name = self._gerrit_credentials[0]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    return f'chromeoshwid <{service_account_name}>'

  def _RefreshCredential(self):
    self._gerrit_credentials = git_util.GetGerritCredentials()
    self._auth_cookie = git_util.GetGerritAuthCookie(self._gerrit_credentials)

  def _GetVPGConfig(self) -> VPGConfig:
    """Get the instance of manually maintained VPG coinfg file."""
    try:
      file_path = f'{self._cl_setting.prefix}vpg_config.yaml'
      raw_content = git_util.GetFileContent(
          self._cl_setting.review_host, self._cl_setting.project, file_path,
          branch=self._cl_setting.branch, auth_cookie=self._auth_cookie,
          optional=False).decode()
      return VPGConfig.Create(yaml.safe_load(raw_content))
    except (git_util.GitUtilException, ValueError) as ex:
      raise VPGConfigGenerationException(
          f'Failed to load {file_path}: {ex}.') from None

  def _GetProductStatusMapping(
      self, vpg_config: VPGConfig, live_hwid_repo: hwid_repo.HWIDRepo
  ) -> Mapping[str, Mapping[str, Set[int]]]:
    """Get a mapping maps (board, model) to product status set.

    Args:
      vpg_config: VPGConfig instance created from vpg_config.yaml
      live_hwid_repo: See Update().

    Returns:
      A dictionary with (board, model) as key, and the set that collects
      status of all products of the model as value.
    """
    dlm_products = self._dlm_product_manager.GetDLMProductsByBoards(
        vpg_config.target_boards)
    # yapf: disable
    product_status_mapping = collections.defaultdict(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        lambda: collections.defaultdict(set))
    for product in dlm_products:
      if (
          product.model not in live_hwid_repo.hwid_db_metadata_of_name or
          product.product_status in self._INVALID_PRODUCT_STATUS
      ):
        continue

      product_status_mapping[product.board][product.model].add(
          product.product_status)

    return product_status_mapping

  def _CreateCL(self, dryrun: bool, vpg_targets: VPGTargets):
    """Create a CL to update vpg_targets.yaml.

    Args:
      dryrun: True to do everything except actually upload the CL.
      vpg_targets_content: The raw string content of vpg_targets to be
        updated.
    """
    author = self._author
    git_url = f'{self._cl_setting.repo_host}/{self._cl_setting.project}'
    branch = self._cl_setting.branch or git_util.GetCurrentBranch(
        self._cl_setting.review_host, self._cl_setting.project,
        self._auth_cookie)
    git_files = [(os.path.join(self._cl_setting.prefix, 'vpg_targets.yaml'),
                  git_util.NORMAL_FILE_MODE, vpg_targets.content)]
    commit_msg = 'vpg_targets: Update the list of model to generate payloads'
    try:
      self._cl_upload_manager.CreateCL(
          # yapf: disable
          dryrun, git_url, self._auth_cookie, branch, git_files, author, author,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          commit_msg, topic=self._cl_setting.topic, auto_submit=True,
          hashtags=self._cl_setting.hashtags)
    except git_util.GitUtilNoModificationException:
      self._logger.debug('No modification is made, skipped')
    except git_util.GitUtilException as ex:
      self._logger.error('CL is not created: %r', str(ex))
      raise VPGConfigGenerationException('CL is not created') from ex

  def Update(self, dryrun: bool, live_hwid_repo: hwid_repo.HWIDRepo):
    """Update vpg_targets.yaml with product status and vpg_config.yaml.

    This function uses the DLM product data and the manually maintained config
    file, vpg_config.yaml, which includes boards and models that are configured
    to generate verification payloads, to compute the final list of models for
    which the payloads are to be generated. Subsequently, a CL will be uploaded
    to write the model list into an auto-updated config file, vpg_targets.yaml.

    Args:
      dryrun: True to do everything except actually upload the CL.
      live_hwid_repo: A HWIDRepo instance being processed.
    """
    self._logger.info('Start syncing')

    if not self._cl_upload_manager.ShouldGenerateContent(force_generate=False):
      return
    self._RefreshCredential()

    vpg_config = self._GetVPGConfig()
    # yapf: disable
    models_vp_on = collections.defaultdict(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        lambda: collections.defaultdict(dict))
    models_vp_on.update(vpg_config.models_force_vp_on)

    product_status_mapping = self._GetProductStatusMapping(vpg_config,
                                                           live_hwid_repo)
    for board, model_to_status in product_status_mapping.items():
      for model, product_status in model_to_status.items():
        if vpg_config.ShouldSkipProductStatus(board, model):
          continue

        if hwid_api_messages_pb2.DlmProduct.SHIPPED in product_status:
          model_config = {}
        else:
          model_config = {
              'encrypted': True
          }

        board_level_config = vpg_config.GetBoardLevelConfig(board)
        model_config.update(board_level_config)
        models_vp_on[board][model] = model_config

    # Sort the result to avoid flakiness.
    # yapf: disable
    models_vp_on = {  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        'models_vp_on': _ToSortedDict(models_vp_on)
    }
    vpg_targets = VPGTargets.Create(models_vp_on)

    if self._cl_upload_manager.ShouldCreateCL(vpg_targets.hash_value):
      self._CreateCL(dryrun, vpg_targets)
      self._PostUpdate(vpg_targets)

    self._logger.info('Sync successfully')

  def _PostUpdate(self, vpg_targets: VPGTargets):
    self._cl_upload_manager.SetLatestVPGTargetsHash(vpg_targets.hash_value)
