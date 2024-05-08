#!/usr/bin/env python3

# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.test.test_lists import manager_unittest
from cros.factory.tools import test_list_insight


class TestListInsightManagerTest(unittest.TestCase):

  def setUp(self):
    # Use example test lists in the manager_unittest dir
    # yapf: disable
    manager_unittest.TestListLoaderTest.setUp(self)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.manager = test_list_insight.TestListInsightManager(loader=self.loader)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def tearDown(self):
    # yapf: disable
    manager_unittest.TestListLoaderTest.tearDown(self)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def testFindTarget(self):
    factory_test_objects = self.manager.FindTarget('halt', 'a')
    self.assertIn('"base; HaltStep": "halt"',
                  factory_test_objects['a:SMT.Halt'])


if __name__ == '__main__':
  unittest.main()
