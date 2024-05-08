#!/usr/bin/env python3
# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.gooftool import write_protect_target


class WriteProtectTargetUnittest(unittest.TestCase):

  def testCreateAvailableTargets(self):
    for target in write_protect_target.WriteProtectTargetType:
      write_protect_target.CreateWriteProtectTarget(target)

  def testCreateTargetWithWrongType(self):
    with self.assertRaises(TypeError):
      # yapf: disable
      write_protect_target.CreateWriteProtectTarget('inexistent_type')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable


if __name__ == '__main__':
  unittest.main()
