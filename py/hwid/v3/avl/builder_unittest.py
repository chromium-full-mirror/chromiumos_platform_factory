#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import collections
from typing import ClassVar
import unittest

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class FakeSuggester(matcher.ISuggester):

  def __init__(self, key, value):
    self._key = key
    self._value = value

  def BuildSuggestion(self,
                      suggestion: runtime_probe_matchers.ProbeInfoSuggestion):
    return [
        matcher.ProbeInfoSuggestion(self._key, self._value, f'{suggestion!r}')
    ]


class FakeConverter(builder.IProbeInfoConverter):

  def __init__(self, field_name):
    self._field_name = field_name

  def Build(self, probe_info: v3_rule.AVLProbeInfo):
    if self._field_name not in probe_info.params:
      return None
    key = self._field_name
    value = probe_info.params[key][0]
    return (runtime_probe_matchers.StringEqualMatcher(
        key, value), FakeSuggester(key, value))


class FakeConverter1(FakeConverter):
  IDENTIFIER: ClassVar = 'FakeConverter1'
  LAST_SUPPORT_VERSIONS: ClassVar = builder.BranchesOSVersions(
      [builder.OSVersion.TOT])

  def __init__(self):
    super().__init__('field_1')


FAKECONVERTER2_LAST_SUPPORT_BUILD = 17500
FAKECONVERTER2_SUPPORTED_BRANCH = 'factory-board-17500.B'
FAKECONVERTER2_UNSUPPORTED_BRANCH = 'factory-board-17501.B'


class FakeConverter2(FakeConverter):
  IDENTIFIER = 'FakeConverter2'
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions(
      [builder.OSVersion(FAKECONVERTER2_LAST_SUPPORT_BUILD)])
  COMPONENT_STATUS = builder.AVLComponentStatus.UNQUALIFIED

  def __init__(self):
    super().__init__('field_2')


FAKE_MODEL = 'fake_model'
FAKE_CID = 123


class BuilderTest(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._builder = builder.Builder()
    self._builder.AddConverterSets(
        builder.ConverterSet(
            'probe_function_a',
            [FakeConverter1(), FakeConverter2()]))

  def testBuilderConverter1(self):
    matcher1 = self._builder.Build(
        v3_rule.AVLProbeInfo(
            'probe_function_a',
            collections.OrderedDict([('field_1', ['value_1'])])), FAKE_MODEL,
        None, FAKE_CID, 0, False)

    assert matcher1 is not None
    self.assertEqual(
        matcher.MatchResult(True, 'FakeConverter1'),
        matcher1.Match({
            'field_1': 'value_1'
        }))
    self.assertEqual(
        matcher.MatchResult(False, 'FakeConverter1'),
        matcher1.Match({
            'field_1': 'value_2'
        }))

  def testBuilderConverter2WithFactoryBranch(self):
    matcher2 = self._builder.Build(
        v3_rule.AVLProbeInfo(
            'probe_function_a',
            collections.OrderedDict([('field_2', ['value_2'])])), FAKE_MODEL,
        FAKECONVERTER2_SUPPORTED_BRANCH, FAKE_CID, 0, False)

    assert matcher2 is not None
    self.assertEqual(
        matcher.MatchResult(True, 'FakeConverter2'),
        matcher2.Match({
            'field_2': 'value_2'
        }))
    self.assertEqual(
        matcher.MatchResult(False, 'FakeConverter2'),
        matcher2.Match({
            'field_2': 'value_1'
        }))

  def testBuilderConverter2WithUnsupportedFactoryBranch(self):
    self.assertIsNone(
        self._builder.Build(
            v3_rule.AVLProbeInfo(
                'probe_function_a',
                collections.OrderedDict([('field_2', ['value_2'])])),
            FAKE_MODEL, FAKECONVERTER2_UNSUPPORTED_BRANCH, FAKE_CID, 0, False))
    # No factory branch fallback to TOT, which is also not supported.
    self.assertIsNone(
        self._builder.Build(
            v3_rule.AVLProbeInfo(
                'probe_function_a',
                collections.OrderedDict([('field_2', ['value_2'])])),
            FAKE_MODEL, None, FAKE_CID, 0, False))

  def testBuilderConverter2WithUnqualified(self):
    # An qualified component has qid of non 0.
    self.assertIsNone(
        self._builder.Build(
            v3_rule.AVLProbeInfo(
                'probe_function_a',
                collections.OrderedDict([('field_2', ['value_2'])])),
            FAKE_MODEL, FAKECONVERTER2_SUPPORTED_BRANCH, FAKE_CID, 1, False))

  def testBuilderNoProbeIdentifier(self):
    self.assertIsNone(
        self._builder.Build(
            v3_rule.AVLProbeInfo(
                'not_found_identifier',
                collections.OrderedDict([('field_1', ['value_1'])])),
            FAKE_MODEL, None, FAKE_CID, 0, False))

  def testBuilderAddDuplicateSetRaiseException(self):
    with self.assertRaises(ValueError):
      self._builder.AddConverterSets(
          builder.ConverterSet('probe_function_a', []))

  def testOSVersions(self):
    versions = builder.BranchesOSVersions([
        builder.OSVersion(17500),
        builder.OSVersion(17499, 10),
        builder.OSVersion(17498, 11),
    ])
    # Test TOT always greater
    self.assertTrue(versions < builder.OSVersion.TOT)
    self.assertTrue(versions <= builder.OSVersion.TOT)
    self.assertFalse(versions > builder.OSVersion.TOT)
    self.assertFalse(versions >= builder.OSVersion.TOT)
    self.assertFalse(versions == builder.OSVersion.TOT)

    # Test main branch OSVersion
    self.assertTrue(versions < builder.OSVersion(17501))
    self.assertFalse(versions < builder.OSVersion(17500))
    self.assertFalse(versions < builder.OSVersion(17499))

    self.assertTrue(versions <= builder.OSVersion(17501))
    self.assertTrue(versions <= builder.OSVersion(17500))
    self.assertFalse(versions <= builder.OSVersion(17499))

    self.assertFalse(versions > builder.OSVersion(17501))
    self.assertFalse(versions > builder.OSVersion(17500))
    self.assertTrue(versions > builder.OSVersion(17499))

    self.assertFalse(versions >= builder.OSVersion(17501))
    self.assertTrue(versions >= builder.OSVersion(17500))
    self.assertTrue(versions >= builder.OSVersion(17499))

    self.assertFalse(versions == builder.OSVersion(17501))
    self.assertTrue(versions == builder.OSVersion(17500))
    self.assertFalse(versions == builder.OSVersion(17499))

    # Test branch 17501.1 always greater because build version greater.
    self.assertTrue(versions < builder.OSVersion(17501, 1))
    self.assertTrue(versions <= builder.OSVersion(17501, 1))
    self.assertFalse(versions > builder.OSVersion(17501, 1))
    self.assertFalse(versions >= builder.OSVersion(17501, 1))
    self.assertFalse(versions == builder.OSVersion(17501, 1))

    # Test OSVersion on branch 17499.*
    self.assertTrue(versions < builder.OSVersion(17499, 11))
    self.assertFalse(versions < builder.OSVersion(17499, 10))
    self.assertFalse(versions < builder.OSVersion(17499, 9))

    self.assertTrue(versions <= builder.OSVersion(17499, 11))
    self.assertTrue(versions <= builder.OSVersion(17499, 10))
    self.assertFalse(versions <= builder.OSVersion(17499, 9))

    self.assertFalse(versions > builder.OSVersion(17499, 11))
    self.assertFalse(versions > builder.OSVersion(17499, 10))
    self.assertTrue(versions > builder.OSVersion(17499, 9))

    self.assertFalse(versions >= builder.OSVersion(17499, 11))
    self.assertTrue(versions >= builder.OSVersion(17499, 10))
    self.assertTrue(versions >= builder.OSVersion(17499, 9))

    self.assertFalse(versions == builder.OSVersion(17499, 11))
    self.assertTrue(versions == builder.OSVersion(17499, 10))
    self.assertFalse(versions == builder.OSVersion(17499, 9))

  def testOSVersionFactoryBranch(self):
    self.assertEqual(
        builder.OSVersion.FromFactoryBranch('factory-board-12345.B'),
        builder.OSVersion(12345))
    self.assertEqual(
        builder.OSVersion.FromFactoryBranch('factory-board-12345.67.B'),
        builder.OSVersion(12345, 67))

    self.assertRaises(ValueError, builder.OSVersion.FromFactoryBranch, '')
    self.assertRaises(ValueError, builder.OSVersion.FromFactoryBranch, 'null')


if __name__ == '__main__':
  unittest.main()
