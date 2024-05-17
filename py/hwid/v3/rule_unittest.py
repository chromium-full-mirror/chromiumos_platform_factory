#!/usr/bin/env python3
# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import pickle
import unittest

from cros.factory.hwid.v3 import rule as v3_rule


@v3_rule.RuleFunction(['string'])
def StrLen():
  return len(v3_rule.GetContext().string)


@v3_rule.RuleFunction(['string'])
def AssertStrLen(length):
  logger = v3_rule.GetLogger()
  if len(v3_rule.GetContext().string) <= length:
    logger.Error('Assertion error')


class HWIDRuleTest(unittest.TestCase):

  def setUp(self):
    self.context = v3_rule.Context(string='12345')

  def testRule(self):
    rule = v3_rule.Rule(name='foobar1', when='StrLen() > 3',
                        evaluate='AssertStrLen(3)', otherwise=None)
    self.assertEqual(None, rule.Evaluate(self.context))
    rule = v3_rule.Rule(name='foobar2', when='StrLen() > 3',
                        evaluate='AssertStrLen(6)', otherwise='AssertStrLen(8)')
    self.assertRaisesRegex(v3_rule.RuleException, r'ERROR: Assertion error',
                           rule.Evaluate, self.context)
    rule = v3_rule.Rule(name='foobar2', when='StrLen() > 6',
                        evaluate='AssertStrLen(6)', otherwise='AssertStrLen(8)')
    self.assertRaisesRegex(v3_rule.RuleException, r'ERROR: Assertion error',
                           rule.Evaluate, self.context)

  def testValue(self):
    self.assertTrue(v3_rule.Value('foo').Matches('foo'))
    self.assertFalse(v3_rule.Value('foo').Matches('bar'))
    self.assertTrue(
        v3_rule.Value('^foo.*bar$', is_re=True).Matches('fooxyzbar'))
    self.assertFalse(
        v3_rule.Value('^foo.*bar$', is_re=True).Matches('barxyzfoo'))

  def testEvaluateOnce(self):
    self.assertEqual(5, v3_rule.Rule.EvaluateOnce('StrLen()', self.context))
    self.assertRaisesRegex(v3_rule.RuleException, r'ERROR: Assertion error',
                           v3_rule.Rule.EvaluateOnce, 'AssertStrLen(6)',
                           self.context)


class AVLProbeValueTest(unittest.TestCase):

  def testValues(self):
    values = collections.OrderedDict({
        'key': 'value'
    })
    apv = v3_rule.AVLProbeValue('identifier', False, None, False, None, False,
                                values)

    self.assertEqual(apv.converter_identifier, 'identifier')
    self.assertFalse(apv.probe_value_matched, False)
    self.assertEqual(collections.OrderedDict(apv), values)

  def testNoneValues(self):
    self.assertRaisesRegex(ValueError, "values shouldn't be None",
                           v3_rule.AVLProbeValue, 'identifier', False, None,
                           False, None, False, None)

  def testProbeInfo(self):
    probe_info = v3_rule.AVLProbeInfo(
        'identifier',
        collections.OrderedDict([
            ('key1', ['value1', 'value2']),
            ('key2', ['value1']),
        ]))
    apv = v3_rule.AVLProbeValue('', False, probe_info, True, None, False,
                                collections.OrderedDict())
    assert apv.probe_info is not None
    self.assertEqual(apv.probe_info.identifier, 'identifier')
    self.assertEqual(
        apv.probe_info.params,
        collections.OrderedDict([
            ('key1', ['value1', 'value2']),
            ('key2', ['value1']),
        ]))
    self.assertTrue(apv.probe_info_matched)
    self.assertIsNone(apv.probe_info_override)
    self.assertFalse(apv.probe_info_override_matched)

    apv2 = v3_rule.AVLProbeValue('', False, None, False, probe_info, True,
                                 collections.OrderedDict())
    assert apv2.probe_info_override is not None
    self.assertEqual(apv2.probe_info_override.identifier, 'identifier')
    self.assertEqual(
        apv2.probe_info_override.params,
        collections.OrderedDict([
            ('key1', ['value1', 'value2']),
            ('key2', ['value1']),
        ]))
    self.assertTrue(apv2.probe_info_override_matched)
    self.assertIsNone(apv2.probe_info)
    self.assertFalse(apv2.probe_info_matched)

  def testPickle(self):
    probe_info = v3_rule.AVLProbeInfo(
        'identifier',
        collections.OrderedDict([
            ('key1', ['value1', 'value2']),
            ('key2', ['value1']),
        ]))
    apv = v3_rule.AVLProbeValue('', False, probe_info, True, probe_info, True,
                                collections.OrderedDict([('key', 'value')]))

    self.assertEqual(apv, pickle.loads(pickle.dumps(apv)))

  def testSorted(self):
    probe_info1 = v3_rule.AVLProbeInfo(
        'identifier1',
        collections.OrderedDict([
            ('key2', ['value2', 'value1']),
            ('key1', ['value2', 'value1']),
        ]))
    sorted_probe_info1 = v3_rule.AVLProbeInfo(
        'identifier1',
        collections.OrderedDict([
            ('key1', ['value1', 'value2']),
            ('key2', ['value1', 'value2']),
        ]))
    probe_info2 = v3_rule.AVLProbeInfo(
        'identifier2',
        collections.OrderedDict([
            ('key2', ['value2', 'value1']),
            ('key1', ['value2', 'value1']),
        ]))
    sorted_probe_info2 = v3_rule.AVLProbeInfo(
        'identifier2',
        collections.OrderedDict([
            ('key1', ['value1', 'value2']),
            ('key2', ['value1', 'value2']),
        ]))
    apv = v3_rule.AVLProbeValue(
        '', False, probe_info1, True, probe_info2, True,
        collections.OrderedDict([('key2', 'value2'), ('key1', 'value1')]))

    self.assertEqual(
        apv.Sorted(),
        v3_rule.AVLProbeValue(
            '', False, sorted_probe_info1, True, sorted_probe_info2, True,
            collections.OrderedDict([('key1', 'value1'), ('key2', 'value2')])))


if __name__ == '__main__':
  unittest.main()
