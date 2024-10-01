#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


def _CreateProbeInfo(params):
  return v3_rule.AVLProbeInfo('probe_function_a',
                              collections.OrderedDict(params))


class CommonTest(unittest.TestCase):

  def testSingleValueAVLAttributeSuggester(self):
    suggester = common.SingleValueAVLAttributeSuggester('attr1', 'key1')
    suggestions = suggester.BuildSuggestion(
        runtime_probe_matchers.FieldProbeInfoSuggestion[str]('key1', 'value1',
                                                             'value2'))
    self.assertCountEqual(suggestions, [
        matcher.ProbeInfoSuggestion(
            'attr1', 'value2',
            "Expected AVL attribute 'attr1'='value1', but got 'value2'.")
    ])

  def testMultiValueAVLAttributeSuggester(self):
    suggester = common.MultiValueAVLAttributeSuggester('attr1', 'key1')
    suggestions = suggester.BuildSuggestion(
        runtime_probe_matchers.OrProbeInfoSuggestion([
            runtime_probe_matchers.FieldProbeInfoSuggestion[str](
                'key1', 'value1', 'value3'),
            runtime_probe_matchers.FieldProbeInfoSuggestion[str](
                'key1', 'value2', 'value3')
        ]))
    self.assertCountEqual(suggestions, [
        matcher.ProbeInfoSuggestion(
            'attr1', 'value3', "Expected AVL attribute 'attr1' equal to one of "
            "['value1', 'value2'], but got 'value3'.")
    ])

  def testJoinedAVLAttributeSuggester(self):
    suggester = common.JoinedAVLAttributeSuggester([
        common.SingleValueAVLAttributeSuggester('attr1', 'key1'),
        common.SingleValueAVLAttributeSuggester('attr2', 'key2')
    ])
    suggestions = suggester.BuildSuggestion(
        runtime_probe_matchers.AndProbeInfoSuggestion([
            runtime_probe_matchers.FieldProbeInfoSuggestion[str](
                'key1', 'value1', 'value3'),
            runtime_probe_matchers.FieldProbeInfoSuggestion[str](
                'key2', 'value2', 'value3')
        ]))
    self.assertCountEqual(suggestions, [
        matcher.ProbeInfoSuggestion(
            'attr1', 'value3',
            "Expected AVL attribute 'attr1'='value1', but got 'value3'."),
        matcher.ProbeInfoSuggestion(
            'attr2', 'value3',
            "Expected AVL attribute 'attr2'='value2', but got 'value3'.")
    ])

  def testGetFieldConverter(self):
    with builder.BuilderErrorLogger('') as logs:
      probe_info = _CreateProbeInfo([
          ('key1', ['value1']),
      ])

      res = common.GetFieldConverter(probe_info, 'key1',
                                     runtime_probe_matchers.StringEqualMatcher)

      assert res is not None
      self.assertEqual(res[0].GenerateProbeConfigMatcherStatement(), {
          'operator': 'STRING_EQUAL',
          'operand': ['key1', 'value1']
      })
      self.assertEqual(logs, [])

  def testGetFieldConverterKeyNotFound(self):
    with builder.BuilderErrorLogger('') as logs:
      probe_info = _CreateProbeInfo([
          ('key1', ['value1']),
      ])

      res = common.GetFieldConverter(probe_info, 'not_found',
                                     runtime_probe_matchers.StringEqualMatcher)

      self.assertIsNone(res)
      self.assertEqual(logs, ["Failed to get key 'not_found'."])

  def testGetFieldConverterKeyNoValue(self):
    with builder.BuilderErrorLogger('') as logs:
      probe_info = _CreateProbeInfo([
          ('key1', []),
      ])

      res = common.GetFieldConverter(probe_info, 'key1',
                                     runtime_probe_matchers.StringEqualMatcher)

      self.assertIsNone(res)
      self.assertEqual(logs, ["Failed to get key 'key1'."])

  def testGetFieldConverterMapping(self):
    with builder.BuilderErrorLogger('') as logs:
      probe_info = _CreateProbeInfo([
          ('key1', ['value1']),
      ])

      res = common.GetFieldConverter(
          probe_info, 'key1', runtime_probe_matchers.StringEqualMatcher, {
              'key1': 'key2'
          })

      assert res is not None
      self.assertEqual(res[0].GenerateProbeConfigMatcherStatement(), {
          'operator': 'STRING_EQUAL',
          'operand': ['key2', 'value1']
      })
      self.assertEqual(logs, [])

  def testGetFieldConverterIngeter(self):
    with builder.BuilderErrorLogger('') as logs:
      probe_info = _CreateProbeInfo([
          ('key1', ['123']),
      ])

      res = common.GetFieldConverter(probe_info, 'key1',
                                     runtime_probe_matchers.IntegerEqualMatcher)

      assert res is not None
      self.assertEqual(res[0].GenerateProbeConfigMatcherStatement(), {
          'operator': 'INTEGER_EQUAL',
          'operand': ['key1', '123']
      })
      self.assertEqual(logs, [])

  def testGetFieldConverterNotInteger(self):
    with builder.BuilderErrorLogger('') as logs:
      probe_info = _CreateProbeInfo([
          ('key1', ['not_int']),
      ])

      res = common.GetFieldConverter(probe_info, 'key1',
                                     runtime_probe_matchers.IntegerEqualMatcher)

      assert res is not None
      self.assertEqual(res[0].GenerateProbeConfigMatcherStatement(), {
          'operator': 'STRING_EQUAL',
          'operand': ['key1', 'not_int']
      })
      self.assertEqual(logs, [
          "Cannot parse 'key1' value 'not_int' as type <class "
          "'cros.factory.probe.runtime_probe.matchers.IntegerEqualMatcher'>. "
          'Fallback to StringEqualMatcher.'
      ])

  def testGetFieldConverterMultipleValues(self):
    with builder.BuilderErrorLogger('') as logs:
      probe_info = _CreateProbeInfo([
          ('key1', ['value1', 'value2']),
      ])

      res = common.GetFieldConverter(probe_info, 'key1',
                                     runtime_probe_matchers.StringEqualMatcher)

      assert res is not None
      self.assertEqual(
          res[0].GenerateProbeConfigMatcherStatement(), {
              'operator':
                  'OR',
              'operand': [
                  {
                      'operator': 'STRING_EQUAL',
                      'operand': ['key1', 'value1']
                  },
                  {
                      'operator': 'STRING_EQUAL',
                      'operand': ['key1', 'value2']
                  },
              ]
          })
      self.assertEqual(logs, [])

  def testJoinFieldConverters(self):
    with builder.BuilderErrorLogger('') as logs:
      res = common.JoinFieldConverters([
          (
              runtime_probe_matchers.StringEqualMatcher('key1', 'value1'),
              common.NopSuggester(),
          ),
          (
              runtime_probe_matchers.StringEqualMatcher('key2', 'value2'),
              common.NopSuggester(),
          ),
      ])

      assert res is not None
      self.assertEqual(
          res[0].GenerateProbeConfigMatcherStatement(), {
              'operator':
                  'AND',
              'operand': [
                  {
                      'operator': 'STRING_EQUAL',
                      'operand': ['key1', 'value1']
                  },
                  {
                      'operator': 'STRING_EQUAL',
                      'operand': ['key2', 'value2']
                  },
              ]
          })
      self.assertEqual(logs, [])

  def testJoinFieldConvertersSingleField(self):
    with builder.BuilderErrorLogger('') as logs:
      res = common.JoinFieldConverters([
          (
              runtime_probe_matchers.StringEqualMatcher('key1', 'value1'),
              common.NopSuggester(),
          ),
      ])

      assert res is not None
      self.assertEqual(res[0].GenerateProbeConfigMatcherStatement(), {
          'operator': 'STRING_EQUAL',
          'operand': ['key1', 'value1']
      })
      self.assertEqual(logs, [])

  def testJoinFieldConvertersNone(self):
    with builder.BuilderErrorLogger('') as logs:
      res = common.JoinFieldConverters([
          (
              runtime_probe_matchers.StringEqualMatcher('key1', 'value1'),
              common.NopSuggester(),
          ),
          None,
      ])

      self.assertIsNone(res)
      self.assertEqual(logs, [])


if __name__ == '__main__':
  unittest.main()
