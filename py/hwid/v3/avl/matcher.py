# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines a matcher wrapping runtime probe matchers to probe AVL components."""

from __future__ import annotations

import abc
import dataclasses
from typing import Any, Mapping, Optional, Sequence

from cros.factory.hwid.v3 import database
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


@dataclasses.dataclass
class ProbeInfoSuggestion:
  # ProbeInfo key.
  key: str
  # ProbeInfo value.
  value: str
  # Suggestion message.
  suggestion: str


class ISuggester(abc.ABC):
  """Builds ProbeInfoSuggestion from a runtime probe matcher suggestion.

  Implementations can return an empty list if there are no suggestions. A
  runtime probe suggestion can generate several suggestions because it can be
  connected to various AVL ProbeInfo key/value pairs.
  """

  @abc.abstractmethod
  def BuildSuggestion(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Sequence[ProbeInfoSuggestion]:
    ...


@dataclasses.dataclass(eq=True)
class MatchResult:
  # If the component matches.
  matched: bool
  # The identifier of the converter that is matched, or the last converter if no
  # converter was matched.
  identifier: str


def _ProbedValueTypeToStrMapping(
    value: database.ProbedValueType) -> Mapping[str, str]:
  return {
      k: v.raw_value if isinstance(v, v3_rule.Value) else v
      for k, v in value.items()
  }


def _KeyMatch(suggestion: runtime_probe_matchers.ProbeInfoSuggestion) -> bool:
  if isinstance(suggestion, runtime_probe_matchers.FieldProbeInfoSuggestion):
    return suggestion.got is not None
  return all(_KeyMatch(s) for s in suggestion.suggestions)


class Matcher:
  """Wraps runtime probe matchers to match AVL components."""

  @dataclasses.dataclass
  class Converters:
    # The identifier of the converter.
    identifier: str
    # A runtime probe matcher to match component.
    matcher: runtime_probe_matchers.IMatcher
    # A suggester to generate suggestion.
    suggester: ISuggester

  def __init__(self, converters: Sequence[Converters]):
    if not converters:
      raise ValueError('The converters must not be empty.')
    self._converters = converters

  def _Match(self, component: Mapping[str, str]) -> MatchResult:
    for converter in self._converters:
      if converter.matcher.Match(component):
        return MatchResult(True, converter.identifier)
    return MatchResult(False, self._converters[-1].identifier)

  def Match(self, component: database.ProbedValueType) -> MatchResult:
    """Matches a component."""
    return self._Match(_ProbedValueTypeToStrMapping(component))

  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """Generates a matcher statement to be inserted into a probe config.

    With this we can ask RuntimeProbe to do the same matching during runtime.

    Returns: The statement, which can be appended to a probe statement.
    """
    if len(self._converters) == 1:
      return self._converters[0].matcher.GenerateProbeConfigMatcherStatement()
    joined_matcher = runtime_probe_matchers.OrMatcher(
        matchers=[x.matcher for x in self._converters])
    return joined_matcher.GenerateProbeConfigMatcherStatement()

  def GetProbeInfoSuggestion(
      self, component: database.ProbedValueType
  ) -> Optional[Sequence[ProbeInfoSuggestion]]:
    """Generates suggestion for editing ProbeInfo.

    Note: Will try to use the converter which match all keys, others will use
    the last converter to generate suggestion.

    Returns: None if component matches. Otherwise returns the suggestion.
    """

    component_str = _ProbedValueTypeToStrMapping(component)
    if self._Match(component_str).matched:
      return None
    for c in self._converters:
      runtime_probe_suggestion = c.matcher.GetProbeInfoSuggestion(component_str)
      if _KeyMatch(runtime_probe_suggestion):
        return c.suggester.BuildSuggestion(runtime_probe_suggestion)
    return self._converters[-1].suggester.BuildSuggestion(
        runtime_probe_suggestion)
