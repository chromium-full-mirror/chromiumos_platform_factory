#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


class StandaloneECComponentsTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'ec_component.ec_component_accel',
        collections.OrderedDict([('accel_component_name', ['the_name_123'])]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    fields = {
        'component_name': 'the_name_123'
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(True, 'StandaloneECComponentNameConverter')
    self.assertEqual(actual, expected)

  def testUnmatch(self):
    fields = {
        'component_name': 'the_name_456'
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(False, 'StandaloneECComponentNameConverter')
    self.assertEqual(actual, expected)

  def testGenerateProbeConfigMatcherStatement(self):
    actual = self.matcher.GenerateProbeConfigMatcherStatement()

    expected = {
        'operator': 'STRING_EQUAL',
        'operand': ['component_name', 'the_name_123']
    }
    self.assertEqual(actual, expected)

  def testGetProbeInfoSuggestion_NoSuggestionsForMatchedComponent(self):
    actual = self.matcher.GetProbeInfoSuggestion({
        'component_name': 'the_name_123'
    })

    self.assertIsNone(actual)

  def testGetProbeInfoSuggestion_ExpectedSuggestionsForUnmatchedComponent(self):
    actual = self.matcher.GetProbeInfoSuggestion({
        'component_name': 'the_name_456'
    })

    expected = [
        matcher.ProbeInfoSuggestion(
            key='accel_component_name', value='the_name_456',
            suggestion=("Expected AVL attribute 'accel_component_name'="
                        "'the_name_123', but got 'the_name_456'.")),
    ]
    self.assertIsNotNone(actual)
    self.assertCountEqual(actual, expected)  # type: ignore


class USBCECComponentsTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'usb_c.ec_components',
        collections.OrderedDict([
            ('ppc_component_name', ['the_ppc_name']),
            ('bc12_component_name', ['the_bc12_name']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    fields = {
        'component_name': 'the_ppc_name',
        'component_type': 'ppc'
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(True, 'USBCECComponentNameConverter')
    self.assertEqual(actual, expected)

  def testUnmatchComponentType(self):
    fields = {
        'component_name': 'the_ppc_name',
        'component_type': 'bc12'
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(False, 'USBCECComponentNameConverter')
    self.assertEqual(actual, expected)

  def testUnexpectedComponentType(self):
    fields = {
        'component_name': 'the_accel_name',
        'component_type': 'accel'
    }

    actual = self.matcher.Match(fields)

    expected = matcher.MatchResult(False, 'USBCECComponentNameConverter')
    self.assertEqual(actual, expected)

  def testGenerateProbeConfigMatcherStatement(self):
    actual = self.matcher.GenerateProbeConfigMatcherStatement()

    expected = {
        'operator':
            'OR',
        'operand': [{
            'operator':
                'AND',
            'operand': [{
                'operator': 'STRING_EQUAL',
                'operand': ['component_type', 'ppc'],
            }, {
                'operator': 'STRING_EQUAL',
                'operand': ['component_name', 'the_ppc_name'],
            }],
        }, {
            'operator':
                'AND',
            'operand': [{
                'operator': 'STRING_EQUAL',
                'operand': ['component_type', 'bc12'],
            }, {
                'operator': 'STRING_EQUAL',
                'operand': ['component_name', 'the_bc12_name'],
            }],
        }]
    }
    self.assertEqual(actual, expected)

  def testGetProbeInfoSuggestion_NoSuggestionsForMatchedComponent(self):
    fields = {
        'component_name': 'the_ppc_name',
        'component_type': 'ppc'
    }

    actual = self.matcher.GetProbeInfoSuggestion(fields)

    self.assertIsNone(actual)

  def testGetProbeInfoSuggestion_ExpectedSuggestionsForUnmatchedComponentName(
      self):
    fields = {
        'component_name': 'hwid_ppc_name',
        'component_type': 'ppc'
    }

    actual = self.matcher.GetProbeInfoSuggestion(fields)

    expected = [
        matcher.ProbeInfoSuggestion(
            key='ppc_component_name', value='hwid_ppc_name',
            suggestion=("Expected AVL attribute 'ppc_component_name'="
                        "'the_ppc_name', but got 'hwid_ppc_name'.")),
    ]
    self.assertIsNotNone(actual)
    self.assertCountEqual(actual, expected)  # type: ignore

  def testGetProbeInfoSuggestion_ExpectedSuggestionsForUnmatchedComponentType(
      self):
    fields = {
        'component_name': 'hwid_mux_name',
        'component_type': 'mux'
    }

    actual = self.matcher.GetProbeInfoSuggestion(fields)

    self.assertIsNotNone(actual)
    self.assertCountEqual(actual, [])  # type: ignore


if __name__ == '__main__':
  unittest.main()
