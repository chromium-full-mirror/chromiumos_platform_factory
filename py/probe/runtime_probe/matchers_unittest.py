#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.probe.runtime_probe import converters
from cros.factory.probe.runtime_probe import matchers
from cros.factory.probe.runtime_probe import probe_types


class MatchersTest(unittest.TestCase):

  def testGenerateProbeConfigMatcherStatement(self):
    for matcher, statement in [
        (
            matchers.StringEqualMatcher('field_a', 'value_a'),
            {
                'operator': 'STRING_EQUAL',
                'operand': ['field_a', 'value_a']
            },
        ),
        (
            matchers.IntegerEqualMatcher('field_a', 1234),
            {
                'operator': 'INTEGER_EQUAL',
                'operand': ['field_a', '1234']
            },
        ),
        (
            matchers.HexEqualMatcher('field_a',
                                     converters.ConvertedHex('0x1a2b')),
            {
                'operator': 'HEX_EQUAL',
                'operand': ['field_a', '0x1a2b']
            },
        ),
    ]:
      with self.subTest(matcher=matcher):
        self.assertEqual(statement,
                         matcher.GenerateProbeConfigMatcherStatement())

  def testFieldMatch(self):
    for matcher_cls, expected_value, fields in [
        (
            matchers.StringEqualMatcher,
            'value_a',
            [('string', 'value_a')],
        ),
        (
            matchers.IntegerEqualMatcher,
            1234,
            [('integer', '1234')],
        ),
        (
            matchers.HexEqualMatcher,
            converters.ConvertedHex('0x1a2b'),
            [
                ('hex', '0x1a2b'),
                ('hex_no_prefix', '1a2b'),
            ],
        ),
    ]:
      for test_name, field_value in fields:
        with self.subTest(matcher_cls=matcher_cls, test_name=test_name):
          matcher = matcher_cls('field_a', expected_value)
          component = probe_types.Component(
              name='FooComponent', field_values={'field_a': field_value})
          self.assertTrue(matcher.Match(component))
          self.assertIsNone(matcher.GetProbeInfoSuggestion(component))

  def testFieldNotMatch(self):
    for matcher_cls, expected_value, fields in [
        (
            matchers.StringEqualMatcher,
            'value_a',
            [
                ('string_not_match', 'value_b', 'value_b'),
                ('field_not_found', None, None),
            ],
        ),
        (
            matchers.IntegerEqualMatcher,
            1234,
            [
                ('integer_not_match', '5678', 5678),
                ('field_not_found', None, None),
                ('field_not_int', 'not_int', None),
            ],
        ),
        (
            matchers.HexEqualMatcher,
            converters.ConvertedHex('0x1a2b'),
            [
                ('hex_not_match', '0x3c4d', converters.ConvertedHex('0x3c4d')),
                ('field_not_found', None, None),
                ('field_not_hex', 'not_hex', None),
            ],
        ),
    ]:
      for test_name, field_value, got_value in fields:
        with self.subTest(test_name=test_name, matcher_cls=matcher_cls):
          matcher = matcher_cls('field_a', expected_value)
          if field_value is None:
            component = probe_types.Component(name='FooComponent',
                                              field_values={})
          else:
            component = probe_types.Component(
                name='FooComponent', field_values={'field_a': field_value})
          self.assertFalse(matcher.Match(component))
          self.assertEqual(
              matchers.FieldProbeInfoSuggestion(
                  field_name='field_a', expected=expected_value, got=got_value),
              matcher.GetProbeInfoSuggestion(component))


if __name__ == '__main__':
  unittest.main()
