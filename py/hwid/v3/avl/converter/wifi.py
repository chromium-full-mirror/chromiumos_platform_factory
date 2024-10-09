# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

from typing import ClassVar, Iterable, Optional, Sequence, Set, Tuple

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import converters as runtime_probe_converters
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


_Hex = runtime_probe_converters.ConvertedHex
_HEX_CONVERTER = runtime_probe_matchers.HexEqualMatcher.CONVERTER


class WifiProbeAttributesSuggester(matcher.ISuggester):

  def __init__(self, key: str, vendor_key: str, device_key: str,
               subsystem_key: Optional[str]):
    self._key = key
    self._vendor_key = vendor_key
    self._device_key = device_key
    self._subsystem_key = subsystem_key
    self._expected_keys = [self._vendor_key, self._device_key]
    if self._subsystem_key is not None:
      self._expected_keys.append(self._subsystem_key)

  def _BuildWifiProbeAttributesFromSuggestion(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Tuple[Set[str], Set[str]]:
    if isinstance(suggestion, runtime_probe_matchers.FieldProbeInfoSuggestion):
      return set(), set()

    if isinstance(suggestion, runtime_probe_matchers.OrProbeInfoSuggestion):
      all_got, all_expected = set(), set()
      for s in suggestion.suggestions:
        gots, expecteds = self._BuildWifiProbeAttributesFromSuggestion(s)
        all_got.update(gots)
        all_expected.update(expecteds)
      return all_got, all_expected

    filtered_suggestions = {
        s.field_name: s
        for s in suggestion.suggestions
        if isinstance(s, runtime_probe_matchers.FieldProbeInfoSuggestion) and
        s.field_name in self._expected_keys
    }
    if set(self._expected_keys) != set(filtered_suggestions):
      return set(), set()

    got = (f'{filtered_suggestions[self._vendor_key].got}, '
           f'{filtered_suggestions[self._device_key].got}')
    expected = (f'{filtered_suggestions[self._vendor_key].expected}, '
                f'{filtered_suggestions[self._device_key].expected}')
    if self._subsystem_key is not None:
      got += f', {filtered_suggestions[self._subsystem_key].got}'
      expected += f', {filtered_suggestions[self._subsystem_key].expected}'
    return {got}, {expected}

  def BuildSuggestion(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    if isinstance(suggestion, runtime_probe_matchers.FieldProbeInfoSuggestion):
      return []
    all_got, all_expected = self._BuildWifiProbeAttributesFromSuggestion(
        suggestion)
    assert len(all_got) == 1
    got = next(iter(all_got))
    return [
        matcher.ProbeInfoSuggestion(
            self._key, got,
            f'Expected AVL attribute {self._key!r} equals to one of '
            f'{sorted(all_expected)!r}, but got '
            f"{got!r}({', '.join(self._expected_keys)}).")
    ]


def _ParseWifiAttributes(
    value: str) -> Optional[Tuple[_Hex, _Hex, Optional[_Hex]]]:
  attrs = value.split(', ')
  if len(attrs) != 2 and len(attrs) != 3:
    builder.LogBuilderError(f'Got unexpected wifi attributes {value!r}')
    return None

  vid = runtime_probe_matchers.HexEqualMatcher.CONVERTER.Parse(attrs[0])
  pid = runtime_probe_matchers.HexEqualMatcher.CONVERTER.Parse(attrs[1])
  if not vid or not pid:
    builder.LogBuilderError(
        f'Invalid vid/pid value of wifi attributes {attrs!r}')
    return None
  subsystem = None
  if len(attrs) == 3:
    subsystem = runtime_probe_matchers.HexEqualMatcher.CONVERTER.Parse(attrs[2])
    if subsystem is None:
      builder.LogBuilderError(
          f'Invalid subsystem value of wifi attributes {attrs!r}')
      return None
  return (vid, pid, subsystem)


class _WifiConverter(builder.IProbeInfoConverter):
  VENDOR_KEY: ClassVar[str]
  DEVICE_KEY: ClassVar[str]
  SUBSYSTEM_KEY: ClassVar[Optional[str]]

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    key = 'wifi_probe_attributes'
    values = probe_info.params.get(key)
    if values is None:
      return None
    matchers = []
    for v in values:
      res = _ParseWifiAttributes(v)
      if not res:
        continue
      vid, pid, subsystem = res
      fields_matcher = [
          runtime_probe_matchers.HexEqualMatcher(self.VENDOR_KEY, vid),
          runtime_probe_matchers.HexEqualMatcher(self.DEVICE_KEY, pid),
      ]
      if subsystem is not None:
        if self.SUBSYSTEM_KEY is not None:
          fields_matcher.append(
              runtime_probe_matchers.HexEqualMatcher(self.SUBSYSTEM_KEY,
                                                     subsystem))
        else:
          builder.LogBuilderError(
              f'Unexpected subsystem in probe info value {v!r}.')
      matchers.append(runtime_probe_matchers.AndMatcher(fields_matcher))
    return (runtime_probe_matchers.OrMatcher(matchers),
            WifiProbeAttributesSuggester(key, self.VENDOR_KEY, self.DEVICE_KEY,
                                         self.SUBSYSTEM_KEY))


class WifiWithPciPrefix(_WifiConverter):
  IDENTIFIER = 'WifiWithPciPrefix'
  VENDOR_KEY = 'pci_vendor_id'
  DEVICE_KEY = 'pci_device_id'
  SUBSYSTEM_KEY = 'pci_subsystem'


class WifiNoPciPrefix(_WifiConverter):
  IDENTIFIER = 'WifiNoPciPrefix'
  VENDOR_KEY = 'vendor'
  DEVICE_KEY = 'device'
  SUBSYSTEM_KEY = 'subsystem_device'
  # crrev/c/5274547. Until GERALT.
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(15840)])


class WifiWithSdioPrefix(_WifiConverter):
  IDENTIFIER = 'WifiWithSdioPrefix'
  VENDOR_KEY = 'sdio_vendor_id'
  DEVICE_KEY = 'sdio_device_id'
  SUBSYSTEM_KEY = None


class WifiNoSdioPrefix(_WifiConverter):
  IDENTIFIER = 'WifiNoSdioPrefix'
  VENDOR_KEY = 'vendor'
  DEVICE_KEY = 'device'
  SUBSYSTEM_KEY = None


def GetConverterSets() -> Iterable[builder.ConverterSet]:
  return (
      builder.ConverterSet('wireless.pci_wireless_network', [
          WifiWithPciPrefix(),
          WifiNoPciPrefix(),
      ]),
      builder.ConverterSet('wireless.sdio_wireless_network', [
          WifiWithSdioPrefix(),
          WifiNoSdioPrefix(),
      ]),
  )
