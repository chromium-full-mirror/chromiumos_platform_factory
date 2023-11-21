#!/usr/bin/env python3
# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unit tests for cros_board_utils module."""

import unittest

from cros.factory.utils.cros_board_utils import BuildBoard


class BuildBoardTest(unittest.TestCase):
  """Unit tests for BuildBoard class."""

  def testBuildBoard_ReplaceUnderscoreWithDash_FullNameIsTheSame(self):
    expected_output = {
        'base': 'veyron',
        'variant': 'mickey',
        'full_name': 'veyron_mickey',
        'short_name': 'mickey',
        'gsutil_name': 'veyron-mickey',
    }

    mickey = BuildBoard('veyron_mickey')
    mickey_dash = BuildBoard('veyron-mickey')

    self.assertDictContainsSubset(expected_output, mickey.__dict__)
    self.assertDictContainsSubset(expected_output, mickey_dash.__dict__)

  def testBuildBoard_NoVariant_Success(self):
    expected_output = {
        'base': 'hatch',
        'variant': None,
        'full_name': 'hatch',
        'short_name': 'hatch',
        'gsutil_name': 'hatch',
    }

    hatch = BuildBoard('hatch')

    self.assertDictContainsSubset(expected_output, hatch.__dict__)


if __name__ == '__main__':
  unittest.main()
