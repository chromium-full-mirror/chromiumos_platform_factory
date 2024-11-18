# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

import binascii
from typing import Optional, Sequence

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
    probe_info: v3_rule.AVLProbeInfo, key: str,
    runtime_probe_key: Optional[str] = None
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
  runtime_probe_key = runtime_probe_key or key
  return (runtime_probe_matchers.HexEqualMatcher(runtime_probe_key,
                                                 _ConvertedHex(encoded_value)),
          _ManufacturerSuggester(key, runtime_probe_key))


def _GetTpmConverters(
    probe_info) -> Sequence[builder.IProbeInfoConverterBuildResult]:
  return [
      _GetManufacturerFieldConverter(probe_info, 'manufacturer'),
      common.GetFieldConverter(probe_info, 'spec_level',
                               runtime_probe_matchers.IntegerEqualMatcher),
      common.GetFieldConverter(probe_info, 'vendor_specific',
                               runtime_probe_matchers.StringEqualMatcher)
  ]


class Tpm(builder.IProbeInfoConverter):
  IDENTIFIER = 'Tpm'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        *_GetTpmConverters(probe_info),
        common.GetFieldConverter(probe_info, 'gsc_device',
                                 runtime_probe_matchers.StringEqualMatcher),
    ))


class TpmLegacyWithoutGSCDevice(builder.IProbeInfoConverter):
  IDENTIFIER = 'TpmLegacyWithoutGSCDevice'

  # Supported until https://crrev.com/c/5966762
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(16078)])

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    gsc_device = probe_info.params.get('gsc_device', [])
    if len(gsc_device) > 0 and gsc_device[0] not in ('H1', 'DT'):
      return None
    return common.JoinFieldConverters(_GetTpmConverters(probe_info))


class TpmLegacy(builder.IProbeInfoConverter):
  IDENTIFIER = 'TpmLegacy'

  # Supported until https://crrev.com/c/5326678
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(15803)])

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    gsc_device = probe_info.params.get('gsc_device', [])
    if len(gsc_device) > 0 and gsc_device[0] not in ('H1', 'DT'):
      return None
    return _GetManufacturerFieldConverter(probe_info, 'manufacturer',
                                          'manufacturer_info')


def GetConverterSet() -> builder.ConverterSet:
  return builder.ConverterSet(
      'tpm.tpm', [Tpm(), TpmLegacyWithoutGSCDevice(),
                  TpmLegacy()])
