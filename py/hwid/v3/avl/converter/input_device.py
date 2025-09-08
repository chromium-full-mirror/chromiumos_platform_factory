# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds touchscreen / touchpad field name mappings from AVL to HWID."""

from typing import Sequence

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class InputDeviceConverter(builder.IProbeInfoConverter):
  IDENTIFIER = 'InputDevice'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.JoinFieldConverters((
        common.GetFieldConverter(probe_info, 'vendor',
                                 runtime_probe_matchers.HexEqualMatcher),
        common.GetFieldConverter(probe_info, 'product',
                                 runtime_probe_matchers.HexEqualMatcher),
    ))


def GetConverterSets() -> Sequence[builder.ConverterSet]:
  return (
      builder.ConverterSet(
          'touchscreen.input_device',
          [InputDeviceConverter()],
      ),
      builder.ConverterSet('touchpad.input_device', [InputDeviceConverter()]),
  )
