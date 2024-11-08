#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


class TpmTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'tpm.tpm',
        collections.OrderedDict([
            ('spec_level', ['162']),
            ('manufacturer', ['CROS']),
            ('vendor_specific', ['xCG fTPM']),
            ('gsc_device', ['DT']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('match', {
            'manufacturer': '0x43524f53',
            'spec_level': '162',
            'vendor_specific': 'xCG fTPM',
            'gsc_device': 'DT'
        }, matcher.MatchResult(True, 'Tpm')),
        ('unmatch', {
            'manufacturer': '0x43524f53',
            'spec_level': '162',
            'vendor_specific': 'xCG fTPM',
            'gsc_device': 'NT'
        }, matcher.MatchResult(False, 'Tpm')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': ['manufacturer', '0x43524f53'],
                'operator': 'HEX_EQUAL'
            }, {
                'operand': ['spec_level', '162'],
                'operator': 'INTEGER_EQUAL'
            }, {
                'operand': ['vendor_specific', 'xCG fTPM'],
                'operator': 'STRING_EQUAL'
            }, {
                'operand': ['gsc_device', 'DT'],
                'operator': 'STRING_EQUAL'
            }],
            'operator': 'AND'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'manufacturer': '0x43524f53',
            'spec_level': '162',
            'vendor_specific': 'xCG fTPM',
            'gsc_device': 'DT'
        }))
    suggestion = self.matcher.GetProbeInfoSuggestion({
        'manufacturer': '0x43524f54',
        'spec_level': '116',
        'vendor_specific': 'not xCG fTPM',
        'gsc_device': 'H1'
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='manufacturer', value='CROT',
            suggestion="Expected AVL attribute "
            "'manufacturer'='CROS'(0x43524f53), but got 'CROT'(0x43524f54)."),
        matcher.ProbeInfoSuggestion(
            key='spec_level', value='116', suggestion="Expected AVL attribute "
            "'spec_level'='162', but got '116'."),
        matcher.ProbeInfoSuggestion(
            key='vendor_specific', value='not xCG fTPM',
            suggestion="Expected AVL attribute "
            "'vendor_specific'='xCG fTPM', but got 'not xCG fTPM'."),
        matcher.ProbeInfoSuggestion(
            key='gsc_device', value='H1', suggestion="Expected AVL attribute "
            "'gsc_device'='DT', but got 'H1'."),
    ])


if __name__ == '__main__':
  unittest.main()
