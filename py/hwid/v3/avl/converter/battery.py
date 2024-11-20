# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

from typing import ClassVar, Iterator, MutableSequence, Optional, Sequence, Type

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import converters as runtime_probe_converters
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class _BatteryExpandConverter(runtime_probe_converters.IConverter[str]):
  """A special converter for RE with ()."""

  def __init__(self, pattern: str, suffix: str):
    self._pattern = pattern
    self._suffix = suffix

  def Parse(self, value: str) -> Optional[str]:
    """See base class."""
    if value.endswith(self._pattern):
      return value[:-len(self._pattern)] + self._suffix
    return None

  def Format(self, value: str) -> str:
    """See base class."""
    return value[:-len(self._suffix)] + self._pattern


class _BatteryExpandMatcherPattern1ToDigit(
    runtime_probe_matchers.FieldMatcher[str]):
  OPERATOR = runtime_probe_matchers.MatherOperator.STRING_EQUAL
  CONVERTER = _BatteryExpandConverter('(0|1|2|3|4|5|6|7|8|9)', '[0-9]')


class _BatteryExpandMatcherPattern2ToDigit(
    runtime_probe_matchers.FieldMatcher[str]):
  OPERATOR = runtime_probe_matchers.MatherOperator.STRING_EQUAL
  CONVERTER = _BatteryExpandConverter('(0|1|2|3|4|5|6|7|8|9|A)', '[0-9]')


class _BatteryExpandMatcherPattern2ToChar(
    runtime_probe_matchers.FieldMatcher[str]):
  OPERATOR = runtime_probe_matchers.MatherOperator.STRING_EQUAL
  CONVERTER = _BatteryExpandConverter('(0|1|2|3|4|5|6|7|8|9|A)', 'A')


def _ToRestrictedPatternArray(
    pattern: runtime_probe_converters.ConvertedRE) -> Optional[Sequence[str]]:
  """Converts `pattern` into an array in units of character or character set.

  Example:
  ```
    pattern: abc[a-z][0-9][a-z]123
    outputs: ['a','b','c','[a-z]','[0-9]','[a-z]','1','2','3']
  ```
  """

  def _HandleCharacterSet(pattern_it: Iterator) -> str:
    character_set = '['
    for character in pattern_it:
      if character == '\\':
        character += next(pattern_it)

      character_set += character

      if character == ']':
        break

    return character_set

  pattern_arr = []
  it = iter(pattern.value)
  for character in it:
    if character == '\\':
      character += next(it)
    elif character == '[':
      character = _HandleCharacterSet(it)

    pattern_arr.append(character)

  return pattern_arr


def _GetBatteryFieldValue(
    value: str, length: Optional[int],
    trim: bool) -> Optional[runtime_probe_converters.ConvertedRE]:
  parsed = runtime_probe_matchers.REMatcher.CONVERTER.Parse(
      value.strip() if trim else value)
  if parsed is None:
    return None
  if length is None:
    return parsed
  pattern_arr = _ToRestrictedPatternArray(parsed)
  if pattern_arr is None:
    return None
  limited_pattern = ''.join(pattern_arr[:length])
  if trim:
    limited_pattern = limited_pattern.strip()
  return runtime_probe_matchers.REMatcher.CONVERTER.Parse(limited_pattern)


class _BatteryConverter(builder.IProbeInfoConverter):
  LENGTH: ClassVar[Optional[int]] = None
  TRIM: ClassVar[bool] = False

  def _GetBatteryFieldConverter(
      self, probe_info: v3_rule.AVLProbeInfo, key: str,
      suggester_type: Type[common.AVLAttributeSuggesterBase] = common
      .SingleValueAVLAttributeSuggester
  ) -> builder.IProbeInfoConverterBuildResult:
    values = probe_info.params.get(key)
    if not values:
      return None
    matchers: MutableSequence[runtime_probe_matchers.IMatcher] = []
    for v in values:
      converted = _GetBatteryFieldValue(v, self.LENGTH, self.TRIM)
      if converted is not None:
        matchers.append(runtime_probe_matchers.REMatcher(key, converted))
        continue
      builder.LogBuilderError(f'Invalid battery {key} {v!r} '
                              f'(cut to prefix length: {self.LENGTH!r}). '
                              'Fallback to StringEqualMatcher')
      matchers.append(runtime_probe_matchers.StringEqualMatcher(key, v))

    return (
        runtime_probe_matchers.OrMatcher(matchers),
        suggester_type(key, key),
    )

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        self._GetBatteryFieldConverter(probe_info, 'manufacturer'),
        self._GetBatteryFieldConverter(probe_info, 'model_name',
                                       common.MultiValueAVLAttributeSuggester),
    ))


class BatteryFullLengthMatch(_BatteryConverter):
  IDENTIFIER = 'BatteryFullLengthMatch'


class BatteryFullLengthMatchTrim(_BatteryConverter):
  IDENTIFIER = 'BatteryFullLengthMatchTrim'
  TRIM = True
  # Until ZORK.
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(13700)])


class BatteryPrefixMatchLength11(_BatteryConverter):
  IDENTIFIER = 'BatteryPrefixMatchLength11'
  LENGTH = 11
  # See crrev/c/4150669. Until REX.
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(15708)])


class BatteryPrefixMatchLength11Trim(BatteryPrefixMatchLength11):
  IDENTIFIER = 'BatteryPrefixMatchLength11Trim'
  TRIM = True


class BatteryPrefixMatchLength11Expand(BatteryPrefixMatchLength11):
  IDENTIFIER = 'BatteryPrefixMatchLength11Expand'

  def _GetBatteryFieldConverter(
      self, probe_info: v3_rule.AVLProbeInfo, key: str,
      suggester_type: Type[common.AVLAttributeSuggesterBase] = common
      .SingleValueAVLAttributeSuggester
  ) -> builder.IProbeInfoConverterBuildResult:
    values = probe_info.params.get(key)
    if not values:
      return None
    matchers: MutableSequence[runtime_probe_matchers.IMatcher] = []
    converted_values = [
        _GetBatteryFieldValue(v, self.LENGTH, self.TRIM) for v in values
    ]
    converted_strs = {v.value
                      for v in converted_values
                      if v is not None}
    for v in converted_strs:
      if v.endswith('[0-9]'):
        matchers.append(_BatteryExpandMatcherPattern1ToDigit(key, v))
        if v[:-5] + 'A' in converted_strs:
          matchers.append(
              runtime_probe_matchers.AndMatcher([
                  _BatteryExpandMatcherPattern2ToChar(key, v[:-5] + 'A'),
                  _BatteryExpandMatcherPattern2ToDigit(key, v)
              ]))
    return (
        runtime_probe_matchers.OrMatcher(matchers),
        suggester_type(key, key),
    )


class BatteryPrefixMatchLength7(_BatteryConverter):
  IDENTIFIER = 'BatteryPrefixMatchLength7'
  LENGTH = 7
  # See crrev/c/2519243. Until REX.
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(15708)])


class BatteryPrefixMatchLength7Trim(BatteryPrefixMatchLength7):
  IDENTIFIER = 'BatteryPrefixMatchLength7Trim'
  TRIM = True


def GetConverterSet() -> builder.ConverterSet:
  return builder.ConverterSet('battery.generic_battery', [
      BatteryFullLengthMatch(),
      BatteryFullLengthMatchTrim(),
      BatteryPrefixMatchLength11(),
      BatteryPrefixMatchLength11Trim(),
      BatteryPrefixMatchLength11Expand(),
      BatteryPrefixMatchLength7(),
      BatteryPrefixMatchLength7Trim(),
  ])
