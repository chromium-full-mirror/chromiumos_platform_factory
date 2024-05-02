# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Displays a status summary for all tests in the current section.

Description
-----------
This is a test to display a summary of test results in same test group.
The summary includes tests up to, but not including, this test itself.

For example, if the test tree is::

 SMT
   ...
 Runin
   A
   B
   C
   report (this test)
   shutdown

Then this test will show the status summary for A, B, and C. No shutdown.

This test is often used as a "barrier" or "check point" when the argument
``disable_input_on_fail`` is set, since operators can't skip to next test item
when the overall status is not PASSED.

Moreover, if argument ``pass_without_prompt`` is ``True``, the test will pass
silently and move to next test item without user interaction. This is usually
known as "Barrier" mode. Otherwise, it'll prompt the given message and wait for
input, which is known as "Check Point" mode.

Test Procedure
--------------
1. If all previous tests in same group are passed, this test will display
   nothing and simply pass when argument ``pass_without_prompt`` is True,
   otherwise display a table of test names and results, prompt the given (or
   default) message and wait for input to pass or fail.
2. Otherwise, if any previous tests in same group failed, a table listing test
   names and results will be displayed. Depends on argument
   ``disable_input_on_fail``, operator may choose to continue or will stay in
   failure screen.

Dependency
----------
None.

Examples
--------
To list previous tests in same group, and always prompt and wait for input to
decide if we can move on, add this in test list::

  {
    "pytest_name": "summary"
  }

To only stop when any previous tests in same group has failed ("Barrier")::

  {
    "pytest_name": "summary",
    "allow_reboot": true,
    "disable_abort": true,
    "args": {
      "disable_input_on_fail": true,
      "pass_without_prompt": true
    }
  }

To always prompt but only pass if all previous tests in same group passed
("Check Point")::

  {
    "pytest_name": "summary",
    "allow_reboot": true,
    "disable_abort": true,
    "args": {
      "prompt_message": "i18n! Press space to shutdown.",
      "disable_input_on_fail": true,
      "pass_without_prompt": false
    }
  }
"""

import itertools
import logging

from cros.factory.device import device_utils
from cros.factory.test.fixture import bft_fixture
from cros.factory.test.i18n import _
from cros.factory.test.i18n import arg_utils as i18n_arg_utils
from cros.factory.test import state
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import type_utils


_EXTERNAL_DIR = '/run/factory/external'

# The following test states are considered passed
_EXTENED_PASSED_STATE = {
    state.TestState.PASSED,
    state.TestState.FAILED_AND_WAIVED,
    state.TestState.SKIPPED, }


class Report(test_case.TestCase):
  """A factory test to report test status."""
  related_components = tuple()

  ARGS = [
      i18n_arg_utils.I18nArg(
          'prompt_message', 'Prompt message in HTML when all tests passed',
          default=_('Click or press SPACE to continue')),
      Arg('disable_input_on_fail', bool,
          ('Disable user input to pass/fail when the overall status is not '
           'PASSED'),
          default=False),
      Arg('pass_without_prompt', bool,
          'If all tests passed, pass this test without prompting',
          default=False),
      Arg('bft_fixture', dict,
          ('BFT fixture arguments (see bft_fixture test).  If provided, then a '
           'red/green light is lit to indicate failure/success rather than '
           'showing the summary on-screen.  The test does not fail if unable '
           'to connect to the BFT fixture.'),
          default=None),
      Arg('accessibility', bool,
          'Display bright red background when the overall status is not PASSED',
          default=False),
      Arg('include_parents', bool,
          'Recursively include parent groups in summary',
          default=False),
      Arg('run_factory_external_name', str,
          'Notify DUT that external test is over, will use DUT interface to '
          'write result file under /run/factory/external/<NAME>.',
          default=None),
      Arg('screensaver_timeout', int,
          'Timeout in seconds to turn on the screensaver, set to ``None`` to '
          'disable the screensaver.',
          default=None)
  ]

  def setUp(self):
    self.assertTrue(
        self.args.screensaver_timeout is None or  # type: ignore #TODO(b/338318729) Fixit!
        self.args.screensaver_timeout >= 1,  # type: ignore #TODO(b/338318729) Fixit!
        "Timeout for screensaver should be positive.")

    self.dut = device_utils.CreateDUTInterface()
    self._frontend_proxy = self.ui.InitJSTestObject(  # type: ignore #TODO(b/338318729) Fixit!
        'SummaryTest', self.args.screensaver_timeout)  # type: ignore #TODO(b/338318729) Fixit!
    self.goofy = state.GetInstance()

  def _GetTestResults(self, test, states):
    previous_tests = []  # type: ignore #TODO(b/338318729) Fixit!
    current = test
    root = test.root if self.args.include_parents else test.parent  # type: ignore #TODO(b/338318729) Fixit!

    while current != root:
      previous_tests = list(itertools.takewhile(
          lambda t: t != current, current.parent.subtests)) + previous_tests
      current = current.parent

    test_results = [
        type_utils.Obj(path=t.path, label=t.label,
                       status=states.get(t.path).status) for t in previous_tests
    ]
    return test_results

  def _SetFixtureStatusLight(self, all_pass):
    try:
      fixture = bft_fixture.CreateBFTFixture(**self.args.bft_fixture)  # type: ignore #TODO(b/338318729) Fixit!
      fixture.SetStatusColor(
          fixture.StatusColor.GREEN if all_pass else fixture.StatusColor.RED)
      fixture.Disconnect()
    except bft_fixture.BFTFixtureException:
      logging.exception('Unable to set status color on BFT fixture')

  def _WriteResultFile(self, all_pass, test_results):
    self.dut.CheckCall(['mkdir', '-p', _EXTERNAL_DIR])
    file_path = self.dut.path.join(_EXTERNAL_DIR,
                                   self.args.run_factory_external_name)  # type: ignore #TODO(b/338318729) Fixit!
    if all_pass:
      self.dut.WriteFile(file_path, 'PASS')
    else:
      report = ''.join(f'{r.path}: {r.status}\n' for r in test_results)
      self.dut.WriteFile(file_path, report)

  def _PromptMessage(self, all_pass):
    if not self.args.disable_input_on_fail or all_pass:  # type: ignore #TODO(b/338318729) Fixit!
      self._frontend_proxy.SetPromptMessage(self.args.prompt_message, True)  # type: ignore #TODO(b/338318729) Fixit!
    else:
      self._frontend_proxy.SetPromptMessage(
          _('Unable to proceed, since some previous tests have not passed.'),
          False)

  def _ShowTestInfoAtFrontend(self, test, overall_status, test_results):
    self._frontend_proxy.SetTestName(test.parent.path)
    self._frontend_proxy.SetOverallTestStatus(overall_status)
    self._frontend_proxy.SetDetailTestResults(test_results)

  def _BindUiKeys(self, all_pass):
    if not self.args.disable_input_on_fail:  # type: ignore #TODO(b/338318729) Fixit!
      self.ui.BindStandardKeys()  # type: ignore #TODO(b/338318729) Fixit!
    # If disable_input_on_fail is True, and overall status is PASSED, user
    # can only pass the test.
    elif all_pass:
      self.ui.BindStandardPassKeys()  # type: ignore #TODO(b/338318729) Fixit!

  def runTest(self):
    test_list = self.test_info.ReadTestList()  # type: ignore #TODO(b/338318729) Fixit!
    test = test_list.LookupPath(self.test_info.path)  # type: ignore #TODO(b/338318729) Fixit!
    states = state.GetInstance().GetTestStates()

    test_results = self._GetTestResults(test, states)
    overall_status = state.TestState.OverallStatus(
        [r.status for r in test_results])
    all_pass = overall_status in _EXTENED_PASSED_STATE
    self.goofy.PostHookEvent('Summary', 'Good' if all_pass else 'Bad')

    if self.args.bft_fixture:  # type: ignore #TODO(b/338318729) Fixit!
      self._SetFixtureStatusLight(all_pass)

    if self.args.run_factory_external_name:  # type: ignore #TODO(b/338318729) Fixit!
      self._WriteResultFile(all_pass, test_results)

    if all_pass and self.args.pass_without_prompt:  # type: ignore #TODO(b/338318729) Fixit!
      return

    self._PromptMessage(all_pass)
    self._ShowTestInfoAtFrontend(test, overall_status, test_results)
    self._BindUiKeys(all_pass)

    if self.args.accessibility and not all_pass:  # type: ignore #TODO(b/338318729) Fixit!
      # Display red background at frontend when test fail.
      self._frontend_proxy.EnableAccessibility()
    logging.info('overall_status=%r', overall_status)

    self.WaitTaskEnd()
