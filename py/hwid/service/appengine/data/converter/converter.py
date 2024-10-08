# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines the converter which converts Probe Info to HWID probe values."""

from __future__ import annotations

import abc
import collections
import enum
import itertools
import logging
import re
from typing import Any, Callable, Collection, Dict, Iterator, Mapping, MutableSequence, NamedTuple, Optional, Sequence, Tuple, Union

from cros.factory.hwid.service.appengine.data.converter import converter_types
from cros.factory.hwid.v3 import contents_analyzer
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe_info_service.app_engine import stubby_pb2  # pylint: disable=no-name-in-module


_PVAlignmentStatus = contents_analyzer.ProbeValueAlignmentStatus
_ConvertedValueTypeMapping = Mapping[
    str, Sequence[converter_types.ConvertedValueType]]


class ProbeValueMatchStatus(enum.IntEnum):
  UNINITIALIZED = enum.auto()
  INCONVERTIBLE = enum.auto()
  VALUE_IS_NONE = enum.auto()
  KEY_UNMATCHED = enum.auto()
  VALUE_UNMATCHED = enum.auto()
  ALL_MATCHED = enum.auto()


class ConverterConflictException(Exception):
  """Raised if converters will cause ambiguous match."""


class AVLAttrs(str, enum.Enum):
  """Holds the attr names in AVL probe info."""

  def __format__(self, format_spec: str) -> str:
    return self.value.__format__(format_spec)


class AbstractConverter(abc.ABC):

  def __init__(self, identifier: str):
    self._identifier = identifier

  @property
  def identifier(self):
    return self._identifier

  @abc.abstractmethod
  def Match(
      self,
      comp_values: Optional[Mapping[str, Any]],
      probe_info: stubby_pb2.ProbeInfo,
      is_qual_probe_info: bool = True,
  ) -> ProbeValueMatchStatus:
    """Tries to match a probe info to HWID comp values with this converter."""

  @abc.abstractmethod
  def ConflictWithExisting(self, other: AbstractConverter) -> bool:
    """Checks if this and other converter might cause ambiguity in matching."""


class ConvertedValueSpec(NamedTuple):
  name: str
  value_factory: Optional[converter_types.ConvertedValueTypeFactory] = None
  qual_specific: Optional[bool] = False


def _ConvertValueWithDefaultTypeFactory(
    value: Any) -> Optional[converter_types.ConvertedValueType]:
  if isinstance(value, int):  # basic int type
    return converter_types.IntValueType(value)
  if isinstance(value, str):  # basic str type
    return converter_types.StrValueType(value)
  return None


_ACCEPTABLE_SPECIAL_CHAR_IN_REGEXP_OF_FIXED_VALUES = (
    # Accept the following because HWID doesn't use `re.VERBOSE` mode.
    '#',
    ' ',
    # Accept the following because they are normal character outside of `[]`,
    # which will not be accepted.
    '-',
    '~',
    '&',
)


def _IsCharAcceptableInRegexpOfFixedValues(c: str) -> bool:
  return (c.isalnum() or
          c in _ACCEPTABLE_SPECIAL_CHAR_IN_REGEXP_OF_FIXED_VALUES or
          re.escape(c) == c)


_OPENING_PARENTHESIS, _CLOSING_PARENTHESIS = '()'


def _ParseRegexpOfFixedValues(
    it: Iterator[str]) -> Optional[Tuple[Collection[str], Iterator[str]]]:
  """Recursively parses the pattern for `_SplitRegexpOfFixedValues()`.

  Args:
    it: The iterator of the pattern under parsing.  It should point to the first
      character *in* the (nested) `(...)` closure to parse.  This function
      then attempts to iterate through the closure until it reaches the closing
      parenthesis.

  Returns:
    On success, it returns a tuple of the following 2 items:
      1. The parsed fixed values.
      2. The iterator of the pattern under parsing where the parent routine
         should continue.  I.e. the first character *after* the parsed `(...)`
         closure.
    On failure, it returns `None`.
  """
  all_values = set()
  curr_value_parts_list: MutableSequence[Collection[str]] = []

  def _AppendCurrentValuePart(part: str):
    curr_value_parts_list.append((part, ))

  def _ExtendAllCurrentValues():
    all_values.update(
        ''.join(parts) for parts in itertools.product(*curr_value_parts_list))

  while True:
    curr_char = next(it, None)
    if curr_char is None:
      return None  # The `(...)` closure must end with a closing parenthesis.

    if curr_char == '\\':
      # Only accept "\<non-alnum>" that escapes <non-alnum>.
      next_char = next(it, None)
      if next_char is None or next_char.isalnum():
        return None
      _AppendCurrentValuePart(next_char)

    elif curr_char == _OPENING_PARENTHESIS:  # reaches a nested `(...)` closure
      # Disallow the extension annotation `(?...)`.
      next_char = next(it, None)
      if next_char is None or next_char == '?':
        return None

      parse_result = _ParseRegexpOfFixedValues(itertools.chain([next_char], it))
      if parse_result is None:
        return None
      sub_parts, it = parse_result
      curr_value_parts_list.append(sub_parts)

    elif curr_char == _CLOSING_PARENTHESIS:  # reaches the end of the closure
      _ExtendAllCurrentValues()
      return all_values, it

    elif curr_char == '|':  # reaches a splitter
      _ExtendAllCurrentValues()
      curr_value_parts_list = []

    elif _IsCharAcceptableInRegexpOfFixedValues(curr_char):
      _AppendCurrentValuePart(curr_char)

    else:  # Do not accept any other regexp special character.
      return None


def _SplitRegexpOfFixedValues(pattern: str) -> Optional[Collection[str]]:
  """Splits regexp pattern of the form "val1|val2|..." to {"val1", "val2", ...}

  More specifically, it only supports `()` and `|` for nested branches like
  "value|(a|b(x|y))(|d)" => {"value", "a", "ad", "bx", "by", "bxd", "byd"}.

  Args:
    pattern: The regular expression pattern to split.

  Returns:
    A list of strings if the pattern follows the acceptable form.
    Otherwise `None`.
  """
  result = _ParseRegexpOfFixedValues(iter(f'{pattern}{_CLOSING_PARENTHESIS}'))
  if result is None:
    return None
  values, remaining_it = result
  return values if next(remaining_it, None) is None else None


def _MatchValue(
    comp_value: Any,
    converted_values: Sequence[converter_types.ConvertedValueType]) -> bool:
  if isinstance(comp_value, v3_rule.Value):
    if comp_value.is_re:
      # Additional check for identical regex patterns.
      if comp_value.raw_value in {str(val)
                                  for val in converted_values}:
        return True

      values = _SplitRegexpOfFixedValues(comp_value.raw_value)
      return values is not None and all(v in converted_values for v in values)

    comp_value = comp_value.raw_value

  return comp_value in converted_values


def _MatchConvertedValues(
    converted_group_list: Collection[_ConvertedValueTypeMapping],
    comp_values: Mapping[str, Any],
) -> ProbeValueMatchStatus:
  """Matches a comp values against a _ConvertedValueTypeMapping collection.

  Args:
    converted_group_list: A collection of _ConvertedValueTypeMapping.
    comp_values: The probe value.

  Returns:
    A ProbeValueMatchStatus enum value as the match status.
  """
  for converted_group in converted_group_list:
    if not converted_group.keys() <= comp_values.keys():
      return ProbeValueMatchStatus.KEY_UNMATCHED
    for converted_name, converted_values in converted_group.items():
      if not _MatchValue(comp_values[converted_name], converted_values):
        return ProbeValueMatchStatus.VALUE_UNMATCHED
  return ProbeValueMatchStatus.ALL_MATCHED


class _ConversionError(Exception):
  """Raised when there are no probe values in probe info."""


def _ConvertProbeValueToMappings(
    value_specs: Sequence[ConvertedValueSpec],
    values: Union[Collection[str], Collection[int]],
    is_qual_probe_info: bool,
) -> Optional[Collection[_ConvertedValueTypeMapping]]:
  """Converts a collection of ConvertedValueSpec and probe info to mappings.

  Args:
    value_specs: A collection of value specs.
    values: Extracted probe info values.
    is_qual_probe_info: A bool indicating that the probe_info is qual
      specific.

  Returns:
    A collection of _ConvertedValueTypeMapping as match criteria, or None if
    this combination does not require a match.

  Raises:
    _ConversionError if the probe value cannot be converted.
  """

  # If only one value_spec in value_specs (which means no potentially unexpected
  # cross-join matches), we could merge the translated values in one map.
  if len(value_specs) == 1:
    value_spec = value_specs[0]
    if value_spec.qual_specific and not is_qual_probe_info:
      return None
    if values is None:
      raise _ConversionError('Probe values of probe info is None')
    translated_values = []
    if value_spec.value_factory is not None:
      for value in values:
        try:
          translated_value = value_spec.value_factory(value)
        except ValueError:
          continue
        translated_values.append(translated_value)
    else:
      for value in values:
        translated_value = _ConvertValueWithDefaultTypeFactory(value)
        if translated_value is None:
          raise _ConversionError(f'Invalid value ({value!r}).')
        translated_values.append(translated_value)
    return [{
        value_spec.name: translated_values
    }]

  required_value_specs = [
      value_spec for value_spec in value_specs
      if not value_spec.qual_specific or is_qual_probe_info
  ]

  if values is None:
    raise _ConversionError('Probe values of probe info is None')

  translated_group: MutableSequence[_ConvertedValueTypeMapping] = []
  for value in values:
    translated: _ConvertedValueTypeMapping = {}
    for value_spec in required_value_specs:
      if value_spec.value_factory is not None:
        try:
          translated[value_spec.name] = [value_spec.value_factory(value)]
        except ValueError:
          break
      else:
        converted = _ConvertValueWithDefaultTypeFactory(value)
        if converted is None:
          break
        translated[value_spec.name] = [converted]
    else:
      translated_group.append(translated)
  return translated_group


class FieldNameConverter(AbstractConverter):

  def __init__(
      self,
      identifier: str,
      field_name_map: Mapping[AVLAttrs, Sequence[ConvertedValueSpec]],
  ):
    super().__init__(identifier)
    self._field_name_map = field_name_map

  @classmethod
  def FromFieldMap(
      cls,
      identifier: str,
      field_name_map: Mapping[AVLAttrs, Union[ConvertedValueSpec,
                                              Sequence[ConvertedValueSpec]]],
  ) -> FieldNameConverter:
    return cls(
        identifier, {
            avl_attr: [value_spec]
            if isinstance(value_spec, ConvertedValueSpec) else value_spec
            for avl_attr, value_spec in field_name_map.items()
        })

  @property
  def field_name_map(self) -> Mapping[AVLAttrs, Sequence[ConvertedValueSpec]]:
    return self._field_name_map

  def _Convert(
      self,
      probe_info: stubby_pb2.ProbeInfo,
      is_qual_probe_info: bool,
  ) -> Optional[Collection[Collection[_ConvertedValueTypeMapping]]]:
    """Converts a probe info to an optional mapping for matching.

    This method takes probe info and their corresponding match criteria from
    self._field_name_map (including potentially multiple criteria per key) and
    returns a list of distinct _ConvertedValueTypeMapping collections. Each
    collection represents a unique match group, ensuring accurate and flexible
    matching even when key collisions might arise. This approach prevents
    unintended matches and facilitates reliable identification of intended probe
    value matches.

    Args:
      probe_info: An instance of `ProbeInfo` to generate mapping.
      is_qual_probe_info: A bool indicating that the probe_info is qual
        specific.

    Returns:
      A list of _ConvertedValueTypeMapping collections.  None if the probe info
      is invalid.
    """
    probe_info_values = collections.defaultdict(list)

    for param in probe_info.probe_parameters:
      if param.HasField('string_value'):
        probe_info_values[param.name].append(param.string_value)
      elif param.HasField('int_value'):
        probe_info_values[param.name].append(param.int_value)

    translated_groups = []
    for name, value_specs in self._field_name_map.items():
      values = probe_info_values.get(name)
      try:
        translated_group = _ConvertProbeValueToMappings(value_specs, values,
                                                        is_qual_probe_info)
      except _ConversionError:
        logging.error(
            'Cannot convert probe info to _ConvertedValueTypeMapping:'
            '(probe_info: %s, converter: %s)', values, self.identifier)
        return None
      if translated_group is None:
        continue
      translated_groups.append(translated_group)
    return list(itertools.product(*translated_groups))

  def Match(
      self,
      comp_values: Optional[Mapping[str, Any]],
      probe_info: stubby_pb2.ProbeInfo,
      is_qual_probe_info: bool = True,
  ) -> ProbeValueMatchStatus:
    converted_groups = self._Convert(probe_info, is_qual_probe_info)
    if not converted_groups:  # None or empty
      return ProbeValueMatchStatus.INCONVERTIBLE
    if not comp_values:
      return ProbeValueMatchStatus.VALUE_IS_NONE
    best_match_status = ProbeValueMatchStatus.UNINITIALIZED
    for converted_group in converted_groups:
      best_match_status = max(
          best_match_status,
          _MatchConvertedValues(converted_group, comp_values),
      )
      if best_match_status == ProbeValueMatchStatus.ALL_MATCHED:
        return ProbeValueMatchStatus.ALL_MATCHED
    return best_match_status

  def ConflictWithExisting(self, other: FieldNameConverter) -> bool:
    """Returns if field_name_map of both converters might create conflict."""
    return (self.field_name_map.items() <= other.field_name_map.items() or
            self.field_name_map.items() >= other.field_name_map.items())


class CollectionMatchResult(NamedTuple):
  alignment_status: _PVAlignmentStatus
  converter_identifier: Optional[str]


class ConverterCollection:

  def __init__(self, category):
    self._category = category
    self._converters: Dict[str, AbstractConverter] = {}

  @property
  def category(self) -> str:
    return self._category

  def AddConverter(self, conv: AbstractConverter):
    if conv.identifier in self._converters:
      raise ValueError(f'The converter {conv.identifier!r} already exists.')
    for existing_converter in self._converters.values():
      if conv.ConflictWithExisting(existing_converter):
        raise ConverterConflictException(
            f'Converter {conv.identifier!r} conflicts with existing converter '
            f'{existing_converter.identifier!r}.')
    self._converters[conv.identifier] = conv

  def GetConverter(self, identifier: str) -> Optional[AbstractConverter]:
    return self._converters.get(identifier)

  def Match(
      self,
      comp_values: Optional[Mapping[str, Any]],
      probe_info: stubby_pb2.ProbeInfo,
      is_qual_probe_info: bool = True,
  ) -> CollectionMatchResult:
    best_match_status, best_match_identifier = (
        ProbeValueMatchStatus.INCONVERTIBLE, None)
    for converter in self._converters.values():
      match_case = converter.Match(comp_values, probe_info, is_qual_probe_info)
      if match_case == ProbeValueMatchStatus.ALL_MATCHED:
        best_match_status, best_match_identifier = (match_case,
                                                    converter.identifier)
        break
      if match_case > best_match_status:  # Prefer key matched to key unmatched.
        best_match_status, best_match_identifier = (match_case,
                                                    converter.identifier)
    return CollectionMatchResult(
        _PVAlignmentStatus.ALIGNED
        if best_match_status == ProbeValueMatchStatus.ALL_MATCHED else
        _PVAlignmentStatus.NOT_ALIGNED, best_match_identifier)


# TODO(clarkchung): Consider centralizing similar converters/formatters with
# the ones used in payload generator.
class HexToHexValueFormatter(converter_types.IStrFormatter):

  def __init__(self, num_digits, source_has_prefix: bool = True,
               target_has_prefix: bool = True):
    super().__init__()
    self._num_digits = num_digits
    self._source_has_prefix = source_has_prefix
    self._target_has_prefix = target_has_prefix

  def __call__(self, value: str) -> str:
    source_prefix = '0x' if self._source_has_prefix else ''
    if not re.fullmatch(
        f'{source_prefix.lower()}0*[0-9a-f]{{1,{self._num_digits}}}', value,
        flags=re.I):
      raise converter_types.StrFormatterError(
          f'Not a regular string of {self._num_digits} digits hex number.')
    target_prefix = '0x' if self._target_has_prefix else ''
    return f'{target_prefix}{int(value, 16):0{self._num_digits}x}'


class HexEncodedStrValueFormatter(converter_types.IStrFormatter):

  def __init__(self, source_has_prefix: bool, encoding: str,
               fixed_num_bytes: Optional[int]):
    super().__init__()
    source_prefix = '0x' if source_has_prefix else ''
    self._skip_prefix_len = len(source_prefix)
    bytes_pattern = re.escape(str(fixed_num_bytes))
    repeat_pattern = (r'*'
                      if fixed_num_bytes is None else f'{{{bytes_pattern}}}')
    prefix_pattern = re.escape(source_prefix)
    byte_in_hex = r'([0-9a-f]{2})'
    self._value_pattern = f'{prefix_pattern}{byte_in_hex}{repeat_pattern}'
    self._encoding = encoding

  def __call__(self, value: str) -> str:
    if not re.fullmatch(self._value_pattern, value, flags=re.I):
      raise converter_types.StrFormatterError('Not a hex-encoded string.')
    the_bytes = bytes.fromhex(value[self._skip_prefix_len:])
    try:
      return the_bytes.decode(encoding=self._encoding)
    except ValueError as ex:
      raise converter_types.StrFormatterError(
          'Unable to decode the byte string.') from ex


class HexDecodedStrValueFormatter(converter_types.IStrFormatter):

  def __init__(self, target_has_prefix: bool, encoding: str):
    super().__init__()
    self._target_prefix = '0x' if target_has_prefix else ''
    self._encoding = encoding

  def __call__(self, value: str) -> str:
    try:
      return self._target_prefix + value.encode(encoding=self._encoding).hex()
    except UnicodeEncodeError as ex:
      raise converter_types.StrFormatterError(
          'Unable to encode the string.') from ex


def MakeFixedWidthHexValueFactory(
    width: int, source_has_prefix: bool = False, target_has_prefix: bool = True
) -> Callable[..., converter_types.FormattedStrType]:
  return converter_types.FormattedStrType.CreateInstanceFactory(
      formatter_self=HexToHexValueFormatter(width, source_has_prefix,
                                            target_has_prefix))


def MakeBothNormalizedFillWidthHexValueFactory(
    fill_width: int,
    source_has_prefix: bool = False,
    target_has_prefix: bool = True,
) -> Callable[..., converter_types.FormattedStrType]:
  return converter_types.FormattedStrType.CreateInstanceFactory(
      formatter_self=HexToHexValueFormatter(fill_width, source_has_prefix,
                                            target_has_prefix),
      formatter_other=HexToHexValueFormatter(fill_width, source_has_prefix,
                                             target_has_prefix))


def MakeHexEncodedStrValueFactory(
    source_has_prefix: bool = False, encoding: str = 'ascii',
    fixed_num_bytes: Optional[int] = None
) -> Callable[..., converter_types.FormattedStrType]:
  return converter_types.FormattedStrType.CreateInstanceFactory(
      formatter_self=HexEncodedStrValueFormatter(source_has_prefix, encoding,
                                                 fixed_num_bytes))


def MakeHexDecodedStrValueFactory(
    source_has_prefix: bool = False,
    encoding: str = 'ascii') -> Callable[..., converter_types.FormattedStrType]:
  return converter_types.FormattedStrType.CreateInstanceFactory(
      formatter_self=HexDecodedStrValueFormatter(source_has_prefix, encoding))
