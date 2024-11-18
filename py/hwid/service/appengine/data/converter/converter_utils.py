# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
from typing import DefaultDict, Iterable, List, Mapping, NamedTuple, Optional

from cros.factory.hwid.service.appengine.data import hwid_db_data
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3.avl import builder as avl_builder
from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import builder
from cros.factory.hwid.v3 import contents_analyzer
from cros.factory.hwid.v3 import database
from cros.factory.hwid.v3 import name_pattern_adapter
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe_info_service.app_engine import stubby_pb2  # pylint: disable=no-name-in-module


_PVAlignmentStatus = contents_analyzer.ProbeValueAlignmentStatus
_HWIDComponentAnalysisResult = contents_analyzer.HWIDComponentAnalysisResult

_SUPPORT_COMPONENT_CLASS = {
    'audio_codec',
    'battery',
    'camera',
    'cpu',
    'display_panel',
    'dram',
    'storage',
    'storage_bridge',
    'tpm',
    'video',
    'wireless',
}


class _AVLKey(NamedTuple):
  cid: int
  qid: int


class _GetAVLKeyAcceptor(
    name_pattern_adapter.NameInfoAcceptor[Optional[_AVLKey]]):
  """An acceptor to provide CID info."""

  def AcceptRegularComp(self, cid: int,
                        qid: Optional[int]) -> Optional[_AVLKey]:
    """See base class."""
    return _AVLKey(cid, 0 if qid is None else qid)

  def AcceptSubcomp(self, cid: int) -> Optional[_AVLKey]:
    """See base class."""
    return _AVLKey(cid, 0)

  def AcceptUntracked(self) -> Optional[_AVLKey]:
    """See base class."""
    return None

  def AcceptLegacy(self, raw_comp_name: str) -> Optional[_AVLKey]:  # pylint: disable=useless-return
    """See base class."""
    del raw_comp_name
    return None


def _StubbyProbeInfoToDBProbeInfo(
    stubby_probe_info: stubby_pb2.ProbeInfo) -> v3_rule.AVLProbeInfo:
  params: DefaultDict[str, List[str]] = collections.defaultdict(list)
  for param in stubby_probe_info.probe_parameters:
    value: str
    if param.HasField("string_value"):
      value = param.string_value
    else:
      value = f'{param.int_value}'
    params[param.name].append(value)
  return v3_rule.AVLProbeInfo(stubby_probe_info.probe_function_name,
                              collections.OrderedDict(params))


class AVLConverter:

  def __init__(self, avl_matcher_builder: avl_builder.Builder,
               probe_info_map: Mapping[_AVLKey, stubby_pb2.ProbeInfo],
               matcher_map: Mapping[_AVLKey, matcher.Matcher], project: str,
               factory_branch: Optional[str] = None,
               suppported_classes: Optional[Iterable[str]] = None):
    self._avl_builder = avl_matcher_builder
    self._probe_info_map = probe_info_map
    self._matcher_map = matcher_map
    self._project = project
    self._factory_branch = factory_branch
    self._supported_classes = set(suppported_classes or
                                  _SUPPORT_COMPONENT_CLASS)
    self._adapter = name_pattern_adapter.NamePatternAdapter()
    self._get_avl_key_acceptor = _GetAVLKeyAcceptor()

  def LinkAVL(
      self,
      hwid_db_content: hwid_db_data.HWIDDBData) -> hwid_db_data.HWIDDBData:
    with builder.DatabaseBuilder.FromDBData(hwid_db_content) as db_builder:
      for comp_cls in db_builder.GetComponentClasses():
        if comp_cls not in self._supported_classes:
          continue
        name_pattern = self._adapter.GetNamePattern(comp_cls)
        for comp_name, comp_info in db_builder.GetComponents(comp_cls).items():
          comp_values = comp_info.values
          if comp_values is None:
            continue

          name_info = name_pattern.Matches(comp_name)
          avl_key = name_info.Provide(self._get_avl_key_acceptor)
          if avl_key is None:
            continue
          probe_info = self._probe_info_map.get(avl_key)
          if probe_info is None:
            continue

          converter_identifier = 'WARNING!!!NO CONVERTER'
          probe_info_matched = False

          avl_matcher = self._matcher_map.get(avl_key)
          if avl_matcher is not None:
            match_result = avl_matcher.Match(comp_values)
            probe_info_matched = match_result.matched
            converter_identifier = match_result.identifier

          probe_info_override = None
          probe_info_override_matched = False
          db_probe_info = _StubbyProbeInfoToDBProbeInfo(probe_info)
          if isinstance(comp_values, v3_rule.AVLProbeValue):
            probe_info_override = comp_values.probe_info_override
          if probe_info_override is not None:
            override_matcher = self._avl_builder.Build(
                probe_info_override, self._project, self._factory_branch,
                avl_key.cid, avl_key.qid, is_probe_info_override=True)
            if override_matcher is not None:
              override_match_result = override_matcher.Match(comp_values)
              probe_info_override_matched = override_match_result.matched
              converter_identifier = override_match_result.identifier

          probe_value_matched = (
              probe_info_matched or probe_info_override_matched)

          avl_probe_value = v3_rule.AVLProbeValue(
              converter_identifier, probe_value_matched, db_probe_info,
              probe_info_matched, probe_info_override,
              probe_info_override_matched, collections.OrderedDict(comp_values))
          db_builder.SetLinkAVLProbeValue(comp_cls, comp_name, avl_probe_value)
    db = db_builder.Build()
    return db.DumpDataWithoutChecksum(suppress_support_status=False,
                                      magic_placeholder_options=None,
                                      internal=True)

  def GetAVLSuggestion(
      self, comp_cls: str, comp_name: str,
      component: Optional[database.ProbedValueType]
  ) -> Optional[hwid_api_messages_pb2.ChangeUnit.AVLSuggestion]:
    if component is None or comp_cls not in self._supported_classes:
      return None
    name_pattern = self._adapter.GetNamePattern(comp_cls)
    name_info = name_pattern.Matches(comp_name)
    avl_key = name_info.Provide(self._get_avl_key_acceptor)
    if avl_key is None:
      return None

    avl_key_suggestions, probe_info_suggestions = [], []
    avl_matcher = self._matcher_map.get(avl_key)
    if avl_matcher is not None:
      suggestions = avl_matcher.GetProbeInfoSuggestion(component)
      if suggestions is not None:
        probe_info_suggestions = [
            stubby_pb2.ProbeParameterSuggestion(hint=s.suggestion, key=s.key,
                                                value=s.value)
            for s in suggestions
        ]

    for avl_key, avl_matcher in self._matcher_map.items():
      if avl_matcher.Match(component).matched:
        avl_key_suggestions.append(
            hwid_api_messages_pb2.AvlInfo(cid=avl_key.cid, qid=avl_key.qid))

    return hwid_api_messages_pb2.ChangeUnit.AVLSuggestion(
        avl_key_suggestions=avl_key_suggestions,
        probe_info_suggestions=probe_info_suggestions)


class ConverterManager:

  def __init__(self, avl_matcher_builder: avl_builder.Builder,
               suppported_classes: Optional[Iterable[str]] = None):
    self._avl_builder = avl_matcher_builder
    self._supported_classes = set(suppported_classes or
                                  _SUPPORT_COMPONENT_CLASS)

  @classmethod
  def FromDefault(cls):
    return cls(default_builder.GetDefaultBuilder())

  def GetAVLConverter(
      self, avl_resource: hwid_api_messages_pb2.HwidDbExternalResource,
      project: str, factory_branch: Optional[str]) -> AVLConverter:

    probe_info_map, avl_matcher_map = {}, {}

    for comp_probe_info in avl_resource.component_probe_infos:
      comp_identity = comp_probe_info.component_identity
      avl_key = _AVLKey(comp_identity.component_id, comp_identity.qual_id)
      probe_info_map[avl_key] = comp_probe_info.probe_info

      db_probe_info = _StubbyProbeInfoToDBProbeInfo(comp_probe_info.probe_info)
      avl_matcher = self._avl_builder.Build(
          db_probe_info, project, factory_branch, avl_key.cid, avl_key.qid,
          is_probe_info_override=False)
      if avl_matcher is not None:
        avl_matcher_map[avl_key] = avl_matcher

    return AVLConverter(self._avl_builder, probe_info_map, avl_matcher_map,
                        project, factory_branch, self._supported_classes)
