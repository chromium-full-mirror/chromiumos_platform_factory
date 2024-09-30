# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A generic interface to control the BFT fixture."""

import logging
import time
import unittest
from typing import Tuple, Dict, List, Optional, Any

from cros.factory.test import test_tags
from cros.factory.test.fixture import bft_fixture
from cros.factory.utils.arg_utils import Arg


class BFTFixtureArgs:
  bft_fixture: Dict[str, Any]
  method: str
  args: List
  retry_secs: Optional[float]


class BFTFixture(unittest.TestCase):
  related_components: Tuple[test_tags.TestCategory, ...] = tuple()
  ARGS = [
      Arg('bft_fixture', dict, bft_fixture.TEST_ARG_HELP),
      Arg('method', str, 'BFTFixture method to call.'),
      Arg('args', list, 'args of the method.', default=[]),
      Arg('retry_secs', (int, float),
          'retry interval in seconds (or None for no retry)',
          default=None),
  ]
  args: BFTFixtureArgs

  def runTest(self):
    while True:
      fixture = None
      try:
        fixture = bft_fixture.CreateBFTFixture(**self.args.bft_fixture)
        getattr(fixture, self.args.method)(*self.args.args)
        break  # Success; we're done
      except Exception:
        logging.exception('BFT fixture test failed')
        if not self.args.retry_secs:
          # No retry; raise the exception to fail the test
          raise
      finally:
        if fixture:
          try:
            fixture.Disconnect()
          except Exception:
            logging.exception('Unable to disconnect fixture')

      logging.info('Will retry in %s secs', self.args.retry_secs)
      time.sleep(self.args.retry_secs)
