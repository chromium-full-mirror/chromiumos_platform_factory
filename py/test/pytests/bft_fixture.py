# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A generic interface to control the BFT fixture."""

import logging
import time
import unittest

from cros.factory.test.fixture import bft_fixture
from cros.factory.utils.arg_utils import Arg


class BFTFixture(unittest.TestCase):
  # yapf: disable
  related_components = tuple()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  ARGS = [
      Arg('bft_fixture', dict, bft_fixture.TEST_ARG_HELP),
      Arg('method', str, 'BFTFixture method to call.'),
      Arg('args', list, 'args of the method.', default=[]),
      Arg('retry_secs', (int, float),
          'retry interval in seconds (or None for no retry)',
          default=None),
  ]

  def runTest(self):
    while True:
      fixture = None
      try:
        # yapf: disable
        fixture = bft_fixture.CreateBFTFixture(**self.args.bft_fixture)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        getattr(fixture, self.args.method)(*self.args.args)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        break  # Success; we're done
      except Exception:
        logging.exception('BFT fixture test failed')
        # yapf: disable
        if not self.args.retry_secs:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          # No retry; raise the exception to fail the test
          raise
      finally:
        if fixture:
          try:
            fixture.Disconnect()
          except Exception:
            logging.exception('Unable to disconnect fixture')

      # yapf: disable
      logging.info('Will retry in %s secs', self.args.retry_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      time.sleep(self.args.retry_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
