# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class AuidoCodecFullLengthMatch(builder.IProbeInfoConverter):
  IDENTIFIER = 'AuidoCodecFullLengthMatch'

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> builder.IProbeInfoConverterBuildResult:
    return common.GetFieldConverter(probe_info, 'name',
                                    runtime_probe_matchers.StringEqualMatcher)


def GetConverterSet() -> builder.ConverterSet:
  return builder.ConverterSet('audio_codec.audio_codec', [
      AuidoCodecFullLengthMatch(),
  ])
