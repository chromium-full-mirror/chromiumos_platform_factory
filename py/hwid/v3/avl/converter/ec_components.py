# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID for ec_component_* types."""

from typing import Iterator, Optional, Sequence

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


def _GetECComponentNameField(ec_component_type: str) -> str:
  """Returns the probe info field name of the specific EC component type."""
  return f'{ec_component_type}_component_name'


_RUNTIME_PROBE_COMPONENT_TYPE_FIELD = 'component_type'
_RUNTIME_PROBE_COMPONENT_NAME_FIELD = 'component_name'


class StandaloneECComponentNameConverter(builder.IProbeInfoConverter):
  IDENTIFIER = 'StandaloneECComponentNameConverter'

  def __init__(self, ec_component_type: str):
    """Initializer."""
    self._ec_component_type = ec_component_type

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    """See base class."""
    probe_info_field_name = _GetECComponentNameField(self._ec_component_type)
    return common.JoinFieldConverters([
        common.GetFieldConverter(
            probe_info, probe_info_field_name,
            runtime_probe_matchers.StringEqualMatcher, {
                probe_info_field_name: _RUNTIME_PROBE_COMPONENT_NAME_FIELD
            }),
    ])


_USBC_FEATURES = ('ppc', 'bc12', 'tcpc')


class USBCECComponentNameSuggester(matcher.ISuggester):
  """The suggester that provide USB-C component feature-specific suggestions."""

  def __init__(self):
    """Initializer."""
    self._feature_suggesters = {
        feature_name:
            common.SingleValueAVLAttributeSuggester(
                _GetECComponentNameField(feature_name),
                _RUNTIME_PROBE_COMPONENT_NAME_FIELD)
        for feature_name in _USBC_FEATURES
    }
    self._joined_suggester = common.JoinedAVLAttributeSuggester(
        list(self._feature_suggesters.values()))

  def _IterateAllFieldSuggestions(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Iterator[runtime_probe_matchers.FieldProbeInfoSuggestion]:
    if isinstance(suggestion, (runtime_probe_matchers.AndProbeInfoSuggestion,
                               runtime_probe_matchers.OrProbeInfoSuggestion)):
      for sub_suggestion in suggestion.suggestions:
        yield from self._IterateAllFieldSuggestions(sub_suggestion)
    else:
      yield suggestion

  def _FindGottenComponentType(
      self,
      suggestion: runtime_probe_matchers.ProbeInfoSuggestion) -> Optional[str]:
    found_component_types = set()
    for field_suggestion in self._IterateAllFieldSuggestions(suggestion):
      if field_suggestion.field_name == _RUNTIME_PROBE_COMPONENT_TYPE_FIELD:
        found_component_types.add(field_suggestion.got)
    assert len(found_component_types) <= 1
    if not found_component_types:
      return None
    return found_component_types.pop()  # type: ignore

  def _EraseGottenComponentName(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion):
    for field_suggestion in self._IterateAllFieldSuggestions(suggestion):
      if field_suggestion.field_name == _RUNTIME_PROBE_COMPONENT_NAME_FIELD:
        field_suggestion.got = None

  def BuildSuggestion(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    """See base class."""
    component_type = self._FindGottenComponentType(suggestion)
    feature_suggester = (None if component_type is None else
                         self._feature_suggesters.get(component_type))
    if feature_suggester is None:
      # Mismatched `component_type` cannot be fixed by changing any of the
      # `*_component_name` in the probe-info, hence returning no suggestions.
      return []
    return feature_suggester.BuildSuggestion(suggestion)


class USBCECComponentNameConverter(builder.IProbeInfoConverter):
  IDENTIFIER = 'USBCECComponentNameConverter'

  def _BuildFeatureMatcher(
      self, feature_name: str, probe_info: v3_rule.AVLProbeInfo
  ) -> Optional[runtime_probe_matchers.IMatcher]:
    probe_info_field_name = _GetECComponentNameField(feature_name)
    expected_component_names = probe_info.params.get(probe_info_field_name, [])
    if not expected_component_names:
      return None
    component_name_matchers = [
        runtime_probe_matchers.StringEqualMatcher(
            _RUNTIME_PROBE_COMPONENT_NAME_FIELD, value)
        for value in expected_component_names
    ]
    component_name_matcher = (
        component_name_matchers[0] if len(component_name_matchers) == 1 else
        runtime_probe_matchers.OrMatcher(component_name_matchers))
    return runtime_probe_matchers.AndMatcher([
        runtime_probe_matchers.StringEqualMatcher(
            _RUNTIME_PROBE_COMPONENT_TYPE_FIELD, feature_name),
        component_name_matcher,
    ])

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    """See base class."""
    feature_matchers = []
    for feature_name in _USBC_FEATURES:
      feature_matcher = self._BuildFeatureMatcher(feature_name, probe_info)
      if feature_matcher is not None:
        feature_matchers.append(feature_matcher)

    if not feature_matchers:
      return None

    aggregated_matcher = (
        feature_matchers[0] if len(feature_matchers) == 1 else
        runtime_probe_matchers.OrMatcher(feature_matchers))

    suggester = USBCECComponentNameSuggester()
    return (aggregated_matcher, suggester)


def GetConverterSets() -> Sequence[builder.ConverterSet]:
  converter_sets = []

  for sub_type in ('accel', 'als', 'pdc', 'mux'):
    probe_info_identifier = f'ec_component.ec_component_{sub_type}'
    converter_sets.append(
        builder.ConverterSet(probe_info_identifier,
                             [StandaloneECComponentNameConverter(sub_type)]))

  converter_sets.append(
      builder.ConverterSet('usb_c.ec_components',
                           [USBCECComponentNameConverter()]))

  return converter_sets
