#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.hwid.v3.avl import builder


class BuilderTest(unittest.TestCase):

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


if __name__ == '__main__':
  unittest.main()
