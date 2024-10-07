#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest

from cros.factory.hwid.v3.avl import matcher
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class FakeSuggester(matcher.ISuggester):

  def BuildSuggestion(self,
                      suggestion: runtime_probe_matchers.ProbeInfoSuggestion):
    return [matcher.ProbeInfoSuggestion('key', 'value', repr(suggestion))]


class MatcherTest(unittest.TestCase):

  def testMatcher(self):
    m = matcher.Matcher([
        matcher.Matcher.Converters(
            'converter_a',
            runtime_probe_matchers.StringEqualMatcher('field_a', 'value_a'),
            FakeSuggester(),
        )
    ])
    self.assertEqual(
        matcher.MatchResult(True, 'converter_a'), m.Match({
            'field_a': 'value_a'
        }))
    self.assertEqual(
        matcher.MatchResult(False, 'converter_a'),
        m.Match({
            'field_a': 'value_b'
        }))

    self.assertEqual(
        {
            'operator': 'STRING_EQUAL',
            'operand': ['field_a', 'value_a']
        }, m.GenerateProbeConfigMatcherStatement())

    self.assertIsNone(m.GetProbeInfoSuggestion({
        'field_a': 'value_a'
    }))
    suggestion = m.GetProbeInfoSuggestion({
        'field_a': 'value_b'
    })
    assert suggestion
    self.assertEqual(
        "FieldProbeInfoSuggestion("
        "field_name='field_a', expected='value_a', got='value_b')",
        suggestion[0].suggestion)

  def testMultipleConverter(self):
    m = matcher.Matcher([
        matcher.Matcher.Converters(
            'converter_a',
            runtime_probe_matchers.StringEqualMatcher('field_a', 'value_a'),
            FakeSuggester(),
        ),
        matcher.Matcher.Converters(
            'converter_b',
            runtime_probe_matchers.StringEqualMatcher('field_b', 'value_b'),
            FakeSuggester(),
        )
    ])
    self.assertEqual(
        matcher.MatchResult(True, 'converter_a'), m.Match({
            'field_a': 'value_a'
        }))
    self.assertEqual(
        matcher.MatchResult(True, 'converter_b'), m.Match({
            'field_b': 'value_b'
        }))
    self.assertEqual(
        matcher.MatchResult(False, 'converter_b'),
        m.Match({
            'field_a': 'value_b'
        }))

    self.assertEqual(
        {
            'operator':
                'OR',
            'operand': [
                {
                    'operator': 'STRING_EQUAL',
                    'operand': ['field_a', 'value_a']
                },
                {
                    'operator': 'STRING_EQUAL',
                    'operand': ['field_b', 'value_b']
                },
            ]
        }, m.GenerateProbeConfigMatcherStatement())

    self.assertIsNone(m.GetProbeInfoSuggestion({
        'field_a': 'value_a'
    }))
    self.assertIsNone(m.GetProbeInfoSuggestion({
        'field_b': 'value_b'
    }))
    suggestion = m.GetProbeInfoSuggestion({
        'field_a': 'value_b'
    })
    assert suggestion
    self.assertEqual(
        "FieldProbeInfoSuggestion("
        "field_name='field_a', expected='value_a', got='value_b')",
        suggestion[0].suggestion)


if __name__ == '__main__':
  unittest.main()
