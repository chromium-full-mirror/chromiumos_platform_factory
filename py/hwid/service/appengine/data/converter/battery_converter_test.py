#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.hwid.service.appengine.data.converter import battery_converter
from cros.factory.hwid.service.appengine.data.converter import converter
from cros.factory.hwid.service.appengine.data.converter import converter_test_utils
from cros.factory.hwid.v3 import contents_analyzer
from cros.factory.hwid.v3 import rule as v3_rule


_PVAlignmentStatus = contents_analyzer.ProbeValueAlignmentStatus


class BatteryConverterCollectionTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._converter_collection = battery_converter.GetConverterCollection()

  def testFullLength_WithNormalProbeInfo_Match(self):
    comp_values = {
        'manufacturer': 'manufacturer',
        'model_name': 'model_name',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'manufacturer',
        'model_name': 'model_name',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(result.alignment_status, _PVAlignmentStatus.ALIGNED)

  def testFullLength_WithNormalProbeInfo_NotMatch(self):
    comp_values = {
        'manufacturer': 'manufacturer',
        'model_name': 'model_name',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'not-manufacturer',
        'model_name': 'model_name',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(result.alignment_status, _PVAlignmentStatus.NOT_ALIGNED)

  def testPrefixMatch_WithNormalProbeInfo_Length7(self):
    comp_values = {
        'manufacturer': 'ABCDEFG',
        'model_name': '1234567',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDEFGHIJKLMN',
        'model_name': '12345678901234',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(
        result,
        converter.CollectionMatchResult(
            _PVAlignmentStatus.ALIGNED,
            converter_identifier='prefix_match_length_7'))

  def testPrefixMatch_WithNormalProbeInfo_Length11(self):
    comp_values = {
        'manufacturer': 'ABCDEFGHIJK',
        'model_name': '12345678901',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'model_name': '12345678901234567890123456',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(
        result,
        converter.CollectionMatchResult(
            _PVAlignmentStatus.ALIGNED,
            converter_identifier='prefix_match_length_11'))

  def testFullLength_WithRegexProbeInfo_Match(self):
    comp_values = {
        'manufacturer': 'manufacturer',
        'model_name': 'model_5_G_name',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'manufacturer',
        'model_name': 'model_[0-9]_[A-Z]_name',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(result.alignment_status, _PVAlignmentStatus.ALIGNED)

  def testFullLength_WithRegexProbeInfo_WithTrailingSpaces_Match(self):
    comp_values = {
        'manufacturer': 'ABCDE  ',
        'model_name': '12345  ',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDE',
        'model_name': '[0-9]2[0-9]45[0 A][0-9 A-Z]',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(result.alignment_status, _PVAlignmentStatus.ALIGNED)

  def testFullLength_WithRegexProbeInfo_NotMatch(self):
    comp_values = {
        'manufacturer': 'manufacturer',
        'model_name': 'model_5_g_Name',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'manufacturer',
        'model_name': 'model_[0-9]_[A-Z]_name',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(result.alignment_status, _PVAlignmentStatus.NOT_ALIGNED)

  def testFullLength_WithRegexProbeInfo_Length7(self):
    comp_values = {
        'manufacturer': 'ABCDEFG',
        'model_name': '1234567',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDEFGHIJKLMN',
        'model_name': '12[0-9]45[0-9]78[0-9]01[0-9]34',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(
        result,
        converter.CollectionMatchResult(
            _PVAlignmentStatus.ALIGNED,
            converter_identifier='prefix_match_length_7'))

  def testPrefixMatch_WithRegexProbeInfo_Length11(self):
    comp_values = {
        'manufacturer': 'ABCDEFGHIJK',
        'model_name': '12345678901',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'model_name': '123[0-9]567[0-9]901[0-9]345[0-9]789[0-9]123[0-9]56',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(
        result,
        converter.CollectionMatchResult(
            _PVAlignmentStatus.ALIGNED,
            converter_identifier='prefix_match_length_11'))

  def testFullLength_WithRegexProbeInfoAndRegexCompValues_Match(self):
    comp_values = {
        'manufacturer': 'manufacturer',
        'model_name': v3_rule.Value(r'model_(1|3|5)_(A|B|C)_name', is_re=True),
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'manufacturer',
        'model_name': 'model_[0-9]_[A-Z]_name',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(result.alignment_status, _PVAlignmentStatus.ALIGNED)

  def testFullLength_WithRegexProbeInfoAndRegexCompValues_NotMatch(self):
    comp_values = {
        'manufacturer': 'manufacturer',
        'model_name': v3_rule.Value(r'model_(1|3|5)_(A|B|C)_name', is_re=True),
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'manufacturer',
        'model_name': 'model_[0-9]_[A-B]_name',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(result.alignment_status, _PVAlignmentStatus.NOT_ALIGNED)

  def testPrefixMatch_WithNormalProbeInfo_Length7WithTrailingSpaces(self):
    comp_values = {
        'manufacturer': 'ABCDE',
        'model_name': '1234',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDE  HIJ',
        'model_name': '1234   890',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(
        result,
        converter.CollectionMatchResult(
            _PVAlignmentStatus.ALIGNED,
            converter_identifier='prefix_match_length_7'))

  def testPrefixMatch_PreferLongerLength(self):
    comp_values = {
        'manufacturer': 'ABCDEFG',
        'model_name': '1234567',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDEFG    LM',
        'model_name': '1234567    23',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(
        result,
        converter.CollectionMatchResult(
            _PVAlignmentStatus.ALIGNED,
            converter_identifier='prefix_match_length_11'))

  def testPrefixMatch_WithTrailingSpace(self):
    comp_values = {
        'manufacturer': 'ABCDEF ',
        'model_name': '123456 ',
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'ABCDEF GHIJ',
        'model_name': '123456 7890',
    })

    result = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(
        result,
        converter.CollectionMatchResult(
            _PVAlignmentStatus.ALIGNED,
            converter_identifier='prefix_match_length_7'))


if __name__ == '__main__':
  unittest.main()
