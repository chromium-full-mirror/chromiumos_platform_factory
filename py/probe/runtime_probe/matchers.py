# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines matchers to match a comoponet or generate matcher statement"""

import abc
import re
from typing import Any, Collection, Generic, Mapping, NamedTuple, Optional, TypeVar, Union

from cros.factory.probe.runtime_probe import converters
from cros.factory.probe.runtime_probe import probe_types


_T = TypeVar('_T', int, str, converters.ConvertedHex)


class FieldProbeInfoSuggestion(NamedTuple, Generic[_T]):
  """Explans a field edit suggestion."""
  field_name: str
  expected: _T
  got: Optional[_T]


class AndProbeInfoSuggestion(NamedTuple):
  """Suggestions that should all be applied to pass an AndMatcher.
  """
  suggestions: Collection['ProbeInfoSuggestion']


class OrProbeInfoSuggestion(NamedTuple):
  """Suggestions that should be applied at least one to pass an OrMatcher.
  """
  suggestions: Collection['ProbeInfoSuggestion']


ProbeInfoSuggestion = Union['FieldProbeInfoSuggestion[str]',
                            'FieldProbeInfoSuggestion[int]',
                            'FieldProbeInfoSuggestion[converters.ConvertedHex]',
                            AndProbeInfoSuggestion, OrProbeInfoSuggestion]
"""Suggestions when matchers can't match a component.

This tells callers how to modify the ProbeInfo to match the component. Can be
used to show ProbeInfo modification suggestions.
"""


class IMatcher(abc.ABC):
  """Interface for a matcher."""

  @abc.abstractmethod
  def Match(self, component: probe_types.Component) -> bool:
    """Matches a component.

    Returns: true if matches. Otherwise false.
    """

  @abc.abstractmethod
  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """Generates a matcher statement to be inserted into a probe config.

    With this we can ask RuntimeProbe to do the same matching during runtime.

    Returns: The statement, which can be appended to a probe statement.
    """

  @abc.abstractmethod
  def GetProbeInfoSuggestion(
      self, component: probe_types.Component) -> Optional[ProbeInfoSuggestion]:
    """Generates suggestion for editing ProbeInfo.

    Returns: None if component matches. Otherwise returns the suggestion.
    """


class _FieldEqualMatcher(IMatcher, Generic[_T]):
  """Matches if the field value is equal to the expected value.

  The value will be converted to type _T before comparison.
  """
  OPERATOR: probe_types.MatherOperator
  CONVERTER: converters.IConverter[_T]

  def __init__(self, field_name: str, expected_value: _T):
    self._field_name = field_name
    self._expected_value: _T = expected_value

  def Match(self, component: probe_types.Component) -> bool:
    """See IMatcher."""
    return self.GetProbeInfoSuggestion(component) is None

  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """See IMatcher."""
    return {
        'operator':
            self.OPERATOR.name,
        'operand': [
            self._field_name,
            self.CONVERTER.Format(self._expected_value)
        ]
    }

  def GetProbeInfoSuggestion(
      self, component: probe_types.Component) -> Optional[ProbeInfoSuggestion]:
    """See IMatcher."""
    got_raw = component.field_values.get(self._field_name)
    got = self.CONVERTER.Parse(got_raw) if got_raw is not None else None
    if got == self._expected_value:
      return None

    return FieldProbeInfoSuggestion(field_name=self._field_name,
                                    expected=self._expected_value, got=got)


class StringEqualMatcher(_FieldEqualMatcher[str]):
  """See base class."""
  OPERATOR = probe_types.MatherOperator.STRING_EQUAL
  CONVERTER = converters.NopConverter()


class HexEqualMatcher(_FieldEqualMatcher[converters.ConvertedHex]):
  """See base class."""
  OPERATOR = probe_types.MatherOperator.HEX_EQUAL
  CONVERTER = converters.HexConverter()


class IntegerEqualMatcher(_FieldEqualMatcher[int]):
  """See base class."""
  OPERATOR = probe_types.MatherOperator.INTEGER_EQUAL
  CONVERTER = converters.IntegerConverter()


class REMatcher(IMatcher):
  """Matches if the field value pass the regular expression."""

  def __init__(self, field_name: str, regular_expression: str):
    self._field_name = field_name
    self._regular_expression = regular_expression

  def Match(self, component: probe_types.Component) -> bool:
    """See IMatcher."""
    return self.GetProbeInfoSuggestion(component) is None

  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """See IMatcher."""
    return {
        'operator': probe_types.MatherOperator.RE.name,
        'operand': [self._field_name, self._regular_expression]
    }

  def GetProbeInfoSuggestion(
      self,
      component: probe_types.Component) -> Optional[FieldProbeInfoSuggestion]:
    """See IMatcher."""
    got = component.field_values.get(self._field_name)
    if got is not None and re.fullmatch(self._regular_expression, got):
      return None

    return FieldProbeInfoSuggestion(field_name=self._field_name,
                                    expected=self._regular_expression, got=got)


class AndMatcher(IMatcher):
  """Contains matchers which should all be applied to match."""

  def __init__(self, matchers: Collection[IMatcher]):
    self._matchers = matchers

  def Match(self, component: probe_types.Component) -> bool:
    """See IMatcher."""
    return all(m.Match(component) for m in self._matchers)

  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """See IMatcher."""
    return {
        'operator':
            probe_types.MatherOperator.AND.name,
        'operand': [
            m.GenerateProbeConfigMatcherStatement() for m in self._matchers
        ]
    }

  def GetProbeInfoSuggestion(
      self, component: probe_types.Component) -> Optional[ProbeInfoSuggestion]:
    """See IMatcher."""
    suggestions: Collection[ProbeInfoSuggestion] = list(
        filter(None,
               [m.GetProbeInfoSuggestion(component) for m in self._matchers]))
    if not suggestions:
      return None
    if len(suggestions) == 1:
      return next(iter(suggestions))
    return AndProbeInfoSuggestion(suggestions=suggestions)


class OrMatcher(IMatcher):
  """Contains matchers which should be applied at least one to match."""

  def __init__(self, matchers: Collection[IMatcher]):
    self._matchers = matchers

  def Match(self, component: probe_types.Component) -> bool:
    """See IMatcher."""
    return any(m.Match(component) for m in self._matchers)

  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """See IMatcher."""
    return {
        'operator':
            probe_types.MatherOperator.OR.name,
        'operand': [
            m.GenerateProbeConfigMatcherStatement() for m in self._matchers
        ]
    }

  def GetProbeInfoSuggestion(
      self, component: probe_types.Component) -> Optional[ProbeInfoSuggestion]:
    """See IMatcher."""
    suggestions: Collection[ProbeInfoSuggestion] = list(
        filter(None,
               [m.GetProbeInfoSuggestion(component) for m in self._matchers]))
    if len(suggestions) != len(self._matchers):
      return None
    if len(suggestions) == 1:
      return next(iter(suggestions))
    return OrProbeInfoSuggestion(suggestions=suggestions)
