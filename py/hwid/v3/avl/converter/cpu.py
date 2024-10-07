# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds CPU field name mappings from AVL to HWID."""

from typing import ClassVar, Mapping

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class _CpuConverter(builder.IProbeInfoConverter):
  RUNTIME_PROBE_KEY_MAPPING: ClassVar[Mapping[str, str]]

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.GetFieldConverter(probe_info, 'identifier',
                                    runtime_probe_matchers.StringEqualMatcher,
                                    self.RUNTIME_PROBE_KEY_MAPPING)


class CpuModelAsIdentifier(_CpuConverter):
  IDENTIFIER = 'CpuModelAsIdentifier'
  RUNTIME_PROBE_KEY_MAPPING = {
      'identifier': 'model'
  }


class CpuChipIDAsIdentifier(_CpuConverter):
  IDENTIFIER = 'CpuChipIDAsIdentifier'
  RUNTIME_PROBE_KEY_MAPPING = {
      'identifier': 'chip_id'
  }


def GetConverterSet() -> builder.ConverterSet:
  return builder.ConverterSet('cpu.generic_cpu', [
      CpuModelAsIdentifier(),
      CpuChipIDAsIdentifier(),
  ])
