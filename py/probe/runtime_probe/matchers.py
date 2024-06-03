# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines matchers to match a comoponet or generate matcher statement"""

from __future__ import annotations

import abc
import dataclasses
import enum
import re
from typing import Any, Generic, Mapping, Optional, Sequence, TypeVar, Union

from cros.factory.probe.runtime_probe import converters


class MatherOperator(enum.Enum):
  """Matcher operators supported by RuntimeProbe.

  Only these may be utilized in the probe config. The RuntimeProbe must
  implement them before they may be generated into a probe config.
  """
  AND = enum.auto()
  OR = enum.auto()
  STRING_EQUAL = enum.auto()
  HEX_EQUAL = enum.auto()
  INTEGER_EQUAL = enum.auto()
  INTEGER_LESS = enum.auto()
  INTEGER_GREATER = enum.auto()
  RE = enum.auto()


_T = TypeVar('_T', int, str, converters.ConvertedHex, converters.ConvertedRE)


@dataclasses.dataclass
class FieldProbeInfoSuggestion(Generic[_T]):
  """Explans a field edit suggestion."""
  field_name: str
  expected: _T
  got: Optional[_T]


@dataclasses.dataclass
class AndProbeInfoSuggestion:
  """Suggestions that should all be applied to pass an AndMatcher.
  """
  suggestions: Sequence[ProbeInfoSuggestion]


@dataclasses.dataclass
class OrProbeInfoSuggestion:
  """Suggestions that should be applied at least one to pass an OrMatcher.
  """
  suggestions: Sequence[ProbeInfoSuggestion]


ProbeInfoSuggestion = Union[FieldProbeInfoSuggestion[str],
                            FieldProbeInfoSuggestion[int],
                            FieldProbeInfoSuggestion[converters.ConvertedHex],
                            FieldProbeInfoSuggestion[converters.ConvertedRE],
                            AndProbeInfoSuggestion, OrProbeInfoSuggestion]
"""Suggestions when matchers can't match a component.

This tells callers how to modify the ProbeInfo to match the component. Can be
used to show ProbeInfo modification suggestions.
"""


class IMatcher(abc.ABC):
  """Interface for a matcher."""

  @abc.abstractmethod
  def Match(self, component: Mapping[str, str]) -> bool:
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
      self, component: Mapping[str, str]) -> Optional[ProbeInfoSuggestion]:
    """Generates suggestion for editing ProbeInfo.

    Returns: None if component matches. Otherwise returns the suggestion.
    """


class FieldMatcher(IMatcher, Generic[_T]):
  """Matches if the field value is equal to the expected value.

  The value will be converted to type _T before comparison.
  """
  OPERATOR: MatherOperator
  CONVERTER: converters.IConverter[_T]

  def __init__(self, field_name: str, expected_value: _T):
    self._field_name = field_name
    self._expected_value: _T = expected_value

  def Match(self, component: Mapping[str, str]) -> bool:
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

  def _MatchExpectedValue(self, got: _T) -> bool:
    return got == self._expected_value

  def GetProbeInfoSuggestion(
      self, component: Mapping[str, str]) -> Optional[ProbeInfoSuggestion]:
    """See IMatcher."""
    got_raw = component.get(self._field_name)
    got = self.CONVERTER.Parse(got_raw) if got_raw is not None else None
    if got is not None and self._MatchExpectedValue(got):
      return None

    return FieldProbeInfoSuggestion(field_name=self._field_name,
                                    expected=self._expected_value, got=got)


class StringEqualMatcher(FieldMatcher[str]):
  """See base class."""
  OPERATOR = MatherOperator.STRING_EQUAL
  CONVERTER = converters.NopConverter()


class HexEqualMatcher(FieldMatcher[converters.ConvertedHex]):
  """See base class."""
  OPERATOR = MatherOperator.HEX_EQUAL
  CONVERTER = converters.HexConverter()


class IntegerEqualMatcher(FieldMatcher[int]):
  """See base class."""
  OPERATOR = MatherOperator.INTEGER_EQUAL
  CONVERTER = converters.IntegerConverter()


class IntegerLessMatcher(FieldMatcher[int]):
  """See base class."""
  OPERATOR = MatherOperator.INTEGER_LESS
  CONVERTER = converters.IntegerConverter()

  def _MatchExpectedValue(self, got: int) -> bool:
    return got < self._expected_value


class IntegerGreaterMatcher(FieldMatcher[int]):
  """See base class."""
  OPERATOR = MatherOperator.INTEGER_GREATER
  CONVERTER = converters.IntegerConverter()

  def _MatchExpectedValue(self, got: int) -> bool:
    return got > self._expected_value


class REMatcher(FieldMatcher[converters.ConvertedRE]):
  """Matches if the value pass the RE or is the same RE string.

  Note that matching a regular expression string is only supported on the Python
  side. In RuntimeProbe, the components always contain actual values rather than
  a regular expression.
  """
  OPERATOR = MatherOperator.RE
  CONVERTER = converters.REConverter()

  def _MatchExpectedValue(self, got: converters.ConvertedRE):
    return (got == self._expected_value or
            re.fullmatch(self._expected_value.value, got.value))


class AndMatcher(IMatcher):
  """Contains matchers which should all be applied to match."""

  def __init__(self, matchers: Sequence[IMatcher]):
    self._matchers = matchers

  def Match(self, component: Mapping[str, str]) -> bool:
    """See IMatcher."""
    return all(m.Match(component) for m in self._matchers)

  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """See IMatcher."""
    return {
        'operator':
            MatherOperator.AND.name,
        'operand': [
            m.GenerateProbeConfigMatcherStatement() for m in self._matchers
        ]
    }

  def GetProbeInfoSuggestion(
      self, component: Mapping[str, str]) -> Optional[ProbeInfoSuggestion]:
    """See IMatcher."""
    suggestions: Sequence[ProbeInfoSuggestion] = list(
        filter(None,
               [m.GetProbeInfoSuggestion(component) for m in self._matchers]))
    if not suggestions:
      return None
    if len(suggestions) == 1:
      return next(iter(suggestions))
    return AndProbeInfoSuggestion(suggestions=suggestions)


class OrMatcher(IMatcher):
  """Contains matchers which should be applied at least one to match."""

  def __init__(self, matchers: Sequence[IMatcher]):
    self._matchers = matchers

  def Match(self, component: Mapping[str, str]) -> bool:
    """See IMatcher."""
    return any(m.Match(component) for m in self._matchers)

  def GenerateProbeConfigMatcherStatement(self) -> Mapping[str, Any]:
    """See IMatcher."""
    return {
        'operator':
            MatherOperator.OR.name,
        'operand': [
            m.GenerateProbeConfigMatcherStatement() for m in self._matchers
        ]
    }

  def GetProbeInfoSuggestion(
      self, component: Mapping[str, str]) -> Optional[ProbeInfoSuggestion]:
    """See IMatcher."""
    suggestions: Sequence[ProbeInfoSuggestion] = list(
        filter(None,
               [m.GetProbeInfoSuggestion(component) for m in self._matchers]))
    if len(suggestions) != len(self._matchers):
      return None
    if len(suggestions) == 1:
      return next(iter(suggestions))
    return OrProbeInfoSuggestion(suggestions=suggestions)
