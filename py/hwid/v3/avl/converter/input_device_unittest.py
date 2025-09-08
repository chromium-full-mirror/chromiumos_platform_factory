#!/usr/bin/env python3
# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


class InputDeviceTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'touchscreen.input_device',
        collections.OrderedDict([('vendor', ['0123']),
                                 ('product', ['aaaa', 'bbbb'])]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    fields = {
        'vendor': '0123',
        'product': 'aaaa',
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(True, 'InputDevice')
    self.assertEqual(actual, expected)

  def testUnmatchWithIncorrectProduct(self):
    fields = {
        'vendor': '0123',
        'product': 'abcd',
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(False, 'InputDevice')
    self.assertEqual(actual, expected)

  def testUnmatchWithIncorrectFields(self):
    fields = {
        'hw_version': '0123',
        'fw_version': 'aaaa',
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(False, 'InputDevice')
    self.assertEqual(actual, expected)

  def testGenerateProbeConfigMatcherStatement(self):
    actual = self.matcher.GenerateProbeConfigMatcherStatement()

    expected = {
        'operator':
            'AND',
        'operand': [{
            'operator': 'HEX_EQUAL',
            'operand': ['vendor', '0x123'],
        }, {
            'operator':
                'OR',
            'operand': [{
                'operator': 'HEX_EQUAL',
                'operand': ['product', '0xaaaa']
            }, {
                'operator': 'HEX_EQUAL',
                'operand': ['product', '0xbbbb']
            }],
        }],
    }
    self.assertEqual(actual, expected)

  def testGetProbeInfoSuggestion_NoSuggestionsForMatchedComponent(self):
    actual = self.matcher.GetProbeInfoSuggestion({
        'vendor': '0123',
        'product': 'aaaa',
    })

    self.assertIsNone(actual)

  def testGetProbeInfoSuggestion_ExpectedSuggestionsForUnmatchedComponent(self):
    actual = self.matcher.GetProbeInfoSuggestion({
        'vendor': '0123',
        'product': '1234',
    })

    expected = [
        matcher.ProbeInfoSuggestion(
            key='product', value='0x1234',
            suggestion=("Expected AVL attribute 'product'='0xaaaa', but "
                        "got '0x1234'.")),
    ]
    self.assertIsNotNone(actual)
    self.assertCountEqual(actual, expected)  # type: ignore


if __name__ == '__main__':
  unittest.main()
