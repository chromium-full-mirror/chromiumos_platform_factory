#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
from typing import Optional, Sequence
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


def _GetMatcher(manufacturer: Sequence[str], model_name: Sequence[str],
                factory_branch: Optional[str]) -> matcher.Matcher:
  probe_info = v3_rule.AVLProbeInfo(
      'battery.generic_battery',
      collections.OrderedDict([
          ('manufacturer', manufacturer),
          ('model_name', model_name),
      ]))
  m = default_builder.GetDefaultBuilder().Build(
      probe_info, 'fake_model', factory_branch=factory_branch, cid=1, qid=1,
      is_probe_info_override=False)
  assert m is not None
  return m


class BatteryTest(unittest.TestCase):

  def testBattery(self):
    m = _GetMatcher(['abcde[0-9][0-9]12345'], ['abcde[0-9][0-9]12345'],
                    'factory-board-1.B')

    for test_name, fields, expected_result in (
        ('BatteryFullLengthMatch', {
            'manufacturer': 'abcde9912345',
            'model_name': 'abcde9912345',
        }, matcher.MatchResult(True, 'BatteryFullLengthMatch')),
        ('BatteryFullLengthMatch_Regex', {
            'manufacturer': 'abcde[0-9][0-9]12345',
            'model_name': 'abcde[0-9][0-9]12345',
        }, matcher.MatchResult(True, 'BatteryFullLengthMatch')),
        ('BatteryPrefixMatchLength11', {
            'manufacturer': 'abcde991234',
            'model_name': 'abcde991234',
        }, matcher.MatchResult(True, 'BatteryPrefixMatchLength11')),
        ('BatteryPrefixMatchLength11_Regex', {
            'manufacturer': 'abcde[0-9][0-9]1234',
            'model_name': 'abcde[0-9][0-9]1234',
        }, matcher.MatchResult(True, 'BatteryPrefixMatchLength11')),
        ('BatteryPrefixMatchLength7', {
            'manufacturer': 'abcde99',
            'model_name': 'abcde99',
        }, matcher.MatchResult(True, 'BatteryPrefixMatchLength7')),
        ('BatteryPrefixMatchLength7_Regex', {
            'manufacturer': 'abcde[0-9][0-9]',
            'model_name': 'abcde[0-9][0-9]',
        }, matcher.MatchResult(True, 'BatteryPrefixMatchLength7')),
        ('NotMatch', {
            'manufacturer': 'not_match',
            'model_name': 'not_match',
        }, matcher.MatchResult(False, 'BatteryPrefixMatchLength7Trim')),
    ):
      with self.subTest(test_name):
        self.assertEqual(m.Match(fields), expected_result)

  def testGetProbeInfoSuggestion(self):
    m = _GetMatcher(['abcde99', 'abcde[0-9][0-9]12345'],
                    ['abcde[0-9][0-9]12345'], 'factory-board-1.B')
    suggestion = m.GetProbeInfoSuggestion({
        'manufacturer': '123',
        'model_name': 'abc'
    })
    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            'manufacturer', '123',
            "Expected AVL attribute 'manufacturer' equal to one of ['abcde99', "
            "'abcde[0-9][0-9]12345'], but got '123'."),
        matcher.ProbeInfoSuggestion(
            'model_name', 'abc',
            "Expected AVL attribute 'model_name'='abcde[0-9][0-9]12345', "
            "but got 'abc'.")
    ])

  def testBatteryExpand_Pattern1(self):
    for (test_name, (manufacturer, model_name), expected_result) in (
        ('Match', (
            ['abcde12345[0-9]'],
            ['abcde12345[0-9]'],
        ), matcher.MatchResult(True, 'BatteryPrefixMatchLength11Expand')),
        ('NotMatch', (
            ['abcde12345A'],
            ['abcde12345A'],
        ), matcher.MatchResult(False, 'BatteryPrefixMatchLength7Trim')),
    ):
      with self.subTest(test_name):
        m = _GetMatcher(manufacturer, model_name, 'factory-board-1.B')
        self.assertEqual(
            m.Match({
                'manufacturer': 'abcde12345(0|1|2|3|4|5|6|7|8|9)',
                'model_name': 'abcde12345(0|1|2|3|4|5|6|7|8|9)',
            }), expected_result)

  def testBatteryExpand_Pattern2(self):
    for (test_name, (manufacturer, model_name), expected_result) in (
        ('Match', (
            ['abcde12345A', 'abcde12345[0-9]'],
            ['abcde12345A', 'abcde12345[0-9]'],
        ), matcher.MatchResult(True, 'BatteryPrefixMatchLength11Expand')),
        ('NotMatch_OnlyASuffix', (
            ['abcde12345A'],
            ['abcde12345A'],
        ), matcher.MatchResult(False, 'BatteryPrefixMatchLength7Trim')),
        ('NotMatch_MissingASuffix', (
            ['abcde12345[0-9]'],
            ['abcde12345[0-9]'],
        ), matcher.MatchResult(False, 'BatteryPrefixMatchLength7Trim')),
    ):
      with self.subTest(test_name):
        m = _GetMatcher(manufacturer, model_name, 'factory-board-1.B')
        self.assertEqual(
            m.Match({
                'manufacturer': 'abcde12345(0|1|2|3|4|5|6|7|8|9|A)',
                'model_name': 'abcde12345(0|1|2|3|4|5|6|7|8|9|A)',
            }), expected_result)

  def testBatteryTrim(self):
    m = _GetMatcher(['123456 abc 123'], ['abc'], 'factory-board-1.B')
    with self.subTest('BatteryPrefixMatchLength11Trim'):
      self.assertEqual(
          m.Match({
              'manufacturer': '123456 abc',
              'model_name': 'abc',
          }), matcher.MatchResult(True, 'BatteryPrefixMatchLength11Trim'))

    with self.subTest('BatteryPrefixMatchLength7Trim'):
      self.assertEqual(
          m.Match({
              'manufacturer': '123456',
              'model_name': 'abc',
          }), matcher.MatchResult(True, 'BatteryPrefixMatchLength7Trim'))

  def testBatteryToT(self):
    m = _GetMatcher(['abcde12345abc'], ['abcde12345abc'], None)
    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(),
        {
            'operand': [{
                'operand': [{
                    'operand': ['manufacturer', 'abcde12345abc'],
                    'operator': 'RE'
                }],
                'operator': 'OR'
            }, {
                'operand': [{
                    'operand': ['model_name', 'abcde12345abc'],
                    'operator': 'RE'
                }],
                'operator': 'OR'
            }],
            'operator': 'AND'
        },
    )


if __name__ == '__main__':
  unittest.main()
