# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from typing import Iterable, List, Mapping, Optional, Sequence, Type

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class NopSuggester(matcher.ISuggester):
  """A placeholder which does nothing.

  TODO(chungsheng): Implement some real suggesters when we need them.
  """

  def BuildSuggestion(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    return []


class AVLAttributeSuggesterBase(matcher.ISuggester):

  def __init__(self, key: str, runtime_probe_key: str):
    self._key = key
    self._runtime_probe_key = runtime_probe_key

  def _FormatSuggestion(
      self, suggestion: runtime_probe_matchers.FieldProbeInfoSuggestion
  ) -> Optional[matcher.ProbeInfoSuggestion]:
    return matcher.ProbeInfoSuggestion(
        self._key, str(suggestion.got), f'Expected AVL attribute {self._key!r}='
        f'{str(suggestion.expected)!r}, but got '
        f'{str(suggestion.got)!r}.')

  def _HandleOrSuggestion(
      self, suggestion: runtime_probe_matchers.OrProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    raise NotImplementedError

  def BuildSuggestion(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    suggestions = []
    if isinstance(suggestion, runtime_probe_matchers.FieldProbeInfoSuggestion):
      if (suggestion.field_name == self._runtime_probe_key and
          suggestion.got != suggestion.expected):
        formated_suggestion = self._FormatSuggestion(suggestion)
        if formated_suggestion is not None:
          suggestions.append(formated_suggestion)
    elif isinstance(suggestion, runtime_probe_matchers.AndProbeInfoSuggestion):
      for s in suggestion.suggestions:
        suggestions.extend(self.BuildSuggestion(s))
    elif isinstance(suggestion, runtime_probe_matchers.OrProbeInfoSuggestion):
      suggestions.extend(self._HandleOrSuggestion(suggestion))
    return suggestions


class SingleValueAVLAttributeSuggester(AVLAttributeSuggesterBase):
  """Suggester for single value AVL attributes"""

  def _HandleOrSuggestion(
      self, suggestion: runtime_probe_matchers.OrProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    return self.BuildSuggestion(suggestion.suggestions[0])


class MultiValueAVLAttributeSuggester(AVLAttributeSuggesterBase):
  """Suggester for multi value AVL attributes"""

  def _HandleOrSuggestion(
      self, suggestion: runtime_probe_matchers.OrProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    filtered_suggestions: Sequence[
        runtime_probe_matchers.FieldProbeInfoSuggestion] = [
            s for s in suggestion.suggestions if
            (isinstance(s, runtime_probe_matchers.FieldProbeInfoSuggestion) and
             s.field_name == self._runtime_probe_key and s.got != s.expected)
        ]

    expected = sorted({str(s.expected)
                       for s in filtered_suggestions})
    probe_values = {s.got
                    for s in filtered_suggestions}

    assert len(probe_values) == 1
    probe_value = str(next(iter(probe_values)))

    return [
        matcher.ProbeInfoSuggestion(
            self._key, probe_value,
            f'Expected AVL attribute {self._key!r} equal to one of '
            f'{expected!r}, but got {probe_value!r}.')
    ]


class JoinedAVLAttributeSuggester(matcher.ISuggester):

  def __init__(self, suggesters: Sequence[matcher.ISuggester]):
    self._suggesters = suggesters

  def BuildSuggestion(self, suggestion):
    suggestions: List[matcher.ProbeInfoSuggestion] = []
    for suggester in self._suggesters:
      suggestions.extend(suggester.BuildSuggestion(suggestion))
    return suggestions


def GetFieldConverter(
    probe_info: v3_rule.AVLProbeInfo, key: str,
    matcher_type: Type[runtime_probe_matchers.FieldMatcher],
    runtime_probe_key_mapping: Optional[Mapping[str, str]] = None,
    suggester_type: Type[
        AVLAttributeSuggesterBase] = SingleValueAVLAttributeSuggester
) -> builder.IProbeInfoConverterBuildResult:
  """A general field converter.

  It tries to fetch values of a key and return a matcher to match any of them.

  Args:
    probe_info: The ProbeInfo.
    key: Key to fetch from `probe_info`.
    matcher_type: A runtime probe FieldMatcher.
    runtime_probe_key_mapping: If contains `key`, it will be used as the runtime
                               probe matcher field name.
    suggester_type: Type of the suggester
  """
  values = probe_info.params.get(key)
  if not values:
    builder.LogBuilderError(f'Failed to get key {key!r}.')
    return None
  runtime_probe_key_mapping = runtime_probe_key_mapping or {}
  runtime_probe_key = runtime_probe_key_mapping.get(key, key)
  matchers = []
  for v in values:
    parsed = matcher_type.CONVERTER.Parse(v)
    if parsed is not None:
      matchers.append(matcher_type(runtime_probe_key, parsed))
      continue
    builder.LogBuilderError(
        f'Cannot parse {key!r} value {v!r} as type {matcher_type}. '
        'Fallback to StringEqualMatcher.')
    matchers.append(
        runtime_probe_matchers.StringEqualMatcher(runtime_probe_key, v))

  assert len(matchers) == len(values)
  suggester = suggester_type(key, runtime_probe_key)
  if len(matchers) == 1:
    return (matchers[0], suggester)
  return (runtime_probe_matchers.OrMatcher(matchers), suggester)


def JoinFieldConverters(
    converters: Iterable[builder.IProbeInfoConverterBuildResult]
) -> builder.IProbeInfoConverterBuildResult:
  """Join multiple field converters to a single converter.

  Matchers are joined by AndMatcher. Returns None if any of them is None.
  """
  matchers = []
  suggesters = []
  for c in converters:
    if c is None:
      return None
    matchers.append(c[0])
    suggesters.append(c[1])
  assert len(matchers) >= 1
  suggester = JoinedAVLAttributeSuggester(suggesters)
  if len(matchers) == 1:
    return (matchers[0], suggester)
  return (runtime_probe_matchers.AndMatcher(matchers), suggester)
