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
from typing import Tuple, Union
import unittest

from cros.factory.test import test_tags
from cros.factory.utils.arg_utils import Arg


class NopTestArgs:
  wait_secs: Union[int, float]


class NopTest(unittest.TestCase):
  related_components: Tuple[test_tags.TestCategory, ...] = ()
  ARGS = [Arg('wait_secs', (int, float), 'Wait for N seconds.', default=0)]
  args: NopTestArgs

  def runTest(self):
    if self.args.wait_secs:
      time.sleep(self.args.wait_secs)
