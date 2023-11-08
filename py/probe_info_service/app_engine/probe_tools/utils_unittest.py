# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re
import unittest

from cros.factory.probe_info_service.app_engine import probe_info_analytics
from cros.factory.probe_info_service.app_engine.probe_tools import utils


class GetProbeParameterValueTest(unittest.TestCase):

  def testGetStringValue(self):
    param = probe_info_analytics.ProbeParameter(name="param_name",
                                                string_value="param_val")

    result = utils.GetProbeParameterValue(param)

    self.assertEqual(result, "param_val")

  def testGetIntValue(self):
    param = probe_info_analytics.ProbeParameter(name="param_name",
                                                int_value=100)

    result = utils.GetProbeParameterValue(param)

    self.assertEqual(result, 100)

  def testGetNoneValue(self):
    param = probe_info_analytics.ProbeParameter(name="param_name")

    result = utils.GetProbeParameterValue(param)

    self.assertEqual(result, None)


class ToRestrictedPatternArrayTest(unittest.TestCase):

  def testNormalString(self):
    pattern = r'ABC123'

    result = utils.ToRestrictedPatternArray(pattern)

    self.assertListEqual(result, ['A', 'B', 'C', '1', '2', '3'])

  def testNormalStringWithEscapeChr(self):
    pattern = r'A\-BC\[12\\3'

    result = utils.ToRestrictedPatternArray(pattern)

    self.assertListEqual(result,
                         ['A', r'\-', 'B', 'C', r'\[', '1', '2', r'\\', '3'])

  def testRestrictedRegexPatternString(self):
    pattern = r'[0-9]ABC[1a2b]123[A-Z]'

    result = utils.ToRestrictedPatternArray(pattern)

    self.assertListEqual(
        result, ['[0-9]', 'A', 'B', 'C', '[1a2b]', '1', '2', '3', '[A-Z]'])

  def testRestrictedRegexPatternStringWithEscapeChr(self):
    pattern = r'[0\-9]AB[a\]]12\[A-Z]'

    result = utils.ToRestrictedPatternArray(pattern)

    self.assertListEqual(
        result,
        [r'[0\-9]', 'A', 'B', r'[a\]]', '1', '2', r'\[', 'A', '-', 'Z', ']'])

  def testInvalidRegexPattern_ShouldRaiseError(self):
    pattern = r'ABC['

    with self.assertRaises(re.error):
      utils.ToRestrictedPatternArray(pattern)


class RestrictedPrefixRegexMatchTest(unittest.TestCase):

  def testNormalString_PrefixMatch_ShouldReturnTrue(self):
    pattern = r'ABC123'
    target = 'ABC1'

    result = utils.RestrictedPrefixRegexMatch(pattern, target)

    self.assertTrue(result)

  def testNormalString_FullMatch_ShouldReturnTrue(self):
    pattern = r'ABC123'
    target = 'ABC123'

    result = utils.RestrictedPrefixRegexMatch(pattern, target)

    self.assertTrue(result)

  def testNormalString_NotMatch_ShouldReturnFalse(self):
    pattern = r'ABC123'
    target = 'XXX'

    result = utils.RestrictedPrefixRegexMatch(pattern, target)

    self.assertFalse(result)

  def testNormalString_LongerTarget_ShouldReturnFalse(self):
    pattern = r'ABC123'
    target = 'ABC123456'

    result = utils.RestrictedPrefixRegexMatch(pattern, target)

    self.assertFalse(result)

  def testRegixPattern_PrefixMatch_ShouldReturnTrue(self):
    pattern = r'ABC[a-z][DEF][0-9]123'
    targets = [
        'ABC', 'ABCd', 'ABCdD', 'ABCdE5', 'ABCdF51', 'ABCdE512', 'ABCdE5123'
    ]

    for target in targets:
      result = utils.RestrictedPrefixRegexMatch(pattern, target)
      self.assertTrue(result)

  def testRegixPattern_NotMatch_ShouldReturnFalse(self):
    pattern = r'ABC[a-z][DEF][0-9]123'
    targets = [
        'XXX', 'ABC0', 'ABCd0', 'ABCdEa', 'ABCdE50', 'ABCdE510', 'ABCdE5120'
    ]

    for target in targets:
      result = utils.RestrictedPrefixRegexMatch(pattern, target)
      self.assertFalse(result)

  def testRegixPattern_LongerTarget_ShouldReturnFalse(self):
    pattern = r'ABC[a-z][DEF][0-9]123'
    target = 'ABCdE512345'

    result = utils.RestrictedPrefixRegexMatch(pattern, target)

    self.assertFalse(result)

  def testEscapeChr_PrefixMatch_ShouldReturnTrue(self):
    pattern = r'ABC\[123'
    targets = ['ABC', 'ABC[', 'ABC[1', 'ABC[12', 'ABC[123']

    for target in targets:
      result = utils.RestrictedPrefixRegexMatch(pattern, target)
      self.assertTrue(result)

  def testEscapeChr_NotMatch_ShouldReturnFalse(self):
    pattern = r'ABC\[123'
    targets = ['XXX', 'ABC\\', 'ABC\\[', 'ABC\n', 'ABC[0']

    for target in targets:
      result = utils.RestrictedPrefixRegexMatch(pattern, target)
      self.assertFalse(result)

  def testEscapeChr_LongerTarget_ShouldReturnFalse(self):
    pattern = r'ABC\[123'
    target = 'ABC[1234'

    result = utils.RestrictedPrefixRegexMatch(pattern, target)
    self.assertFalse(result)

  def testEscapeChrInRegixPattern_PrefixMatch_ShouldReturnTrue(self):
    pattern = r'ABC[a-z][D\-F][\\\]\.]123'
    targets = [
        'ABC', 'ABCd', 'ABCdF', 'ABCd-', 'ABCd-\\', 'ABCd-.', 'ABCd-]',
        'ABCd-]123'
    ]

    for target in targets:
      result = utils.RestrictedPrefixRegexMatch(pattern, target)
      self.assertTrue(result)

  def testEscapeChrInRegixPattern_NotMatch_ShouldReturnFalse(self):
    pattern = r'ABC[a-z][D\-F][\\\]\.]123'
    targets = ['XXX', 'ABCD', 'ABCdE', 'ABCd\\', 'ABCd-\\\\', 'ABCd-\\2']

    for target in targets:
      result = utils.RestrictedPrefixRegexMatch(pattern, target)
      self.assertFalse(result)

  def testEscapeChrInRegixPattern_LongerTarget_ShouldReturnFalse(self):
    pattern = r'ABC[a-z][D\-F][\\\]\.]123'
    target = 'ABCd-\\1234'

    result = utils.RestrictedPrefixRegexMatch(pattern, target)
    self.assertFalse(result)

  def testRegixPattern_InvalidPattern_ShouldRaiseError(self):
    pattern = r'ABC['
    target = 'dont care'

    with self.assertRaises(re.error):
      utils.RestrictedPrefixRegexMatch(pattern, target)


if __name__ == '__main__':
  unittest.main()
