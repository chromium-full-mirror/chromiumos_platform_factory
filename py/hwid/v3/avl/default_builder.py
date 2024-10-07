# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import audio_codec
from cros.factory.hwid.v3.avl.converter import battery
from cros.factory.hwid.v3.avl.converter import camera
from cros.factory.hwid.v3.avl.converter import cpu


def GetDefaultBuilder() -> builder.Builder:
  b = builder.Builder()
  b.AddConverterSet(audio_codec.GetConverterSet())
  b.AddConverterSet(battery.GetConverterSet())
  b.AddConverterSet(cpu.GetConverterSet())
  for s in camera.GetConverterSets():
    b.AddConverterSet(s)
  return b
