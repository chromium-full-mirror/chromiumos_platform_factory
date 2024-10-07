# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class DisplayPanelEdid(builder.IProbeInfoConverter):
  IDENTIFIER = 'DisplayPanelEdid'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        common.GetFieldConverter(probe_info, 'product_id',
                                 runtime_probe_matchers.HexEqualMatcher),
        common.GetFieldConverter(probe_info, 'vendor',
                                 runtime_probe_matchers.StringEqualMatcher),
        common.GetFieldConverter(probe_info, 'height',
                                 runtime_probe_matchers.IntegerEqualMatcher),
        common.GetFieldConverter(probe_info, 'width',
                                 runtime_probe_matchers.IntegerEqualMatcher),
    ))


def GetConverterSet() -> builder.ConverterSet:
  return builder.ConverterSet('display_panel.edid', [
      DisplayPanelEdid(),
  ])
