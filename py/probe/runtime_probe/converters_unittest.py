#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.probe.runtime_probe import converters


class ConverterTest(unittest.TestCase):

  def testNopConverter(self):
    converter = converters.NopConverter()
    self.assertEqual('abc', converter.Parse('abc'))
    self.assertEqual('abc', converter.Format('abc'))

  def testIntegerConverter(self):
    converter = converters.IntegerConverter()
    self.assertEqual(123, converter.Parse('123'))
    self.assertEqual('123', converter.Format(123))

    self.assertIsNone(converter.Parse('abc'))

  def testHexConverter(self):
    converter = converters.HexConverter()
    expected = converters.ConvertedHex('0x12ab')
    self.assertEqual(expected, converter.Parse('0x12ab'))
    self.assertEqual(expected, converter.Parse('0x12AB'))
    self.assertEqual(expected, converter.Parse('12ab'))
    self.assertEqual(expected, converter.Parse('12AB'))

    self.assertEqual('0x12ab', converter.Format(expected))

    self.assertIsNone(converter.Parse('xyz'))

  def testHexConverterFormat(self):
    value = converters.ConvertedHex('0x12ab')
    with self.subTest():
      self.assertEqual(converters.HexConverter().Format(value), '0x12ab')
    with self.subTest('NoPrefix'):
      self.assertEqual(
          converters.HexConverter(prefix=False).Format(value), '12ab')
    with self.subTest('Padding'):
      self.assertEqual(
          converters.HexConverter(padding_size=6).Format(value), '0x0012ab')
    with self.subTest('NoPrefix_Padding'):
      self.assertEqual(
          converters.HexConverter(prefix=False, padding_size=6).Format(value),
          '0012ab')

  def testReConverter(self):
    converter = converters.REConverter()
    expected = converters.ConvertedRE('.*')
    self.assertIsNotNone(converter.Parse('.*'))

    self.assertEqual('.*', converter.Format(expected))

    self.assertIsNone(converter.Parse('('))


if __name__ == '__main__':
  unittest.main()
