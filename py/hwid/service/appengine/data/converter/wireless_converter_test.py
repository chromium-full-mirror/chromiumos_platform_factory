#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.hwid.service.appengine.data.converter import wireless_converter
from cros.factory.hwid.service.appengine.data.converter import converter_test_utils
from cros.factory.hwid.v3 import contents_analyzer


_PVAlignmentStatus = contents_analyzer.ProbeValueAlignmentStatus


class WirelessConverterCollectionTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._converter_collection = wireless_converter.GetConverterCollection()

  def testMatch(self):
    for test_name, comp_values, probe_info_mapping, align_status in [
        (
            'match_without_subsystem',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
            },
            {
                'wifi_probe_attributes': '0xaa11, 0xbb22',
            },
            _PVAlignmentStatus.ALIGNED,
        ),
        (
            'unmatch_without_subsystem',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
            },
            {
                'wifi_probe_attributes': '0xaa11, 0xcc33',
            },
            _PVAlignmentStatus.NOT_ALIGNED,
        ),
        (
            'match_with_extra_subsystem_comp_value',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
                'subsystem_device': '0x1234',
            },
            {
                'wifi_probe_attributes': '0xaa11, 0xbb22',
            },
            _PVAlignmentStatus.ALIGNED,
        ),
        (
            'match_with_subsystem',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
                'subsystem_device': '0x1234',
            },
            {
                'wifi_probe_attributes': '0xaa11, 0xbb22, 0x1234',
            },
            _PVAlignmentStatus.ALIGNED,
        ),
        (
            'unmatch_with_subsystem',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
                'subsystem_device': '0x1234',
            },
            {
                'wifi_probe_attributes': '0xaa11, 0xbb22, 0x1235',
            },
            _PVAlignmentStatus.NOT_ALIGNED,
        ),
        (
            'unmatch_missing_probe_values',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
            },
            {
                'wifi_probe_attributes': '0xaa11, 0xbb22, 0x1234',
            },
            _PVAlignmentStatus.NOT_ALIGNED,
        ),
        (
            'unmatch_not_cross_join_attributes',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
                'subsystem_device': '0x1234',
            },
            {
                'wifi_probe_attributes': [
                    '0xaa11, 0xbb22, 0x5678',
                    '0xcc33, 0xdd44, 0x1234',
                ],
            },
            _PVAlignmentStatus.NOT_ALIGNED,
        ),
        (
            'unmatch_with_and_without_subsystem',
            {
                'vendor': '0xaa10',
                'device': '0xbb22',
                'subsystem_device': '0x1234',
            },
            {
                'wifi_probe_attributes': [
                    '0xaa11, 0xbb22',
                    '0xcc33, 0xdd44, 0x1234',
                ],
            },
            _PVAlignmentStatus.NOT_ALIGNED,
        ),
        (
            'match_without_subsystem_both_provided',
            {
                'vendor': '0xaa11',
                'device': '0xbb22',
                'subsystem_device': '0x1234',
            },
            {
                'wifi_probe_attributes': [
                    '0xaa11, 0xbb22',
                    '0xcc33, 0xdd44, 0x1234',
                ],
            },
            _PVAlignmentStatus.ALIGNED,
        ),
        (
            'match_with_subsystem_both_provided',
            {
                'vendor': '0xcc33',
                'device': '0xdd44',
                'subsystem_device': '0x1234',
            },
            {
                'wifi_probe_attributes': [
                    '0xaa11, 0xbb22',
                    '0xcc33, 0xdd44, 0x1234',
                ],
            },
            _PVAlignmentStatus.ALIGNED,
        ),
    ]:
      with self.subTest(test_name):
        probe_info = converter_test_utils.ProbeInfoFromMapping(
            probe_info_mapping)
        result = self._converter_collection.Match(comp_values, probe_info)
        self.assertEqual(result.alignment_status, align_status)


if __name__ == '__main__':
  unittest.main()
