# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Testcases of converter types."""

import unittest

from cros.factory.hwid.service.appengine.data.converter import converter_types


class IntValueTypeTest(unittest.TestCase):

  def testEqual(self):
    value = converter_types.IntValueType(100)
    self.assertEqual(value, 100)
    self.assertEqual(value, '100')
    self.assertEqual(value, '0x64')

  def testUnEqual(self):
    value = converter_types.IntValueType(100)
    self.assertNotEqual(value, 200)
    self.assertNotEqual(value, '200')
    self.assertNotEqual(value, '0xc8')

  def testNotNumber(self):
    value = converter_types.IntValueType(100)
    self.assertNotEqual(value, 'this_is_not_a_number')

  def testInvalidType(self):
    value = converter_types.IntValueType(100)
    self.assertNotEqual(value, [])


class FormattedStrTypeTest(unittest.TestCase):

  def testNoFormatter(self):
    # Should be the simple str type.
    not_formatted = converter_types.FormattedStrType('not_formatted')
    self.assertEqual(not_formatted, 'not_formatted')
    self.assertNotEqual(not_formatted, 'not_formatted_diff')

  def testFormatted(self):

    def _PrefixFormatter(s: str) -> str:
      return f'(prefix){s}'

    format_self = converter_types.FormattedStrType(
        'foo', formatter_self=_PrefixFormatter)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(format_self, '(prefix)foo')

    format_other = converter_types.FormattedStrType(
        '(prefix)foo', formatter_other=_PrefixFormatter)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(format_other, 'foo')

  def testFormatterException(self):

    def _FormatterWithException(s: str) -> str:
      raise converter_types.StrFormatterError

    format_self = converter_types.FormattedStrType(
        'foo', formatter_self=_FormatterWithException)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertNotEqual(format_self, 'foo')

    format_other = converter_types.FormattedStrType(
        'foo', formatter_other=_FormatterWithException)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertNotEqual(format_other, 'foo')

  def testCallable(self):

    def _PrefixFormatter(s: str) -> str:
      return f'(prefix){s}'

    callable_self = converter_types.FormattedStrType.CreateInstanceFactory(
        formatter_self=_PrefixFormatter)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(callable_self('foo'), '(prefix)foo')

    callable_other = converter_types.FormattedStrType.CreateInstanceFactory(
        formatter_other=_PrefixFormatter)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(callable_other('(prefix)foo'), 'foo')


class FormattedRegexStrTypeTest(unittest.TestCase):

  def testNoFormatter(self):
    not_formatted = converter_types.FormattedRegexStrType('not_formatted[0-8]')
    for i in range(9):
      self.assertEqual(not_formatted, f'not_formatted{i}')
    self.assertNotEqual(not_formatted, 'not_formatted9')

  def testFormatted(self):

    def _PrefixRegexFormatter(s: str) -> str:
      return f'[0-9]{s}'

    def _PrefixNumberFormatter(s: str) -> str:
      return f'5{s}'

    format_self = converter_types.FormattedRegexStrType(
        'foo', formatter_self=_PrefixRegexFormatter)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(format_self, '5foo')

    format_other = converter_types.FormattedRegexStrType(
        '[0-9]foo', formatter_other=_PrefixNumberFormatter)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(format_other, 'foo')

  def testFormatterException(self):

    def _FormatterWithException(s: str) -> str:
      raise converter_types.StrFormatterError

    format_self = converter_types.FormattedRegexStrType(
        'foo', formatter_self=_FormatterWithException)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertNotEqual(format_self, 'foo')

    format_other = converter_types.FormattedRegexStrType(
        'foo', formatter_other=_FormatterWithException)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertNotEqual(format_other, 'foo')

  def testCallable(self):

    def _PrefixRegexFormatter(s: str) -> str:
      return f'[0-9]{s}'

    def _PrefixNumberFormatter(s: str) -> str:
      return f'5{s}'

    callable_self = converter_types.FormattedRegexStrType.CreateInstanceFactory(
        formatter_self=_PrefixRegexFormatter)  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(callable_self('foo'), '5foo')

    callable_other = (
        converter_types.FormattedRegexStrType.CreateInstanceFactory(
            formatter_other=_PrefixNumberFormatter))  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(callable_other('[0-9]foo'), 'foo')


if __name__ == '__main__':
  unittest.main()
