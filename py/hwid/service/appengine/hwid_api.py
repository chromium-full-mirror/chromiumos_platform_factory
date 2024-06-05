# Copyright 2018 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""HWID Api definition.  Defines all the exposed API methods.

This file is also the place that all the binding is done for various components.
"""

from typing import Collection

from cros.factory.hwid.service.appengine.hwid_api_helpers import bom_and_configless_helper as bc_helper_module
from cros.factory.hwid.service.appengine.hwid_api_helpers import common_helper
from cros.factory.hwid.service.appengine.hwid_api_helpers import decoding_apis
from cros.factory.hwid.service.appengine.hwid_api_helpers import dlm_product_apis
from cros.factory.hwid.service.appengine.hwid_api_helpers import project_info_apis
from cros.factory.hwid.service.appengine.hwid_api_helpers import self_service_helper as ss_helper
from cros.factory.hwid.service.appengine.hwid_api_helpers import sku_helper as sku_helper_module
from cros.factory.hwid.service.appengine import ingestion
from cros.factory.hwid.service.appengine import memcache_adapter


_SESSION_CACHE_NAMESPACE = 'SessionCache'


def GetAllHWIDServiceShards(
    # yapf: disable
    config, config_data) -> Collection[common_helper.HWIDServiceShardBase]:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  goldeneye_memcache_adapter = memcache_adapter.MemcacheAdapter(
      namespace=ingestion.GOLDENEYE_MEMCACHE_NAMESPACE)
  bc_helper = bc_helper_module.BOMAndConfiglessHelper(
      config.decoder_data_manager, config.bom_data_cacher)
  project_info_shard = project_info_apis.ProjectInfoShard(
      config.hwid_action_manager,
      config.hwid_db_data_manager,
      bc_helper,
      config.release_version_manager,
  )
  sku_helper = sku_helper_module.SKUHelper(config.decoder_data_manager)
  get_bom_shard = decoding_apis.GetBOMShard(
      config.hwid_action_manager, bc_helper)
  get_sku_shard = decoding_apis.GetSKUShard(
      config.hwid_action_manager, bc_helper, sku_helper)
  get_dut_label_shard = decoding_apis.GetDUTLabelShard(
      config.decoder_data_manager, goldeneye_memcache_adapter,
      bc_helper, sku_helper, config.hwid_action_manager)

  session_cache_adapter = memcache_adapter.MemcacheAdapter(
      namespace=_SESSION_CACHE_NAMESPACE)

  self_service_shard = ss_helper.SelfServiceShard(
      config.hwid_action_manager, config.hwid_repo_manager,
      config.hwid_db_data_manager, config.avl_converter_manager,
      session_cache_adapter, config.avl_metadata_manager,
      ss_helper.FeatureMatcherBuilderImpl, config.battery_config_fetcher,
      config.vpg_targets_data_manager,
      config_data.cq_count_over_limit_cl_reviewers)

  dlm_product_shard = dlm_product_apis.DLMProductShard(
      config.dlm_product_manager)

  return [
      project_info_shard,
      get_bom_shard,
      get_sku_shard,
      get_dut_label_shard,
      self_service_shard,
      dlm_product_shard,
  ]
