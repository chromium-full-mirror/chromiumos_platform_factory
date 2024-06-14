# Copyright 2019 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Verify and close modem access authority.

Description
-----------
This test verifies the modem access level. If the access level is not 0,
this test will try to set it to 0.

Internal references
-------------------

- b/120004153#comment23

Test Procedure
--------------
This is an automatic test that doesn't need any user interaction.

1. Verify the access level of modem is 0. Pass the test if so.
2. Set the access level to 0.
3. Verify the access level of modem is 0. Pass the test if so.

Dependency
----------
- `modem`

Examples
--------
To verify and set modem access level to 0:

.. test_list::

  generic_cellular_examples:CellularTests.ModemSecurity

"""

import logging
import re

from cros.factory.device import device_utils
from cros.factory.test import test_case


ACCESS_LEVEL_RE = re.compile('^access_level = [0-9]', re.MULTILINE)
RESPONSE_RE = re.compile('^response: \'(.*)\'$', re.DOTALL)


class ModemSecurity(test_case.TestCase):

  related_components = (test_case.TestCategory.WWAN, )
  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()

  def RunATCommand(self, command: str):
    response = self._dut.CheckOutput(
        ['mmcli', '-m', 'any', '--command', command], log=True)
    match = RESPONSE_RE.search(response)
    if not match:
      self.FailTask(f'Bad response: {response}')

    # yapf: disable
    return match.group(1)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def runTest(self):
    response = self._dut.CheckOutput(['mmcli', '-L'], log=True)
    if 'L850' not in response:
      logging.info('Modem is %r', response)
      self.WaiveTest('Modem is not L850 waived.')
    # Check whether access authority is closed already first.
    response = self.RunATCommand('AT@sec:status_info()')
    # yapf: disable
    if ACCESS_LEVEL_RE.search(response).group(0) == 'access_level = 0':  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      return

    # If access authority is still open then try to close it.
    self.RunATCommand('AT@sec:code_clear(0)')
    response = self.RunATCommand('AT@sec:status_info()')
    # yapf: disable
    if ACCESS_LEVEL_RE.search(response).group(0) != 'access_level = 0':  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # If we can't close the access authority then raise this failure.
      self.FailTask('Failed to set the access_level')
