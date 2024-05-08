# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""An no-op test.

Description
-----------
This test does nothing but waits for a given period of time.

The length of time is given in `wait_secs`.

Test Procedure
--------------
No user interaction is required, the test waits `wait_secs` seconds and pass.

Dependency
----------
None.

Examples
--------
To wait for 5 seconds, add this in test list::

  {
    "pytest_name": "nop",
    "args": {
      "wait_secs": 5
    }
  }
"""

import time
import unittest

from cros.factory.utils.arg_utils import Arg


class NopTest(unittest.TestCase):
  # yapf: disable
  related_components = tuple()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  ARGS = [
      Arg('wait_secs', (int, float), 'Wait for N seconds.', default=0)]

  def runTest(self):
    # yapf: disable
    if self.args.wait_secs:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      time.sleep(self.args.wait_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
