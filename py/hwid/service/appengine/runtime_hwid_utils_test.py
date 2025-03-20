#!/usr/bin/env python3
# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.hwid.service.appengine import runtime_hwid_utils


class CheckIsRuntimeHWIDTest(unittest.TestCase):

  def testCheckIsRuntimeHWID_WithRuntimeHWID_ShouldReturnTrue(self):
    hwid_string = 'TESTPROJ-ABC A8A-B4T R:1-1-1-1'

    is_runtime_hwid = runtime_hwid_utils.CheckIsRuntimeHWID(hwid_string)

    self.assertTrue(is_runtime_hwid)

  def testCheckIsRuntimeHWID_WithFactoryHWID_ShouldReturnFalse(self):
    hwid_string = 'TESTPROJ-ABC A8A-B4T'

    is_runtime_hwid = runtime_hwid_utils.CheckIsRuntimeHWID(hwid_string)

    self.assertFalse(is_runtime_hwid)


class GetRuntimeHWIDComponentsTest(unittest.TestCase):

  def testGetRuntimeHWIDComponents(self):
    hwid_string = 'R:1-2-3-4-5,6-?,7'

    runtime_hwid_comps = runtime_hwid_utils.GetRuntimeHWIDComponents(
        hwid_string)

    print(runtime_hwid_comps)
    self.assertEqual(runtime_hwid_comps.feature_level, 1)
    self.assertEqual(runtime_hwid_comps.scope_level, 2)
    self.assertEqual(
        runtime_hwid_comps.component_positions, {
            'battery': ['3'],
            'camera': ['4'],
            'display_panel': ['5', '6'],
            'stylus': ['?', '7']
        })

  def testGetRuntimeHWIDComponents_WithoutRuntimeHWIDPrefix(self):
    invalid_hwid_string = '1-2-3'

    self.assertRaises(runtime_hwid_utils.InvalidRuntimeHWIDError,
                      runtime_hwid_utils.GetRuntimeHWIDComponents,
                      invalid_hwid_string)

  def testGetRuntimeHWIDComponents_WithTooManyFields(self):
    invalid_hwid_string = 'R:1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1'

    self.assertRaises(runtime_hwid_utils.InvalidRuntimeHWIDError,
                      runtime_hwid_utils.GetRuntimeHWIDComponents,
                      invalid_hwid_string)

  def testGetRuntimeHWIDComponents_WithNonIntegerFeatureEnablementFields(self):
    invalid_hwid_string = 'R:1-X-1-1'

    self.assertRaises(runtime_hwid_utils.InvalidRuntimeHWIDError,
                      runtime_hwid_utils.GetRuntimeHWIDComponents,
                      invalid_hwid_string)

  def testGetRuntimeHWIDComponents_WithInvalidCharacter(self):
    invalid_hwid_string = 'R:1-1-1-$-1'

    self.assertRaises(runtime_hwid_utils.InvalidRuntimeHWIDError,
                      runtime_hwid_utils.GetRuntimeHWIDComponents,
                      invalid_hwid_string)

  def testGetRuntimeHWIDComponents_WithInvalidCharacterCombination(self):
    invalid_hwid_string = 'R:1-1-1-#,1-1'

    self.assertRaises(runtime_hwid_utils.InvalidRuntimeHWIDError,
                      runtime_hwid_utils.GetRuntimeHWIDComponents,
                      invalid_hwid_string)


class ExtractRuntimeHWIDTest(unittest.TestCase):

  def testExtractRuntimeHWID_WithRuntimeHWID(self):
    hwid_string = 'TESTPROJ-ABC A8A-B4T R:1-2-3-4'

    masked_factory_hwid, runtime_hwid_comps = (
        runtime_hwid_utils.ExtractRuntimeHWID(hwid_string))

    self.assertEqual(masked_factory_hwid, 'TESTPROJ-ABC A8A-B4T')
    assert runtime_hwid_comps is not None
    self.assertEqual(runtime_hwid_comps.feature_level, 1)
    self.assertEqual(runtime_hwid_comps.scope_level, 2)
    self.assertEqual(runtime_hwid_comps.component_positions, {
        'battery': ['3'],
        'camera': ['4']
    })

  def testExtractRuntimeHWID_WithFactoryHWID(self):
    hwid_string = 'TESTPROJ-ABC A8A-B4T'

    factory_hwid, runtime_hwid_comps = runtime_hwid_utils.ExtractRuntimeHWID(
        hwid_string)

    self.assertEqual(factory_hwid, hwid_string)
    self.assertIsNone(runtime_hwid_comps)


if __name__ == '__main__':
  unittest.main()
