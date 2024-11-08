# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

import binascii
from typing import Optional

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import converters as runtime_probe_converters
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


_ConvertedHex = runtime_probe_converters.ConvertedHex


def _HexToString(converted_hex: _ConvertedHex) -> str:
  return bytes.fromhex(str(converted_hex)[2:]).decode('ascii')


class _ManufacturerSuggester(common.AVLAttributeSuggesterBase):

  def _FormatSuggestion(
      self, suggestion: runtime_probe_matchers.FieldProbeInfoSuggestion
  ) -> Optional[matcher.ProbeInfoSuggestion]:
    if (not isinstance(suggestion.got, _ConvertedHex) or
        not isinstance(suggestion.expected, _ConvertedHex)):
      return None
    return matcher.ProbeInfoSuggestion(
        self._key, _HexToString(suggestion.got),
        f'Expected AVL attribute {self._key!r}='
        f'{_HexToString(suggestion.expected)!r}({suggestion.expected}), '
        f'but got {_HexToString(suggestion.got)!r}({suggestion.got}).')


def _GetManufacturerFieldConverter(
    probe_info: v3_rule.AVLProbeInfo,
    key: str,
) -> builder.IProbeInfoConverterBuildResult:
  values = probe_info.params.get(key, [])
  if len(values) != 1:
    builder.LogBuilderError(f'Must have one manufacturer, but got {values!r}')
    return None
  try:
    encoded_value = (
        '0x' +
        binascii.hexlify(values[0].encode('ascii')).decode('ascii').lower())
  except Exception as e:
    builder.LogBuilderError(f'manufacturer encode error {e!r}')
    return None
  return (runtime_probe_matchers.HexEqualMatcher(
      key, _ConvertedHex(encoded_value)), _ManufacturerSuggester(key, key))


class Tpm(builder.IProbeInfoConverter):
  IDENTIFIER = 'Tpm'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        _GetManufacturerFieldConverter(probe_info, 'manufacturer'),
        common.GetFieldConverter(probe_info, 'spec_level',
                                 runtime_probe_matchers.IntegerEqualMatcher),
        common.GetFieldConverter(probe_info, 'vendor_specific',
                                 runtime_probe_matchers.StringEqualMatcher),
        common.GetFieldConverter(probe_info, 'gsc_device',
                                 runtime_probe_matchers.StringEqualMatcher),
    ))


def GetConverterSet() -> builder.ConverterSet:
  return builder.ConverterSet('tpm.tpm', [
      Tpm(),
  ])
