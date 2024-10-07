#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


class DisplayPanelTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'display_panel.edid',
        collections.OrderedDict([
            ('product_id', ['000a']),
            ('vendor', ['ABC']),
            ('width', ['100']),
            ('height', ['200']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('match', {
            'product_id': '000a',
            'vendor': 'ABC',
            'width': '100',
            'height': '200',
        }, matcher.MatchResult(True, 'DisplayPanelEdid')),
        ('unmatch', {
            'product_id': '000b',
            'vendor': 'ABC',
            'width': '100',
            'height': '200',
        }, matcher.MatchResult(False, 'DisplayPanelEdid')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': ['product_id', '0xa'],
                'operator': 'HEX_EQUAL'
            }, {
                'operand': ['vendor', 'ABC'],
                'operator': 'STRING_EQUAL'
            }, {
                'operand': ['height', '200'],
                'operator': 'INTEGER_EQUAL'
            }, {
                'operand': ['width', '100'],
                'operator': 'INTEGER_EQUAL'
            }],
            'operator': 'AND'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'product_id': '000a',
            'vendor': 'ABC',
            'width': '100',
            'height': '200',
        }))
    suggestion = self.matcher.GetProbeInfoSuggestion({
        'product_id': '000b',
        'vendor': 'ABD',
        'width': '200',
        'height': '100',
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='product_id', value='0xb',
            suggestion="Expected AVL attribute 'product_id'='0xa', "
            "but got '0xb'."),
        matcher.ProbeInfoSuggestion(
            key='vendor', value='ABD',
            suggestion="Expected AVL attribute 'vendor'='ABC', but got 'ABD'."),
        matcher.ProbeInfoSuggestion(
            key='height', value='100',
            suggestion="Expected AVL attribute 'height'='200', but got '100'."),
        matcher.ProbeInfoSuggestion(
            key='width', value='200',
            suggestion="Expected AVL attribute 'width'='100', but got '200'."),
    ])


if __name__ == '__main__':
  unittest.main()
