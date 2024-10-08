# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import converters as runtime_probe_converters
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class _DramFieldConverter(runtime_probe_converters.NopConverter):

  def Parse(self, value: str) -> str:
    return value.replace(' ', '')


class _DramStringEqualMatcher(runtime_probe_matchers.StringEqualMatcher):
  CONVERTER = _DramFieldConverter()


class DramPartNumber(builder.IProbeInfoConverter):
  IDENTIFIER = 'DramPartNumber'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    parts_values = list(probe_info.params.get('part', []))
    parts_values += probe_info.params.get('extra_part', [])
    if not parts_values:
      return None
    return (
        runtime_probe_matchers.OrMatcher([
            _DramStringEqualMatcher('part',
                                    _DramFieldConverter().Parse(v))
            for v in parts_values
        ]),
        common.MultiValueAVLAttributeSuggester('part', 'part'),
    )


def GetConverterSet() -> builder.ConverterSet:
  return builder.ConverterSet('dram.memory', [
      DramPartNumber(),
  ])
