#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


def _GetMatcher(probe_info_value: collections.OrderedDict) -> matcher.Matcher:
  probe_info = v3_rule.AVLProbeInfo('dram.memory', probe_info_value)
  m = default_builder.GetDefaultBuilder().Build(
      probe_info, 'fake_model', factory_branch=None, cid=1, qid=0,
      is_probe_info_override=False)
  assert m is not None
  return m


class DramTest(unittest.TestCase):

  def testMatch(self):
    for test_name, fields, probe_info, expected_result in (
        ('part_match', {
            'part': 'part'
        }, [
            ('part', ['part']),
        ], matcher.MatchResult(True, 'DramPartNumber')),
        ('part_with_spaces_match', {
            'part': 'partwithspaces'
        }, [
            ('part', ['part with spaces']),
        ], matcher.MatchResult(True, 'DramPartNumber')),
        ('extra_part_match', {
            'part': 'part'
        }, [
            ('extra_part', ['part']),
        ], matcher.MatchResult(True, 'DramPartNumber')),
        ('extra_part_with_spaces_match', {
            'part': 'partwithspaces'
        }, [
            ('extra_part', ['part with spaces']),
        ], matcher.MatchResult(True, 'DramPartNumber')),
        ('unmatch', {
            'part': 'unmatch'
        }, [
            ('part', ['part']),
        ], matcher.MatchResult(False, 'DramPartNumber')),
    ):
      with self.subTest(test_name=test_name):
        m = _GetMatcher(collections.OrderedDict(probe_info))
        self.assertEqual(m.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    m = _GetMatcher(
        collections.OrderedDict([('part', ['part']),
                                 ('extra_part', ['part with spaces'])]))

    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': ['part', 'part'],
                'operator': 'STRING_EQUAL'
            }, {
                'operand': ['part', 'partwithspaces'],
                'operator': 'STRING_EQUAL'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    m = _GetMatcher(
        collections.OrderedDict([('part', ['part']),
                                 ('extra_part', ['part with spaces'])]))

    self.assertIsNone(m.GetProbeInfoSuggestion({
        'part': 'part'
    }))
    suggestion = m.GetProbeInfoSuggestion({
        'part': 'part2'
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='part', value='part2',
            suggestion="Expected AVL attribute 'part' equal to one of "
            "['part', 'partwithspaces'], but got 'part2'.")
    ])


if __name__ == '__main__':
  unittest.main()
