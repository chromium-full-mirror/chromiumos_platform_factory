#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
# pylint: disable=protected-access

import logging
import unittest
from unittest import mock

from cros.factory.device import device_utils
from cros.factory.goofy import invocation
from cros.factory.test import state
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test.fixture import bft_fixture
from cros.factory.test.i18n import _
from cros.factory.test.pytests import summary
from cros.factory.test.test_lists import manager
from cros.factory.utils import type_utils


MOCK_TEST_LIST = manager.BuildTestListForUnittest({
    'tests': [{
        'id':
            'Root',
        'subtests': [
            {
                'id': 'Test1',
                'pytest_name': 'test_1'
            },
            {
                'id': 'Test2',
                'pytest_name': 'test_2'
            },
            {
                'id':
                    'TestGroup',
                'subtests': [{
                    'id': 'Test3',
                    'pytest_name': 'test_3'
                }, {
                    'id': 'Test4',
                    'pytest_name': 'test_4'
                }, {
                    'id': 'Test5',
                    'pytest_name': 'test_5'
                }, {
                    'id': 'Summary',
                    'pytest_name': 'summary'
                }]
            },
        ]
    }]
})
TEST_INFO_PATH = 'test:Root.TestGroup.Summary'


class FakeArgs:

  def __init__(self, **kwargs):
    self.prompt_message: str = _('Click or press SPACE to continue')
    self.disable_input_on_fail: bool = False
    self.pass_without_prompt: bool = False
    self.bft_fixture: dict = None
    self.accessibility: bool = False
    self.include_parents: bool = False
    self.run_factory_external_name: str = None
    self.screensaver_timeout: int = None

    for k, v in kwargs.items():
      setattr(self, k, v)


class SummaryUnitTest(unittest.TestCase):

  def setUp(self):
    # Disable root logger to avoid redundant logs from other module.
    logging.getLogger().disabled = True

    self.test = summary.Report()
    self.ui = mock.create_autospec(test_ui.StandardUI)
    type_utils.LazyProperty.Override(self.test, 'ui', self.ui)
    self.mock_frontend_proxy = self.ui.InitJSTestObject.return_value

    self.test.test_info = mock.create_autospec(invocation.PytestInfo)
    self.test.test_info.ReadTestList.return_value = MOCK_TEST_LIST
    self.test.test_info.path = TEST_INFO_PATH

    patcher = mock.patch.object(device_utils, 'CreateDUTInterface',
                                autospec=True)
    self.mock_dut = patcher.start().return_value
    patcher = mock.patch.object(state, 'GetInstance', autospec=True)
    self.mock_goofy = patcher.start().return_value
    patcher = mock.patch.object(type_utils, 'Obj', autospec=True)
    self.mock_obj = patcher.start()
    self.mock_obj.return_value.status = None
    patcher = mock.patch.object(state.TestState, 'OverallStatus', autospec=True,
                                return_value=state.TestState.PASSED)
    self.mock_overall_status = patcher.start()
    patcher = mock.patch.object(test_case.TestCase, 'WaitTaskEnd',
                                autospec=True)
    self.mock_wait_task_end = patcher.start()
    self.addCleanup(mock.patch.stopall)

    self.test.args = FakeArgs()

  def test_setUp_InitFrontendProxy(self):
    # Turn on the screensaver after 5 seconds.
    self.test.args = FakeArgs(screensaver_timeout=5)
    self.test.setUp()

    # Disable the screensaver.
    self.test.args = FakeArgs(screensaver_timeout=None)
    self.test.setUp()

    self.ui.InitJSTestObject.assert_has_calls([
        mock.call('SummaryTest', 5),
        mock.call('SummaryTest', None),
    ])

  def test_setUp_TimeoutShouldNotBeZero(self):
    self.test.args = FakeArgs(screensaver_timeout=0)
    with self.assertRaisesRegex(
        AssertionError, r"False is not true : "
        r"Timeout for screensaver should be positive\."):
      self.test.setUp()

  def test_GetTestResults_IncludeParent(self):
    mock_test_list = MOCK_TEST_LIST
    mock_test = mock_test_list.LookupPath(TEST_INFO_PATH)
    mock_state = mock.Mock()
    mock_state.get.return_value.status = 'fake_status_from_state'
    self.test.args = FakeArgs(include_parents=True)

    self.test.setUp()
    test_results = self.test._GetTestResults(mock_test, mock_state)

    self.mock_obj.assert_has_calls([
        mock.call(path='test:Root.Test1', label={'en-US': 'Test 1'},
                  status='fake_status_from_state'),
        mock.call(path='test:Root.Test2', label={'en-US': 'Test 2'},
                  status='fake_status_from_state'),
        mock.call(path='test:Root.TestGroup.Test3', label={'en-US': 'Test 3'},
                  status='fake_status_from_state'),
        mock.call(path='test:Root.TestGroup.Test4', label={'en-US': 'Test 4'},
                  status='fake_status_from_state'),
        mock.call(path='test:Root.TestGroup.Test5', label={'en-US': 'Test 5'},
                  status='fake_status_from_state')
    ])
    self.assertEqual(test_results, [self.mock_obj.return_value] * 5)

  def test_GetTestResults_NotIncludeParent(self):
    mock_test_list = MOCK_TEST_LIST
    mock_test = mock_test_list.LookupPath(TEST_INFO_PATH)
    mock_state = mock.Mock()
    mock_state.get.return_value.status = 'fake_status_from_state'
    self.test.args = FakeArgs(include_parents=False)

    self.test.setUp()
    test_results = self.test._GetTestResults(mock_test, mock_state)

    self.mock_obj.assert_has_calls([
        mock.call(path='test:Root.TestGroup.Test3', label={'en-US': 'Test 3'},
                  status='fake_status_from_state'),
        mock.call(path='test:Root.TestGroup.Test4', label={'en-US': 'Test 4'},
                  status='fake_status_from_state'),
        mock.call(path='test:Root.TestGroup.Test5', label={'en-US': 'Test 5'},
                  status='fake_status_from_state')
    ])
    self.assertEqual(test_results, [self.mock_obj.return_value] * 3)

  @mock.patch.object(summary.Report, '_GetTestResults', autospec=True)
  @mock.patch.object(summary.Report, '_ShowTestInfoAtFrontend', autospec=True)
  def test_GetTestResults_InteractWithOtherFunction(self, mock_show_test_info,
                                                    mock_get_test_results):
    self.test.setUp()
    self.test.runTest()

    self.assertEqual(mock_show_test_info.call_args.args[3],
                     mock_get_test_results.return_value)

  @mock.patch.object(summary.Report, '_GetTestResults', autospec=True)
  @mock.patch.object(summary.Report, '_ShowTestInfoAtFrontend', autospec=True)
  def test_runTest_GetOverallStatus(self, mock_show_test_info,
                                    mock_get_test_results):
    self.mock_overall_status.return_value = 'fake_status'
    mock_result = mock.Mock()
    mock_get_test_results.return_value = [mock_result] * 3

    self.test.setUp()
    with self.assertLogs(level='INFO') as log:
      logging.getLogger().disabled = False
      self.test.runTest()
      logging.getLogger().disabled = True
      self.assertTrue(
          any("overall_status='fake_status'" in msg for msg in log.output))

    self.mock_overall_status.assert_called_once_with([mock_result.status] * 3)
    self.assertEqual(mock_show_test_info.call_args.args[2], 'fake_status')

  @mock.patch.object(bft_fixture, 'CreateBFTFixture', autospec=True)
  def test_SetFixtureStatusLight(self, mock_create_fixture):
    fake_bit_fixture = {
        'class_name': 'fake_name',
        'params': {}
    }
    self.test.args = FakeArgs(bft_fixture=fake_bit_fixture)
    mock_fixture = mock_create_fixture.return_value

    # All tests passed.
    self.test.setUp()
    self.test._SetFixtureStatusLight(all_pass=True)

    # Some tests failed.
    self.test.setUp()
    self.test._SetFixtureStatusLight(all_pass=False)

    mock_create_fixture.assert_has_calls(
        [mock.call(**fake_bit_fixture),
         mock.call(**fake_bit_fixture)], any_order=True)
    mock_fixture.SetStatusColor.assert_has_calls([
        mock.call(mock_fixture.StatusColor.GREEN),
        mock.call(mock_fixture.StatusColor.RED)
    ])
    assert mock_fixture.Disconnect.call_count == 2

  @mock.patch.object(bft_fixture, 'CreateBFTFixture', autospec=True)
  def test_SetFixtureStatusLight_Fail(self, mock_create_fixture):
    self.test.args = FakeArgs(bft_fixture={
        'class_name': 'fake_name',
        'params': {}
    })
    mock_fixture = mock_create_fixture.return_value
    mock_fixture.SetStatusColor.side_effect = bft_fixture.BFTFixtureException

    self.test.setUp()
    with self.assertLogs(level='ERROR') as log:
      logging.getLogger().disabled = False
      self.test._SetFixtureStatusLight(all_pass=True)
      logging.getLogger().disabled = True
      self.assertTrue(
          'Unable to set status color on BFT fixture' in log.output[0])

  @mock.patch.object(summary.Report, '_SetFixtureStatusLight', autospec=True)
  def test_runTest_SetFixtureStatusLightWhenBFTFixtureIsSet(
      self, mock_set_fixture_status_light):
    self.test.args = FakeArgs(bft_fixture={
        'class_name': 'fake_name',
        'params': {}
    })

    self.test.setUp()
    self.test.runTest()

    mock_set_fixture_status_light.assert_called_once()

  def test_WriteResultFile_GetFilePath(self):
    self.test.args = FakeArgs(run_factory_external_name='fake_result_file')

    self.test.setUp()
    self.test._WriteResultFile(all_pass=True, test_results=[])

    self.mock_dut.CheckCall.assert_called_once_with(
        ['mkdir', '-p', '/run/factory/external'])
    self.mock_dut.path.join.assert_called_once_with('/run/factory/external',
                                                    'fake_result_file')
    self.assertEqual(self.mock_dut.WriteFile.call_args.args[0],
                     self.mock_dut.path.join.return_value)

  def test_WriteResultFile_TestPass(self):
    self.test.args = FakeArgs(run_factory_external_name='fake_result_file')

    self.test.setUp()
    self.test._WriteResultFile(all_pass=True, test_results=[])

    self.mock_dut.WriteFile.assert_called_once_with(
        self.mock_dut.path.join.return_value, 'PASS')

  def test_WriteResultFile_TestFail(self):
    self.test.args = FakeArgs(run_factory_external_name='fake_result_file')

    self.test.setUp()
    self.test._WriteResultFile(
        all_pass=False,
        test_results=[mock.Mock(path='fake_path', status='fake_status')])

    self.mock_dut.WriteFile.assert_called_once_with(
        self.mock_dut.path.join.return_value, 'fake_path: fake_status\n')

  @mock.patch.object(summary.Report, '_WriteResultFile', autospec=True)
  def test_runTest_WriteResultFileWhenExternalNameIsSet(self,
                                                        mock_write_result_file):
    self.test.args = FakeArgs(run_factory_external_name='fake_result_file')

    self.test.setUp()
    self.test.runTest()

    mock_write_result_file.assert_called_once()

  def test_runTest_FinishTestWhenAllTestsPassAndWithoutPrompt(self):
    self.test.args = FakeArgs(pass_without_prompt=True)
    self.mock_overall_status.return_value = state.TestState.PASSED

    self.test.setUp()
    self.test.runTest()

    self.mock_frontend_proxy.SetPromptMessage.assert_not_called()

  def test_PromptMessage_TestsPass(self):
    self.test.args = FakeArgs(pass_without_prompt=False, prompt_message='msg')

    self.test.setUp()
    self.test._PromptMessage(all_pass=True)

    self.mock_frontend_proxy.SetPromptMessage.assert_called_once_with(
        'msg', True)

  def test_PromptMessage_TestsFailAndEnableInputOnFail(self):
    self.test.args = FakeArgs(prompt_message='msg', disable_input_on_fail=False)

    self.test.setUp()
    self.test._PromptMessage(all_pass=False)

    self.mock_frontend_proxy.SetPromptMessage.assert_called_once_with(
        'msg', True)

  def test_PromptMessage_TestsFailAndDisableInputOnFail(self):
    self.test.args = FakeArgs(disable_input_on_fail=True)
    self.test.setUp()

    self.test._PromptMessage(all_pass=False)

    self.mock_frontend_proxy.SetPromptMessage.assert_called_once_with(
        _('Unable to proceed, since some previous tests have not passed.'),
        False)

  def test_ShowTestInfoAtFrontend(self):
    mock_test = mock.Mock()
    fake_status = 'fake status'
    fake_results = ['fake results']

    self.test.setUp()
    self.test._ShowTestInfoAtFrontend(mock_test, fake_status, fake_results)

    self.mock_frontend_proxy.SetTestName.assert_called_once_with(
        mock_test.parent.path)
    self.mock_frontend_proxy.SetOverallTestStatus.assert_called_once_with(
        fake_status)
    self.mock_frontend_proxy.SetDetailTestResults.assert_called_once_with(
        fake_results)

  def test_BindUiKeys_EnableInputOnFail(self):
    self.test.args = FakeArgs(disable_input_on_fail=False)

    self.test.setUp()
    self.test._BindUiKeys(all_pass=False)

    self.ui.BindStandardKeys.assert_called_once()

  def test_BindUiKeys_TestPassAndDisableInput(self):
    self.test.args = FakeArgs(disable_input_on_fail=True)

    self.test.setUp()
    self.test._BindUiKeys(all_pass=True)

    self.ui.BindStandardPassKeys.assert_called_once()

  def test_BindUiKeys_TestFailAndDisableInput(self):
    self.test.args = FakeArgs(disable_input_on_fail=True)

    self.test.setUp()
    self.test._BindUiKeys(all_pass=False)

    self.ui.BindStandardKeys.assert_not_called()
    self.ui.BindStandardPassKeys.assert_not_called()

  def test_runTest_OverallStatusInPassedState(self):
    self.test.args = FakeArgs(
        bft_fixture={
            'class_name': 'fake_name',
            'params': {}
        }, accessibility=True, run_factory_external_name='fake_file')
    self.mock_overall_status.return_value = state.TestState.PASSED

    with mock.patch.multiple(
        self.test,
        autospec=True,
        _SetFixtureStatusLight=mock.DEFAULT,
        _WriteResultFile=mock.DEFAULT,
        _PromptMessage=mock.DEFAULT,
        _BindUiKeys=mock.DEFAULT,
    ) as mock_methods:
      self.test.setUp()
      self.test.runTest()

      self.assertEqual(self.mock_goofy.PostHookEvent.call_args.args[1], 'Good')
      mock_methods['_SetFixtureStatusLight'].assert_called_once_with(True)
      self.assertEqual(mock_methods['_WriteResultFile'].call_args.args[0], True)
      mock_methods['_PromptMessage'].assert_called_once_with(True)
      mock_methods['_BindUiKeys'].assert_called_once_with(True)
      self.mock_frontend_proxy.EnableAccessibility.assert_not_called()

  def test_runTest_OverallStatusNotInPassedState(self):
    self.test.args = FakeArgs(
        bft_fixture={
            'class_name': 'fake_name',
            'params': {}
        }, accessibility=True, run_factory_external_name='fake_file')
    self.mock_overall_status.return_value = state.TestState.FAILED

    with mock.patch.multiple(
        self.test,
        autospec=True,
        _SetFixtureStatusLight=mock.DEFAULT,
        _WriteResultFile=mock.DEFAULT,
        _PromptMessage=mock.DEFAULT,
        _BindUiKeys=mock.DEFAULT,
    ) as mock_methods:
      self.test.setUp()
      self.test.runTest()

      self.assertEqual(self.mock_goofy.PostHookEvent.call_args.args[1], 'Bad')
      mock_methods['_SetFixtureStatusLight'].assert_called_once_with(False)
      self.assertEqual(mock_methods['_WriteResultFile'].call_args.args[0],
                       False)
      mock_methods['_PromptMessage'].assert_called_once_with(False)
      mock_methods['_BindUiKeys'].assert_called_once_with(False)
      self.mock_frontend_proxy.EnableAccessibility.assert_called_once()


if __name__ == '__main__':
  unittest.main()
