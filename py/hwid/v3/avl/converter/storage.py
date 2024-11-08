# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

import math
from typing import ClassVar, Iterable, List, Mapping, Optional, Sequence

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


_SECTOR_SIZE = 512


class StorageSizeSuggester(matcher.ISuggester):

  def __init__(self, key: str, runtime_probe_key: str, use_sector: bool):
    self._key = key
    self._runtime_probe_key = runtime_probe_key
    self._use_sector = use_sector

  def BuildSuggestion(
      self, suggestion: runtime_probe_matchers.ProbeInfoSuggestion
  ) -> Sequence[matcher.ProbeInfoSuggestion]:
    if isinstance(suggestion, runtime_probe_matchers.FieldProbeInfoSuggestion):
      return []
    suggestions: List[matcher.ProbeInfoSuggestion] = []
    for s in suggestion.suggestions:
      suggestions.extend(self.BuildSuggestion(s))
    size_suggestions = [
        s for s in suggestion.suggestions
        if (isinstance(s, runtime_probe_matchers.FieldProbeInfoSuggestion) and
            s.field_name == self._runtime_probe_key and isinstance(s.got, int))
    ]
    if not size_suggestions:
      return suggestions
    suggestion = max(size_suggestions, key=lambda s: s.expected)
    raw_size_got = suggestion.got or 0
    size_expected = suggestion.expected
    size_got = raw_size_got
    if self._use_sector:
      size_expected *= _SECTOR_SIZE
      size_got *= _SECTOR_SIZE
    size_expected = round(size_expected / (1000**3))
    size_got = size_got // (1000**3)
    suggestions.append(
        matcher.ProbeInfoSuggestion(
            self._key, str(size_got),
            f'Expected AVL attribute {self._key!r}={size_expected}GB, but got '
            f'{size_got}GB({raw_size_got} in {self._runtime_probe_key}).'))
    return suggestions


class _Storage(builder.IProbeInfoConverter):
  RUNTIME_PROBE_KEY_MAPPING: ClassVar[Mapping[str, str]] = {}
  SIZE_UPPERBOUND_RATIO: ClassVar[float] = 1.001
  SIZE_LOWERBOUND_RATIO: ClassVar[float] = 0.95
  USE_SECTOR: ClassVar[bool] = False

  def _GetSizeConverter(self, probe_info: v3_rule.AVLProbeInfo):
    values = probe_info.params.get('size_in_gb')
    if not values or len(values) > 1:
      builder.LogBuilderError(
          f'Storage must have only one size_in_gb but got {values!r}.')
      return None
    try:
      size_in_gb = int(values[0])
    except ValueError:
      builder.LogBuilderError(f'size_in_gb {values[0]!r} is not int.')
      return None

    size_in_bytes = size_in_gb * 1000**3
    key = 'size'
    upper = math.floor(size_in_bytes * self.SIZE_UPPERBOUND_RATIO)
    lower = math.floor(size_in_bytes * self.SIZE_LOWERBOUND_RATIO)
    if self.USE_SECTOR:
      key = 'sectors'
      upper //= _SECTOR_SIZE
      lower //= _SECTOR_SIZE
    return (runtime_probe_matchers.AndMatcher([
        runtime_probe_matchers.IntegerLessMatcher(key, upper),
        runtime_probe_matchers.IntegerGreaterMatcher(key, lower),
    ]), StorageSizeSuggester('size_in_gb', key, self.USE_SECTOR))


class NvmeStorage(_Storage):
  IDENTIFIER = 'NvmeStorage'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        common.GetFieldConverter(probe_info, 'nvme_model',
                                 runtime_probe_matchers.StringEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'pci_class',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'pci_device',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'pci_vendor',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        self._GetSizeConverter(probe_info),
    ))


class NvmeStorageNoSize(NvmeStorage):
  IDENTIFIER = 'NvmeStorageNoSize'
  USE_SECTOR = True


class NvmeStorageNoPciPrefix(NvmeStorageNoSize):
  IDENTIFIER = 'NvmeStorageNoPciPrefix'
  RUNTIME_PROBE_KEY_MAPPING = {
      'pci_class': 'class',
      'pci_device': 'device',
      'pci_vendor': 'vendor',
  }


def _EncodeEmmcName(value):
  return '0x' + str(value).encode('ascii').hex().lower()


class _EmmcNameSuggester(common.AVLAttributeSuggesterBase):

  def _FormatSuggestion(
      self, suggestion: runtime_probe_matchers.FieldProbeInfoSuggestion
  ) -> Optional[matcher.ProbeInfoSuggestion]:
    return matcher.ProbeInfoSuggestion(
        self._key, _EncodeEmmcName(suggestion.got),
        f'Expected AVL attribute {self._key!r}='
        f'{_EncodeEmmcName(suggestion.expected)!r}({suggestion.expected}),'
        f' but got {_EncodeEmmcName(suggestion.got)!r}({suggestion.got}).')


def _GetEmmcNameConverter(
    probe_info: v3_rule.AVLProbeInfo, runtime_probe_key_mapping: Mapping[str,
                                                                         str]
) -> builder.IProbeInfoConverterBuildResult:
  key = 'mmc_name'
  mmc_names = probe_info.params.get(key, [])
  if len(mmc_names) != 1:
    builder.LogBuilderError(f'Must have one mmc_name, but got {mmc_names!r}')
    return None
  if not mmc_names[0].startswith('0x'):
    builder.LogBuilderError(f'mmc_name {mmc_names[0]!r} does not start with 0x')
    return None

  try:
    mmc_name_decoded = bytes.fromhex(mmc_names[0][2:]).decode('ascii')
  except Exception as e:
    builder.LogBuilderError(f'mmc_name decode error {e!r}')
    return None

  runtime_probe_key = runtime_probe_key_mapping.get(key, key)
  return (runtime_probe_matchers.StringEqualMatcher(
      runtime_probe_key, mmc_name_decoded), _EmmcNameSuggester(key, key))


class EmmcStorage(_Storage):
  IDENTIFIER = 'EmmcStorage'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    matchers = [
        common.GetFieldConverter(probe_info, 'mmc_manfid',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        _GetEmmcNameConverter(probe_info, self.RUNTIME_PROBE_KEY_MAPPING),
        self._GetSizeConverter(probe_info),
    ]
    if self.COMPONENT_STATUS != builder.AVLComponentStatus.UNQUALIFIED:
      matchers.append(
          common.GetFieldConverter(probe_info, 'mmc_prv',
                                   runtime_probe_matchers.HexEqualMatcher,
                                   self.RUNTIME_PROBE_KEY_MAPPING))
    return common.JoinFieldConverters(matchers)


class EmmcStorageUnqualified(EmmcStorage):
  IDENTIFIER = 'EmmcStorageUnqualified'
  COMPONENT_STATUS = builder.AVLComponentStatus.UNQUALIFIED


class EmmcStorageNoSize(EmmcStorage):
  IDENTIFIER = 'EmmcStorageNoSize'
  USE_SECTOR = True


class EmmcStorageNoSizeUnqualified(EmmcStorageNoSize):
  IDENTIFIER = 'EmmcStorageNoSizeUnqualified'
  COMPONENT_STATUS = builder.AVLComponentStatus.UNQUALIFIED


class EmmcStorageNoMmcPrefix(EmmcStorageNoSize):
  IDENTIFIER = 'EmmcStorageNoMmcPrefix'
  RUNTIME_PROBE_KEY_MAPPING = {
      'mmc_manfid': 'manfid',
      'mmc_name': 'name',
      'mmc_prv': 'prv',
  }


class EmmcStorageNoMmcPrefixUnqualified(EmmcStorageNoMmcPrefix):
  IDENTIFIER = 'EmmcStorageNoMmcPrefixUnqualified'
  COMPONENT_STATUS = builder.AVLComponentStatus.UNQUALIFIED


class UfsStorage(_Storage):
  IDENTIFIER = 'UfsStorage'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        common.GetFieldConverter(probe_info, 'ufs_model',
                                 runtime_probe_matchers.StringEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'ufs_vendor',
                                 runtime_probe_matchers.StringEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        self._GetSizeConverter(probe_info),
    ))


class UfsStorageSizeIsWrong(UfsStorage):
  IDENTIFIER = 'UfsStorageSizeIsWrong'
  USE_SECTOR = True


class _StorageBridge(_Storage):

  def _IsNvme(self, probe_info: v3_rule.AVLProbeInfo) -> bool:
    nvme_model = probe_info.params.get('nvme_model', [])
    return (len(nvme_model) > 1 or
            (len(nvme_model) == 1 and nvme_model[0] != 'N/A'))


class PciEmmcStorageBridgeAssembly(_StorageBridge):
  IDENTIFIER = 'PciEmmcStorageBridgeAssembly'
  CHECK_CLASS: ClassVar[bool] = True

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    if self._IsNvme(probe_info):
      builder.LogBuilderError('This is a NVMe storage bridge')
      return None

    matchers = [
        common.GetFieldConverter(probe_info, 'bridge_pcie_device',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'bridge_pcie_vendor',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'mmc_manfid',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        _GetEmmcNameConverter(probe_info, self.RUNTIME_PROBE_KEY_MAPPING),
    ]
    if self.CHECK_CLASS:
      matchers.append(
          common.GetFieldConverter(probe_info, 'bridge_pcie_class',
                                   runtime_probe_matchers.HexEqualMatcher,
                                   self.RUNTIME_PROBE_KEY_MAPPING),
      )
    return common.JoinFieldConverters(matchers)


class PciEmmcStorageBridgeAssemblyNoPrefix(PciEmmcStorageBridgeAssembly):
  IDENTIFIER = 'PciEmmcStorageBridgeAssemblyNoPrefix'
  RUNTIME_PROBE_KEY_MAPPING = {
      'bridge_pcie_device': 'device',
      'bridge_pcie_vendor': 'vendor',
      'mmc_manfid': 'manfid',
      'mmc_name': 'name',
  }
  CHECK_CLASS = False


class NvmeEmmcStorageBridgeAssembly(_StorageBridge):
  IDENTIFIER = 'NvmeEmmcStorageBridgeAssembly'
  RUNTIME_PROBE_KEY_MAPPING = {
      'bridge_pcie_class': 'pci_class',
      'bridge_pcie_device': 'pci_device',
      'bridge_pcie_vendor': 'pci_vendor',
  }

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    if not self._IsNvme(probe_info):
      builder.LogBuilderError('This is a not nvme storage bridge')
      return None

    return common.JoinFieldConverters((
        common.GetFieldConverter(probe_info, 'bridge_pcie_class',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'bridge_pcie_device',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'bridge_pcie_vendor',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'nvme_model',
                                 runtime_probe_matchers.StringEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
    ))


class PciEmmcStorageBridgeHostOnly(_Storage):
  IDENTIFIER = 'PciEmmcStorageBridgeHostOnly'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        common.GetFieldConverter(probe_info, 'pci_device_id',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
        common.GetFieldConverter(probe_info, 'pci_vendor_id',
                                 runtime_probe_matchers.HexEqualMatcher,
                                 self.RUNTIME_PROBE_KEY_MAPPING),
    ))


class PciEmmcStorageBridgeHostOnlyNoPciPrefix(PciEmmcStorageBridgeHostOnly):
  IDENTIFIER = 'PciEmmcStorageBridgeHostOnlyNoPciPrefix'
  RUNTIME_PROBE_KEY_MAPPING = {
      'pci_device_id': 'device',
      'pci_vendor_id': 'vendor',
  }

  # crrev/c/5274547. Until GERALT.
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(15840)])


def GetConverterSets() -> Iterable[builder.ConverterSet]:
  return (
      builder.ConverterSet('storage.nvme_storage', [
          NvmeStorage(),
          NvmeStorageNoSize(),
          NvmeStorageNoPciPrefix(),
      ]),
      builder.ConverterSet('storage.mmc_storage', [
          EmmcStorage(),
          EmmcStorageNoSize(),
          EmmcStorageNoMmcPrefix(),
          EmmcStorageUnqualified(),
          EmmcStorageNoSizeUnqualified(),
          EmmcStorageNoMmcPrefixUnqualified(),
      ]),
      builder.ConverterSet('storage.ufs_storage', [
          UfsStorage(),
          UfsStorageSizeIsWrong(),
      ]),
      builder.ConverterSet('emmc_pcie_assembly.generic', [
          PciEmmcStorageBridgeAssembly(),
          NvmeEmmcStorageBridgeAssembly(),
          PciEmmcStorageBridgeAssemblyNoPrefix(),
      ]),
      builder.ConverterSet('emmc_pcie_storage_bridge.mmc_host', [
          PciEmmcStorageBridgeHostOnly(),
          PciEmmcStorageBridgeHostOnlyNoPciPrefix(),
      ]),
  )
