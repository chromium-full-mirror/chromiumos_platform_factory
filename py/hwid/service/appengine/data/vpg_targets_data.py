# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from typing import Any, Mapping

from cros.factory.hwid.service.appengine.data import config_data as config_data_module
from cros.factory.hwid.service.appengine import git_util
from cros.factory.hwid.service.appengine import memcache_adapter
from cros.factory.hwid.service.appengine import verification_payload_generator_config as vpg_config_module
from cros.factory.hwid.v3 import yaml_wrapper as yaml


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

    return (vpg_config_module.VerificationPayloadGeneratorConfig
            .BatchCreateForVpgTargets(raw_content['models_vp_on']))

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

    file_path = f'{setting.prefix}vpg_targets.yaml'
    raw_content = git_util.GetFileContent(setting.review_host, setting.project,
                                          file_path, branch=setting.branch,
                                          auth_cookie=auth_cookie).decode()
    vpg_targets = yaml.safe_load(raw_content)
    self.SetVpgTargets(vpg_targets)
    return (vpg_config_module.VerificationPayloadGeneratorConfig
            .BatchCreateForVpgTargets(vpg_targets['models_vp_on']))
