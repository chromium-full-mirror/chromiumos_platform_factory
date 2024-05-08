# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import fnmatch
import math
import tempfile
import time
from typing import Callable, Optional

from cros.factory.hwid.service.appengine.data import avl_metadata_util
from cros.factory.hwid.service.appengine.data import config_data
from cros.factory.hwid.service.appengine.data.converter import converter_utils
from cros.factory.hwid.service.appengine.data import decoder_data
from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine.data import hwid_db_data
from cros.factory.hwid.service.appengine import hwid_action as hwid_action_module
from cros.factory.hwid.service.appengine import hwid_action_manager
from cros.factory.hwid.service.appengine.hwid_api_helpers import bom_and_configless_helper as bc_helper_module
from cros.factory.hwid.service.appengine import hwid_preproc_data
from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module
from cros.factory.hwid.v3 import filesystem_adapter


class FakeMemcacheAdapter:

  def __init__(self):
    self._data = {}
    self._expiry = {}

  def ClearAll(self):
    self._data.clear()
    self._expiry.clear()

  def Put(self, key, value, expiry: Optional[int] = None):
    self._data[key] = value
    if expiry is not None:
      self._expiry[key] = time.time() + expiry
    else:
      self._expiry.pop(key, None)

  def Get(self, key):
    if self._expiry.get(key, math.inf) < time.time():
      self._data.pop(key, None)
      self._expiry.pop(key, None)
    return self._data.get(key)

  def DelByPattern(self, entry_key_pattern: str):
    for key in fnmatch.filter(self._data, entry_key_pattern):
      self._data.pop(key, None)
      self._expiry.pop(key, None)


class FakeHWIDPreprocData(hwid_preproc_data.HWIDPreprocData):
  CACHE_VERSION = '1'

  def __init__(self, project, raw_db, raw_db_internal, feature_matcher_source,
               bundle_metadata_source):
    super().__init__(project)
    self.raw_db = raw_db
    self.raw_db_internal = raw_db_internal
    self.feature_matcher_source = feature_matcher_source
    self.bundle_metadata_source = bundle_metadata_source


class FakeHWIDInstanceFactory(hwid_action_manager.IInstanceFactory):

  def __init__(self):
    self._hwid_actions = {}
    self._hwid_action_factories = {}

  def CreateHWIDAction(self, hwid_data):
    if not isinstance(hwid_data, FakeHWIDPreprocData):
      raise hwid_action_manager.ProjectUnavailableError
    registered_hwid_action = self._hwid_actions.get(hwid_data.project)
    if registered_hwid_action is not None:
      return registered_hwid_action
    registered_hwid_action_factory = self._hwid_action_factories.get(
        hwid_data.project)
    if registered_hwid_action_factory is not None:
      return registered_hwid_action_factory(hwid_data)
    raise hwid_action_manager.ProjectUnavailableError

  def CreateHWIDPreprocData(self, metadata, raw_db,
                            raw_db_internal: Optional[str] = None,
                            feature_matcher_source: Optional[str] = None,
                            bundle_metadata_source: Optional[str] = None):
    return FakeHWIDPreprocData(metadata.project, raw_db, raw_db_internal,
                               feature_matcher_source, bundle_metadata_source)

  def SetHWIDActionForProject(self, project, hwid_action, hwid_action_factory):
    self._hwid_actions[project] = hwid_action
    self._hwid_action_factories[project] = hwid_action_factory


class FakeModuleCollection:

  def __init__(self):
    self._ndb_connector = ndbc_module.NDBConnector()
    self._tmpdir_for_hwid_db_data = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self._tempfs_for_hwid_db_data = filesystem_adapter.LocalFileSystemAdapter(
        self._tmpdir_for_hwid_db_data.name)
    self._fake_memcache_for_hwid_preproc_data = FakeMemcacheAdapter()
    self._fake_hwid_instance_factory = FakeHWIDInstanceFactory()

    self.fake_decoder_data_manager = decoder_data.DecoderDataManager(
        self._ndb_connector)
    self.fake_hwid_db_data_manager = hwid_db_data.HWIDDBDataManager(
        self._ndb_connector, self._tempfs_for_hwid_db_data)
    self.fake_goldeneye_memcache = FakeMemcacheAdapter()
    self.fake_bom_data_cacher = bc_helper_module.BOMDataCacher(
        # yapf: disable
        FakeMemcacheAdapter())  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.fake_hwid_action_manager = hwid_action_manager.HWIDActionManager(
        self.fake_hwid_db_data_manager,
        # yapf: disable
        self._fake_memcache_for_hwid_preproc_data,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        [self.fake_bom_data_cacher],
        instance_factory=self._fake_hwid_instance_factory,
    )
    self.fake_avl_converter_manager = converter_utils.ConverterManager({})
    self.fake_session_cache_adapter = FakeMemcacheAdapter()
    self.fake_avl_metadata_manager = avl_metadata_util.AVLMetadataManager(
        self._ndb_connector,
        config_data.AVLMetadataSetting.CreateInstance(True, '', '', []))
    self.fake_dlm_product_manager = dlm_product_data.DLMProductManager(
        self._ndb_connector)

  @property
  def ndb_connector(self):
    return self._ndb_connector

  def ClearAll(self):
    self.fake_decoder_data_manager.CleanAllForTest()
    self.fake_hwid_db_data_manager.CleanAllForTest()
    self.fake_avl_metadata_manager.CleanAllForTest()
    self.fake_dlm_product_manager.CleanAllForTest()
    self._tmpdir_for_hwid_db_data.cleanup()

  def ConfigHWID(
      self,
      project: str,
      version: int,
      raw_db: Optional[hwid_db_data.HWIDDBData],
      *,
      board: Optional[str] = None,
      hwid_action: Optional[hwid_action_module.HWIDAction] = None,
      hwid_action_factory: Optional[Callable[
          [FakeHWIDPreprocData], hwid_action_module.HWIDAction]] = None,
      commit_id: str = 'TEST-COMMIT-ID',
      raw_db_internal: Optional[hwid_db_data.HWIDDBData] = None,
      feature_matcher_source: Optional[str] = None,
  ):
    """Specifies the behavior of the fake modules.

    This method lets caller assign the HWIDAction instance to return for the
    given HWID project.  Or the user can also make the project unavailable by
    specify both `hwid_action` and `hwid_action_factory` to `None`.

    Args:
      project: The project to configure.
      version: Specify the HWID version of the specific project.
      raw_db: Specify the HWID DB contents.
      board: The board of the project, defaults to project if set to None.
      hwid_action: Specify the corresponding HWIDAction instance.
      hwid_action_factory: Specify the factory function to create the HWIDAction
          instance.  The given callable function should accept one positional
          argument -- the `FakeHWIDPreprocData` instance.
      raw_db_internal: Specify the internl HWID DB contents.
      feature_matcher_source: The optional feature matcher source.
    """
    if board is None:
      board = project
    self.fake_hwid_db_data_manager.RegisterProjectForTest(
        board, project, str(version), raw_db, commit_id, raw_db_internal,
        feature_matcher_source)
    self._fake_hwid_instance_factory.SetHWIDActionForProject(
        project, hwid_action, hwid_action_factory)

  def AddAVLNameMapping(self, component_id, name):
    with self._ndb_connector.CreateClientContext():
      decoder_data.AVLNameMapping(component_id=component_id, name=name).put()
