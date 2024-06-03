#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


class AudioCodecTest(unittest.TestCase):

  def testAuidoCodec(self):
    probe_info = v3_rule.AVLProbeInfo(
        'audio_codec.audio_codec',
        collections.OrderedDict([('name', ['name_1', 'name_2'])]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)

    assert m is not None
    self.assertEqual(
        m.Match({
            'name': 'name_1'
        }), matcher.MatchResult(True, 'AuidoCodecFullLengthMatch'))
    self.assertEqual(
        m.Match({
            'name': 'name_2'
        }), matcher.MatchResult(True, 'AuidoCodecFullLengthMatch'))
    self.assertEqual(
        m.Match({
            'name': 'name_3'
        }), matcher.MatchResult(False, 'AuidoCodecFullLengthMatch'))

    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': ['name', 'name_1'],
                'operator': 'STRING_EQUAL'
            }, {
                'operand': ['name', 'name_2'],
                'operator': 'STRING_EQUAL'
            }],
            'operator': 'OR'
        })


if __name__ == '__main__':
  unittest.main()
