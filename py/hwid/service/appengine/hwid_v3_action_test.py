#!/usr/bin/env python3
# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import unittest

from cros.factory.hwid.service.appengine import feature_matching
from cros.factory.hwid.service.appengine import features
from cros.factory.hwid.service.appengine import hwid_action
from cros.factory.hwid.service.appengine import hwid_preproc_data
from cros.factory.hwid.service.appengine import hwid_v3_action
from cros.factory.hwid.service.appengine import verification_payload_generator_config as vpg_config_module
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.utils import file_utils


GOLDEN_HWIDV3_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'testdata/v3-golden.yaml')
GOLDEN_HWIDV3_CAMERA_VIDEO_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'testdata/v3-golden-camera-and-video.yaml')
TEST_V3_HWID_1 = 'CHROMEBOOK AA5A-Y6L'
TEST_V3_HWID_WITH_CONFIGLESS = 'CHROMEBOOK-BRAND 0-8-74-180 AA5C-YNQ'

_FeatureEnablementStatus = feature_matching.FeatureEnablementStatus
_FeatureEnablementType = feature_matching.FeatureEnablementType


class HWIDV3ActionWithoutFeatureMatcherTextTest(unittest.TestCase):

  def setUp(self):
    super().setUp()

    self.preproc_data = hwid_preproc_data.HWIDV3PreprocData(
        'CHROMEBOOK', 'CHROMEBOOK', file_utils.ReadFile(GOLDEN_HWIDV3_FILE),
        file_utils.ReadFile(GOLDEN_HWIDV3_FILE), 'COMMIT-ID', None, None)
    self.action = hwid_v3_action.HWIDV3Action(self.preproc_data)

  def testGetBOM(self):
    """Tests fetching a BOM."""
    bom, configless = self.action.GetBOMAndConfigless(TEST_V3_HWID_1)

    self.assertIn(
        hwid_action.Component('chipset', 'chipset_0'),
        bom.GetComponents('chipset'))
    self.assertIn(
        hwid_action.Component('keyboard', 'keyboard_us'),
        bom.GetComponents('keyboard'))
    self.assertEqual([hwid_action.Component('battery', 'battery_huge')],
                     bom.GetComponents('battery'))
    self.assertEqual([hwid_action.Component('camera', 'camera_0')],
                     bom.GetComponents('camera'))
    self.assertCountEqual(
        [hwid_action.Component('display_panel', 'display_panel_0')],
        bom.GetComponents('display_panel'))
    self.assertCountEqual([], bom.GetComponents('stylus'))
    self.assertCountEqual([], bom.GetComponents('touchpad'))
    self.assertCountEqual([], bom.GetComponents('touchscreen'))
    self.assertCountEqual([hwid_action.Component('dram', 'dram_0')],
                          bom.GetComponents('dram'))
    self.assertCountEqual([], bom.GetComponents('cellular'))
    self.assertCountEqual([], bom.GetComponents('ethernet'))
    self.assertCountEqual([], bom.GetComponents('wireless'))
    self.assertCountEqual([hwid_action.Component('storage', 'storage_0')],
                          bom.GetComponents('storage'))

    self.assertEqual('EVT', bom.phase)
    self.assertEqual('CHROMEBOOK', bom.project)
    self.assertIsNone(configless)

    self.assertRaises(hwid_action.InvalidHWIDError,
                      self.action.GetBOMAndConfigless, 'NOTCHROMEBOOK HWID')

  def testGetBOMWithConfigless(self):
    """Tests fetching a BOM."""
    bom, configless = self.action.GetBOMAndConfigless(
        TEST_V3_HWID_WITH_CONFIGLESS)

    self.assertIn(
        hwid_action.Component('chipset', 'chipset_0'),
        bom.GetComponents('chipset'))
    self.assertIn(
        hwid_action.Component('keyboard', 'keyboard_us'),
        bom.GetComponents('keyboard'))
    self.assertIn(
        hwid_action.Component('dram', 'dram_0'), bom.GetComponents('dram'))
    self.assertEqual('EVT', bom.phase)
    self.assertIn(
        hwid_action.Component('storage', 'storage_2',
                              {"comp_group": "storage_0"}),
        bom.GetComponents('storage'))
    self.assertEqual('CHROMEBOOK', bom.project)
    self.assertEqual(
        {
            'version': 0,
            'memory': 8,
            'storage': 116,
            'feature_list': {
                'has_fingerprint': 0,
                'has_front_camera': 0,
                'has_rear_camera': 0,
                'has_stylus': 0,
                'has_touchpad': 0,
                'has_touchscreen': 1,
                'is_convertible': 0,
                'is_rma_device': 0,
            },
        }, configless)

    self.assertRaises(hwid_action.InvalidHWIDError,
                      self.action.GetBOMAndConfigless, 'NOTCHROMEBOOK HWID')

  def testGetBOMWithVerboseFlag(self):
    """Test BatchGetBom with the detail fields returned."""
    bom, configless = self.action.GetBOMAndConfigless(TEST_V3_HWID_1,
                                                      verbose=True)

    self.assertIsNone(configless)

    dram = bom.GetComponents(cls='dram')
    self.assertSequenceEqual(dram, [
        hwid_action.Component('dram', 'dram_0', fields={
            'part': 'part0',
            'size': '4G'
        })
    ])

    audio_codec = bom.GetComponents(cls='audio_codec')
    self.assertSequenceEqual(audio_codec, [
        hwid_action.Component('audio_codec', 'codec_1',
                              fields={'compact_str': 'Codec 1'}),
        hwid_action.Component('audio_codec', 'hdmi_1',
                              fields={'compact_str': 'HDMI 1'}),
    ])

    storage = bom.GetComponents(cls='storage')
    self.assertSequenceEqual(storage, [
        hwid_action.Component(
            'storage', 'storage_0', fields={
                'model': 'model0',
                'sectors': '0',
                'vendor': 'vendor0',
                'serial': v3_rule.Value(r'^#123\d+$', is_re=True)
            })
    ])

  def testGetBOMAndConfiglessWithVpgWaivedComponentCategory(self):
    vpg_config = vpg_config_module.VerificationPayloadGeneratorConfig.Create(
        waived_comp_categories=['battery'])
    bom, unused_configless = self.action.GetBOMAndConfigless(
        TEST_V3_HWID_1, require_vp_info=True, vpg_config=vpg_config)

    for comp in bom.GetComponents(cls='battery'):
      self.assertFalse(comp.is_vp_related)

    for comp in bom.GetComponents(cls='storage'):
      self.assertTrue(comp.is_vp_related)

  def testGetBOMAndConfiglessWithRuntimeHWID(self):
    bom, configless = self.action.GetBOMAndConfigless(
        'CHROMEBOOK AA5A-Y6L R:1-1-2-1-1-#-#-#-2-1-#-#-3')

    self.assertIn(
        hwid_action.Component('chipset', 'chipset_0'),
        bom.GetComponents('chipset'))
    self.assertIn(
        hwid_action.Component('keyboard', 'keyboard_us'),
        bom.GetComponents('keyboard'))
    self.assertCountEqual([hwid_action.Component('battery', 'battery_medium')],
                          bom.GetComponents('battery'))
    self.assertCountEqual([hwid_action.Component('camera', 'camera_0')],
                          bom.GetComponents('camera'))
    self.assertCountEqual(
        [hwid_action.Component('display_panel', 'display_panel_0')],
        bom.GetComponents('display_panel'))
    self.assertCountEqual([], bom.GetComponents('stylus'))
    self.assertCountEqual([], bom.GetComponents('touchpad'))
    self.assertCountEqual([], bom.GetComponents('touchscreen'))
    self.assertCountEqual([hwid_action.Component('dram', 'dram_0')],
                          bom.GetComponents('dram'))
    self.assertCountEqual([hwid_action.Component('cellular', 'cellular_0')],
                          bom.GetComponents('cellular'))
    self.assertCountEqual([], bom.GetComponents('ethernet'))
    self.assertCountEqual([], bom.GetComponents('wireless'))
    self.assertCountEqual([
        hwid_action.Component('storage', 'storage_2', {
            'comp_group': 'storage_0'
        })
    ], bom.GetComponents('storage'))
    self.assertEqual('EVT', bom.phase)
    self.assertEqual('CHROMEBOOK', bom.project)
    self.assertIsNone(configless)

  def testGetBOMAndConfiglessWithRuntimeHWID_NoComponentIsProbed(self):
    bom, configless = self.action.GetBOMAndConfigless(
        'CHROMEBOOK AA5A-Y6L R:1-1-2-X-1')

    self.assertCountEqual([hwid_action.Component('battery', 'battery_medium')],
                          bom.GetComponents('battery'))
    self.assertCountEqual([], bom.GetComponents('camera'))
    self.assertCountEqual(
        [hwid_action.Component('display_panel', 'display_panel_0')],
        bom.GetComponents('display_panel'))
    self.assertIsNone(configless)

  def testGetBOMAndConfiglessWithRuntimeHWID_WithUnidentifiedComponent(self):
    bom, configless = self.action.GetBOMAndConfigless(
        'CHROMEBOOK AA5A-Y6L R:1-1-2-?-1')

    self.assertCountEqual([hwid_action.Component('battery', 'battery_medium')],
                          bom.GetComponents('battery'))
    self.assertCountEqual(
        [hwid_action.Component('camera', 'camera_unidentified')],
        bom.GetComponents('camera'))
    self.assertCountEqual(
        [hwid_action.Component('display_panel', 'display_panel_0')],
        bom.GetComponents('display_panel'))
    self.assertIsNone(configless)

  def testGetBOMAndConfiglessWithRuntimeHWID_WithMultipleComponents(self):
    bom, configless = self.action.GetBOMAndConfigless(
        'CHROMEBOOK AA5A-Y6L R:1-1-1,2-1-1')

    self.assertCountEqual([
        hwid_action.Component('battery', 'battery_medium'),
        hwid_action.Component('battery', 'battery_small')
    ], bom.GetComponents('battery'))
    self.assertCountEqual([hwid_action.Component('camera', 'camera_0')],
                          bom.GetComponents('camera'))
    self.assertCountEqual(
        [hwid_action.Component('display_panel', 'display_panel_0')],
        bom.GetComponents('display_panel'))
    self.assertIsNone(configless)

  def testGetBOMAndConfiglessWithRuntimeHWID_ShouldIgnoreDram(self):
    for runtime_hwid in [
        'CHROMEBOOK AA5A-Y6L R:1-1-2-1-1-#-#-#-1',
        'CHROMEBOOK AA5A-Y6L R:1-1-2-1-1-#-#-#-2',
        'CHROMEBOOK AA5A-Y6L R:1-1-2-1-1-#-#-#-?',
        'CHROMEBOOK AA5A-Y6L R:1-1-2-1-1-#-#-#-X',
        'CHROMEBOOK AA5A-Y6L R:1-1-2-1-1-#-#-#-#',
    ]:
      bom, unused_configless = self.action.GetBOMAndConfigless(runtime_hwid)

      self.assertCountEqual(
          [hwid_action.Component('battery', 'battery_medium')],
          bom.GetComponents('battery'))
      self.assertCountEqual([hwid_action.Component('camera', 'camera_0')],
                            bom.GetComponents('camera'))
      self.assertCountEqual(
          [hwid_action.Component('display_panel', 'display_panel_0')],
          bom.GetComponents('display_panel'))
      self.assertCountEqual([], bom.GetComponents('stylus'))
      self.assertCountEqual([], bom.GetComponents('touchpad'))
      self.assertCountEqual([], bom.GetComponents('touchscreen'))
      self.assertCountEqual([hwid_action.Component('dram', 'dram_0')],
                            bom.GetComponents('dram'))
      self.assertCountEqual([], bom.GetComponents('cellular'))
      self.assertCountEqual([], bom.GetComponents('ethernet'))
      self.assertCountEqual([], bom.GetComponents('wireless'))
      self.assertCountEqual([hwid_action.Component('storage', 'storage_0')],
                            bom.GetComponents('storage'))

  def testGetBOMAndConfiglessWithRuntimeHWID_WithInvalidPosition(self):
    self.assertRaises(hwid_action.InvalidHWIDError,
                      self.action.GetBOMAndConfigless,
                      'CHROMEBOOK AA5A-Y6L R:1-1-100')

  def testGetBOMAndConfiglessWithRuntimeHWID_WithUnknownCharacter(self):
    self.assertRaises(hwid_action.InvalidHWIDError,
                      self.action.GetBOMAndConfigless,
                      'CHROMEBOOK AA5A-Y6L R:1-1-1-A-2')

  def testGetBOMAndConfiglessWithRuntimeHWID_WithWrongProject(self):
    self.assertRaises(hwid_action.InvalidHWIDError,
                      self.action.GetBOMAndConfigless,
                      'NOTCHROMEBOOK HWID R:1-1-1-2-3-4')

  def testGetBOMAndConfiglessWithRuntimeHWID_WithCameraAndVideo(self):
    self.preproc_data = hwid_preproc_data.HWIDV3PreprocData(
        'CHROMEBOOK', 'CHROMEBOOK',
        file_utils.ReadFile(GOLDEN_HWIDV3_CAMERA_VIDEO_FILE),
        file_utils.ReadFile(GOLDEN_HWIDV3_CAMERA_VIDEO_FILE), 'COMMIT-ID', None,
        None)
    self.action = hwid_v3_action.HWIDV3Action(self.preproc_data)
    bom, configless = self.action.GetBOMAndConfigless(
        'CHROMEBOOK ACR3 R:1-1-#-2')

    self.assertCountEqual([], bom.GetComponents('battery'))
    self.assertCountEqual([hwid_action.Component('video', 'video_1')],
                          bom.GetComponents('video'))
    self.assertCountEqual([], bom.GetComponents('camera'))
    self.assertIsNone(configless)

  def testGetFeatureEnablementStatus(self):
    status = self.action.GetFeatureEnablementStatus(TEST_V3_HWID_1)

    self.assertEqual(status, _FeatureEnablementStatus.FromHWIncompliance())


class HWIDV3ActionWithFeatureMatcherTextTest(unittest.TestCase):

  def testGetFeatureEnablementStatus(self):
    feature_matcher_builder = (
        hwid_preproc_data.HWIDV3PreprocData.HWID_FEATURE_MATCHER_BUILDER)
    raw_source = feature_matcher_builder.GenerateFeatureMatcherRawSource(
        1,
        {'ABCD': [feature_matching.FeatureEnablementType.SOFT_BRANDED_LEGACY]},
        [
            features.HWIDRequirement(description='always_match',
                                     bit_string_prerequisites=[])
        ])
    preproc_data = hwid_preproc_data.HWIDV3PreprocData(
        'CHROMEBOOK', 'CHROMEBOOK', file_utils.ReadFile(GOLDEN_HWIDV3_FILE),
        file_utils.ReadFile(GOLDEN_HWIDV3_FILE), 'COMMIT-ID', raw_source, None)
    action = hwid_v3_action.HWIDV3Action(preproc_data)

    for hwid, expected_label in (
        ('CHROMEBOOK-WXYZ A2A-BUY',
         _FeatureEnablementStatus(0, _FeatureEnablementType.DISABLED)),
        ('CHROMEBOOK-ABCD A2A-BHL',
         _FeatureEnablementStatus(1,
                                  _FeatureEnablementType.SOFT_BRANDED_LEGACY)),
    ):
      with self.subTest(hwid=hwid, expected_label=expected_label):
        actual = action.GetFeatureEnablementStatus(hwid)

        self.assertEqual(actual, expected_label)


if __name__ == '__main__':
  unittest.main()
