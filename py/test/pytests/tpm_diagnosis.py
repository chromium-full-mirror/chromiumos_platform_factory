# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Runs tpm_selftest to perform TPM self-diagnosis.

Description
-----------
This test stopped working after the tpm_selftest being removed.

Internal references
^^^^^^^^^^^^^^^^^^^
- b/35577239

Test Procedure
--------------
This is an automatic test that doesn't need any user interaction.

Dependency
----------
- /usr/local/sbin/tpm_selftest

Examples
--------
An example::

  {
    "pytest_name": "tpm_diagnosis"
  }

"""

import os
import threading

from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.utils.arg_utils import Arg


class TpmDiagnosisTest(test_case.TestCase):
  related_components = (
      test_case.TestCategory.SECURE_ELEMENT,
      test_case.TestCategory.TPM,
  )
  ARGS = [
      Arg('tpm_selftest', str, 'Path of tpm_selftest program.',
          default='/usr/local/sbin/tpm_selftest'),
      Arg('tpm_args', list, 'List of tpm_selftest args.',
          default=['-l', 'debug']),
      Arg('success_pattern', str, 'Pattern of success.',
          default='tpm_selftest succeeded')
  ]

  ui_class = test_ui.ScrollableLogUI

  def setUp(self):
    self.assertTrue(
        # yapf: disable
        os.path.isfile(self.args.tpm_selftest),  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        msg=f'{self.args.tpm_selftest} is missing.')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def runTest(self):
    """Runs tpm_selftest.

    It shows diagnosis result on factory UI.
    """
    success = threading.Event()
    def _Callback(line):
      # yapf: disable
      if self.args.success_pattern in line:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        success.set()

    # yapf: disable
    returncode = self.ui.PipeProcessOutputToUI(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        [self.args.tpm_selftest] + self.args.tpm_args, callback=_Callback)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertTrue(
        success.is_set(),
        # yapf: disable
        f'TPM self-diagnose failed: Cannot find a success pattern: '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        f'"{self.args.success_pattern}". tpm_selftest returncode: '
        f'{int(returncode)}.')
