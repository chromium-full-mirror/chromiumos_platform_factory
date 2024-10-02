#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for TPM converter."""

import unittest

from cros.factory.hwid.service.appengine.data.converter import converter
from cros.factory.hwid.service.appengine.data.converter import converter_test_utils
from cros.factory.hwid.service.appengine.data.converter import tpm_converter
from cros.factory.hwid.v3 import contents_analyzer


_PVAlignmentStatus = contents_analyzer.ProbeValueAlignmentStatus


class TPMConverterCollectionTest(unittest.TestCase):

  def setUp(self):
    self._converter_collection = tpm_converter.GetConverterCollection()

  def testMatch_AllMatched(self):
    comp_values = {
        'manufacturer': '0x43524f53',
        'spec_level': '162',
        'vendor_specific': 'xCG fTPM'
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'CROS',
        'spec_level': 162,
        'vendor_specific': 'xCG fTPM',
    })

    actual = self._converter_collection.Match(comp_values, probe_info)

    expect = converter.CollectionMatchResult(_PVAlignmentStatus.ALIGNED,
                                             'full_length_match')
    self.assertEqual(actual, expect)

  def testMatch_ValueUnmatched(self):
    comp_values = {
        'manufacturer': '0x43524f53',
        'spec_level': '116',
        'vendor_specific': 'xCG fTPM'
    }
    probe_info = converter_test_utils.ProbeInfoFromMapping({
        'manufacturer': 'CROS',
        'spec_level': 162,
        'vendor_specific': 'xCG fTPM',
    })

    actual = self._converter_collection.Match(comp_values, probe_info)

    self.assertEqual(actual.alignment_status, _PVAlignmentStatus.NOT_ALIGNED)


if __name__ == '__main__':
  unittest.main()
