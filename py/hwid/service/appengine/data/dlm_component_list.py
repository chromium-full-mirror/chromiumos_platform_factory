# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""DLM device component list related utils."""

import itertools
from typing import Mapping, NamedTuple, Optional, Sequence, Tuple

from cros.factory.hwid.service.appengine.hwid_api_helpers import common_helper
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import database
from cros.factory.hwid.v3 import name_pattern_adapter as npa


DeviceComponentList = Sequence[hwid_api_messages_pb2.DlmComponentInfo]
Status = common.ComponentStatus


class AvlInfo(NamedTuple):
  cid: int
  qid: Optional[int]
  is_subcomp: bool

  @classmethod
  def FromMessage(cls, msg: hwid_api_messages_pb2.AvlInfo):
    return cls(msg.cid, msg.qid or None, msg.is_subcomp)


AVL_INFO_ACCEPTOR = common_helper.GenerateAVLInfoAcceptor()

_STATUS_TRANSITION: Mapping[Tuple[str, bool], str] = {
    (Status.unqualified, True): Status.supported,
    (Status.unqualified, False): Status.unsupported,
    (Status.supported, False): Status.deprecated,
}


def PatchComponentList(db: database.WritableDatabase,
                       comp_list: DeviceComponentList) -> None:
  all_classes = set(
      itertools.chain.from_iterable(
          comp.related_hwid_classes for comp in comp_list))
  comps_by_avl_info = {
      AvlInfo.FromMessage(comp.avl_info): comp
      for comp in comp_list
  }
  for comp_cls in all_classes:
    name_pattern = npa.NamePattern(comp_cls)
    for comp_name, comp_info in db.GetComponents(comp_cls, False).items():
      avl_info = name_pattern.Matches(comp_name).Provide(AVL_INFO_ACCEPTOR)
      if avl_info is None:
        continue
      comp = comps_by_avl_info.get(AvlInfo.FromMessage(avl_info))
      if comp is None or not comp.has_claim_for_pvt_or_mp_use:
        continue
      update_status = _STATUS_TRANSITION.get(
          (comp_info.status, comp.claim_for_pvt_or_mp_use))
      if update_status is not None:
        db.SetComponentStatus(comp_cls, comp_name, update_status)
