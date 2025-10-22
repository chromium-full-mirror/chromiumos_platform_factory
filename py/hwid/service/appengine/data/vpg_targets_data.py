# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import logging
from typing import Any, Mapping

from cros.factory.hwid.service.appengine.data import config_data as config_data_module
from cros.factory.hwid.service.appengine import git_util
from cros.factory.hwid.service.appengine import memcache_adapter
from cros.factory.hwid.service.appengine import verification_payload_generator_config as vpg_config_module
from cros.factory.hwid.v3 import yaml_wrapper as yaml


def _UpdateGenericProbeStatementOverrides(
    vpg_targets: Mapping[str, Any], generic_pst_override: Mapping[str, Any]):
  """Updates the generic probe statement override from keys.

  This function modifies `vpg_targets` in-place. It iterates through all models
  and if a model's config contains a 'generic_probe_statement_override_key', it
  uses the value as a key into `generic_pst_override` and puts the result into
  the 'generic_probe_statement_override' field.
  """
  for configs in vpg_targets['models_vp_on'].values():
    for model, config in configs.items():
      if 'generic_probe_statement_override_key' not in config:
        continue

      key = config['generic_probe_statement_override_key']
      if (pst_override := generic_pst_override.get(key)) is None:
        logging.error('%s for %s not found in generic_probe_statement_override',
                      key, model)
        continue

      config['generic_probe_statement_override'] = pst_override


class VPGTargetsDataManager:

  _KEY = 'raw_content'

  def __init__(self, mem_adapter: memcache_adapter.MemcacheAdapter):
    self._mem_adapter = mem_adapter

  def GetVpgTargets(
      self
  ) -> Mapping[str, vpg_config_module.VerificationPayloadGeneratorConfig]:
    """Gets VPG targets from memcache.

    If the VPG targets is not present in memcache, the function will load the
    ToT VPG targets into memcache and return it.

    Returns:
      A dictionary where keys are model names and values are verification
      payload generator config instances.
    """
    raw_content = self._mem_adapter.Get(self._KEY)
    if raw_content is None:
      return self.RefreshVpgTargets()

    return vpg_config_module.VerificationPayloadGeneratorConfig.BatchCreate(
        raw_content['models_vp_on'])

  def SetVpgTargets(self, vpg_targets: Mapping[str, Any]):
    """Sets VPG targets in memcache."""
    self._mem_adapter.Put(self._KEY, vpg_targets)

  def RefreshVpgTargets(
      self
  ) -> Mapping[str, vpg_config_module.VerificationPayloadGeneratorConfig]:
    """Loads ToT VPG targets into memcache and returns it.

    Returns:
      A dictionary where keys are model names and values are verification
      payload generator config instances.
    """
    gerrit_credentials = git_util.GetGerritCredentials()
    auth_cookie = git_util.GetGerritAuthCookie(gerrit_credentials)
    setting = config_data_module.CreateVPGTargetsSettings()

    vpg_targets_file_path = f'{setting.prefix}vpg_targets.yaml'
    vpg_targets_raw_content = git_util.GetFileContent(
        setting.review_host, setting.project, vpg_targets_file_path,
        branch=setting.branch, auth_cookie=auth_cookie).decode()

    generic_pst_override_file_path = (
        f'{setting.prefix}generic_probe_statement_override.json')
    generic_pst_override_raw_content = git_util.GetFileContent(
        setting.review_host, setting.project, generic_pst_override_file_path,
        branch=setting.branch, auth_cookie=auth_cookie).decode()

    vpg_targets = yaml.safe_load(vpg_targets_raw_content)
    generic_pst_override = json.loads(generic_pst_override_raw_content)
    _UpdateGenericProbeStatementOverrides(vpg_targets, generic_pst_override)

    self.SetVpgTargets(vpg_targets)
    return vpg_config_module.VerificationPayloadGeneratorConfig.BatchCreate(
        vpg_targets['models_vp_on'])
