# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds data models and their management utils regarding decoding HWIDs."""

import logging
from typing import Collection, Mapping

from google.cloud import ndb

from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module
from cros.factory.hwid.v3 import name_pattern_adapter


class AVLNameMapping(ndb.Model):

  component_id = ndb.IntegerProperty()
  name = ndb.StringProperty()


class PrimaryIdentifier(ndb.Model):
  """Primary identifier for component groups.

  Multiple components could have the same probe values after removing fields
  which are not identifiable like `timing` in dram or `emmc5_fw_ver` in storage.
  This table records those components and chooses one by status (in the order of
  [QUALIFIED, UNQUALIFIED, REJECTED]) then lexicographically smallest name as
  the primary identifier for both GetDutLabels and
  verification_payload_generator to match components by HWID-decoded and probed
  values.
  """
  model = ndb.StringProperty(indexed=True)
  category = ndb.StringProperty(indexed=True)
  comp_name = ndb.StringProperty(indexed=True)
  primary_comp_name = ndb.StringProperty()


class DecoderDataManager:

  def __init__(self, ndb_connector: ndbc_module.NDBConnector):
    self._ndb_connector = ndb_connector
    self._get_cid_acceptor = name_pattern_adapter.GetCIDAcceptor()

  def SyncAVLNameMapping(
      self,
      mapping: Mapping[int, str],
      comp_ids: Collection[int] | None = None,
  ) -> Collection[int]:
    """Sync the set of AVL name mapping to be exactly the mapping provided.

    Args:
      mapping: The {cid: avl_name} dictionary for updating datastore.
      comp_ids: Optional collection of component IDs that were queried. If
          provided, only datastore entries for these component IDs will be
          checked for updates or deletion.

    Returns:
      A collection of CIDs as integers having AVL name mapping
      created, changed, or deleted.
    """
    if comp_ids is not None and not comp_ids:
      return set()

    touched_cids = set()
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      cids_to_create = set(mapping)
      entries_to_put = []
      keys_to_delete = []

      if comp_ids is None:
        existing_entries = list(AVLNameMapping.query())
      else:
        existing_entries = []
        comp_id_list = list(comp_ids)
        for i in range(0, len(comp_id_list), 30):
          chunk = comp_id_list[i:i + 30]
          existing_entries.extend(
              AVLNameMapping.query(AVLNameMapping.component_id.IN(chunk)))

      for entry in existing_entries:
        # Discard the entries indexed by cid.
        if entry.component_id not in mapping:
          keys_to_delete.append(entry.key)
          touched_cids.add(entry.component_id)
        else:
          new_name = mapping[entry.component_id]
          if entry.name != new_name:
            touched_cids.add(entry.component_id)
            entry.name = new_name
            entries_to_put.append(entry)
          cids_to_create.discard(entry.component_id)

      for cid in cids_to_create:
        touched_cids.add(cid)
        name = mapping[cid]
        entries_to_put.append(AVLNameMapping(component_id=cid, name=name))

      if keys_to_delete:
        ndb.delete_multi(keys_to_delete)
      if entries_to_put:
        ndb.put_multi(entries_to_put)
    logging.info('AVL name mapping is synced.')
    return touched_cids

  def DeleteMissingAVLNameMappings(
      self, active_cids: Collection[int]) -> Collection[int]:
    """Deletes AVLNameMapping entries whose component_id is not in active_cids.

    Args:
      active_cids: Collection of all active component IDs across all projects.

    Returns:
      Set of deleted component IDs.
    """
    active_cids_set = set(active_cids)
    deleted_cids = set()
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      keys_to_delete = []
      for entry in AVLNameMapping.query():
        if entry.component_id not in active_cids_set:
          keys_to_delete.append(entry.key)
          deleted_cids.add(entry.component_id)
      if keys_to_delete:
        ndb.delete_multi(keys_to_delete)
    return deleted_cids

  def GetAVLName(self, category, comp_name, fallback=True):
    """Get AVL Name from hourly updated mapping data.

    Args:
      category: Component category.
      comp_name: Component name defined in HWID DB.
      fallback: whether to fallback to comp_name if fail to query AVL name.

    Returns:
      If the name follows the policy and can be queries from datastore, the AVL
      name is returned.  Otherwise, return comp_name if fallback=True or an
      empty string instead.
    """
    np_adapter = name_pattern_adapter.NamePatternAdapter()
    name_pattern = np_adapter.GetNamePattern(category)
    name_info = name_pattern.Matches(comp_name)
    cid = name_info.Provide(self._get_cid_acceptor)
    if cid is None:
      return comp_name if fallback else ''

    with self._ndb_connector.CreateClientContextWithGlobalCache():
      entry = AVLNameMapping.query(AVLNameMapping.component_id == cid).get()
    if entry is None:
      logging.error(
          'mapping not found for category "%s" and component name "%s"',
          category, comp_name)
      return comp_name if fallback else ''
    return entry.name

  def UpdatePrimaryIdentifiers(self, mapping_per_model):
    """Update primary identifiers to datastore.

    This method is for updating the mappings to datastore which will be looked
    up in GetDutLabels API.  To provide consistency, it will clear existing
    mappings per model first.

    Args:
      mapping_per_model: An instance of collections.defaultdict(dict) mapping
          `model` to {(category, component name): target component name}
          mappings.
    """

    with self._ndb_connector.CreateClientContextWithGlobalCache():
      for model, mapping in mapping_per_model.items():
        q = PrimaryIdentifier.query(PrimaryIdentifier.model == model)
        for entry in list(q):
          entry.key.delete()
        for (category, comp_name), primary_comp_name in mapping.items():
          PrimaryIdentifier(model=model, category=category, comp_name=comp_name,
                            primary_comp_name=primary_comp_name).put()

  def GetPrimaryIdentifier(self, model, category, comp_name):
    """Look up existing DUT label mappings from Datastore."""

    with self._ndb_connector.CreateClientContextWithGlobalCache():
      q = PrimaryIdentifier.query(PrimaryIdentifier.model == model,
                                  PrimaryIdentifier.category == category,
                                  PrimaryIdentifier.comp_name == comp_name)
      mapping = q.get()
      return mapping.primary_comp_name if mapping else comp_name

  def CleanAllForTest(self):
    with self._ndb_connector.CreateClientContext():
      for key in AVLNameMapping.query().iter(keys_only=True):
        key.delete()
      for key in PrimaryIdentifier.query().iter(keys_only=True):
        key.delete()
