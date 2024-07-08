#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.external.chromeos_cli import flashrom


class PlatformAMainFirmwareContent(flashrom.FirmwareContent):

  @classmethod
  def Load(cls):  # pylint: disable=arguments-differ
    obj = super(PlatformAMainFirmwareContent, cls).Load(flashrom.TARGET_MAIN)
    return obj


class FlashromTest(unittest.TestCase):

  def testFirmwareContentCacheByClassName(self):
    general_fw_content = flashrom.FirmwareContent.Load(flashrom.TARGET_MAIN)
    platform_a_fw_content = PlatformAMainFirmwareContent.Load()

    self.assertIsInstance(general_fw_content, flashrom.FirmwareContent)
    self.assertIsInstance(platform_a_fw_content, PlatformAMainFirmwareContent)
    self.assertDictEqual(
        flashrom.FirmwareContent._target_cache,  # pylint: disable=protected-access
        {
            f"{flashrom.TARGET_MAIN}_{PlatformAMainFirmwareContent.__name__}":
                platform_a_fw_content,
            f"{flashrom.TARGET_MAIN}_{flashrom.FirmwareContent.__name__}":
                general_fw_content,
        })


if __name__ == '__main__':
  unittest.main()
