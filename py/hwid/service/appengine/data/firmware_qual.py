# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Firmware qualification related utils."""

import re
from typing import Mapping, Sequence, Set

from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import database


FirmwareQual = hwid_api_messages_pb2.FirmwareQual


def _GetBundleUUIDsByBuildVersion(
    firmware_quals: Sequence[FirmwareQual],
    ro_main_firmware_comps: Mapping[str, database.ComponentInfo]) -> Set[str]:
  bundle_uuids: Set[str] = set()
  build_versions = {q.build_version
                    for q in firmware_quals}
  pattern = re.compile(r'(?:google_\w+\.)?(\d+\.\d+\.\d+)', flags=re.I)
  for comp_info in ro_main_firmware_comps.values():
    if not comp_info.bundle_uuids or comp_info.values is None:
      continue
    version = comp_info.values.get('version')
    if not isinstance(version, str):
      continue
    match = pattern.fullmatch(version)
    if match is not None and match.group(1) in build_versions:
      bundle_uuids.update(comp_info.bundle_uuids)
  return bundle_uuids


def PatchFirmwareQualStatus(
    db: database.Database,
    firmware_quals: Sequence[FirmwareQual]) -> database.Database:
  """Patches support status according to the given firmware quals"""
  new_db = database.WritableDatabase.LoadData(
      db.DumpDataWithoutChecksum(internal=True))
  bundle_uuids = _GetBundleUUIDsByBuildVersion(
      firmware_quals, db.GetComponents(common.FirmwareComps.RO_MAIN_FIRMWARE))
  for comp_cls in common.FirmwareComps:
    for comp_name, comp_info in db.GetComponents(comp_cls).items():
      if comp_info.status in (common.ComponentStatus.deprecated,
                              common.ComponentStatus.supported):
        continue
      if bundle_uuids.intersection(comp_info.bundle_uuids):
        new_db.SetComponentStatus(comp_cls, comp_name,
                                  common.ComponentStatus.supported)
  return new_db
