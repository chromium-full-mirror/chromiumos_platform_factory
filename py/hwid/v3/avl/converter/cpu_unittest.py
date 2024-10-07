#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


class CPUTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'cpu.generic_cpu', collections.OrderedDict([('identifier', ['cpu_1'])]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=0,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('model_as_id', {
            'model': 'cpu_1'
        }, matcher.MatchResult(True, 'CpuModelAsIdentifier')),
        ('chip_id_as_id', {
            'chip_id': 'cpu_1'
        }, matcher.MatchResult(True, 'CpuChipIDAsIdentifier')),
        ('unmatch', {
            'model': 'cpu_2'
        }, matcher.MatchResult(False, 'CpuChipIDAsIdentifier')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': ['model', 'cpu_1'],
                'operator': 'STRING_EQUAL'
            }, {
                'operand': ['chip_id', 'cpu_1'],
                'operator': 'STRING_EQUAL'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(self.matcher.GetProbeInfoSuggestion({
        'model': 'cpu_1'
    }))
    suggestion = self.matcher.GetProbeInfoSuggestion({
        'model': 'cpu_2'
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            'identifier', 'cpu_2', "Expected AVL attribute 'identifier'='cpu_1'"
            ", but got 'cpu_2'.")
    ])


if __name__ == '__main__':
  unittest.main()
