#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import time
import unittest
from unittest import mock

from cros.factory.device import device_utils
from cros.factory.goofy.plugins import plugin_controller
from cros.factory.test import state
from cros.factory.test.pytests import stressapptest
from cros.factory.test.utils import stress_manager


class FakeArgs:

  def __init__(self, **kwargs):
    self.seconds: int = 60
    self.memory_ratio: float = 0.9
    self.free_memory_only: bool = True
    self.wait_secs: int = 0
    self.disk_thread: bool = True
    self.disk_thread_dir: str = None
    self.max_errors: int = stress_manager.DEFAULT_MAX_ERRORS
    self.num_threads: int = None
    self.taskset_args: list = None
    self.scaling_min_freq: int = None
    self.scaling_max_freq: int = None
    self.scaling_governor: int = None

    for k, v in kwargs.items():
      setattr(self, k, v)


class StressAppTestUnitTest(unittest.TestCase):

  def setUp(self):
    self.test = stressapptest.StressAppTest()

    patcher = mock.patch.object(device_utils, 'CreateDUTInterface',
                                autospec=True)
    self.mock_dut = patcher.start().return_value
    patcher = mock.patch.object(state, 'GetInstance', autospec=True)
    self.mock_goofy = patcher.start().return_value
    patcher = mock.patch.object(plugin_controller, 'GetPluginRPCProxy',
                                autospec=True)
    self.mock_get_plugin_rpc_proxy = patcher.start()
    self.mock_cpu_freq_manager = self.mock_get_plugin_rpc_proxy.return_value
    patcher = mock.patch.object(stress_manager, 'StressManager', autospec=True)
    self.mock_get_stress_manager = patcher.start()
    self.mock_stress_manager = self.mock_get_stress_manager.return_value

    self.addCleanup(mock.patch.stopall)

    self.test.args = FakeArgs()

  def test_setUp_GetCPUFreqManager(self):
    self.test.setUp()
    self.mock_get_plugin_rpc_proxy.assert_called_once_with('cpu_freq_manager')

  @mock.patch.object(time, 'sleep', autospec=True)
  def test_runTest_WaitBeforeTestStart(self, mock_sleep):
    self.test.args = FakeArgs(wait_secs=10)

    self.test.setUp()
    self.test.runTest()

    mock_sleep.assert_called_once_with(10)

  def test_runTest_SetCPUScalingFrequency(self):
    self.test.args = FakeArgs(scaling_min_freq=1000, scaling_max_freq=2000,
                              scaling_governor=1)

    self.test.setUp()
    self.test.runTest()

    self.mock_cpu_freq_manager.SetFrequency.assert_called_once_with({
        'scaling_min_freq': 1000,
        'scaling_max_freq': 2000,
        'scaling_governor': 1
    })

  def test_runTest_RunStressTest_Success(self):
    self.test.args = FakeArgs(seconds=10, memory_ratio=0.8,
                              free_memory_only=True, disk_thread=False,
                              disk_thread_dir='dir', max_errors=5,
                              num_threads=4, taskset_args=['arg1', 'arg2'])

    self.test.setUp()
    self.test.runTest()

    self.mock_get_stress_manager.assert_called_once_with(self.mock_dut)
    self.mock_stress_manager.Run.assert_called_once_with(
        duration_secs=10, memory_ratio=0.8, free_memory_only=True,
        disk_thread=False, disk_thread_dir='dir', max_errors=5, num_threads=4,
        taskset_args=['arg1', 'arg2'])
    self.mock_goofy.WaitForWebSocketUp.assert_called_once()
    self.mock_cpu_freq_manager.RestoreFrequency.assert_called_once()

  def test_runTest_RunStressTest_Fail(self):
    exception = stress_manager.StressManagerError
    self.mock_stress_manager.Run.side_effect = exception('fake error message')

    self.test.setUp()
    with self.assertRaises(exception), self.assertLogs(level='ERROR') as log:
      self.test.runTest()

    self.assertEqual(log.output,
                     ['ERROR:root:StressAppTest failed: fake error message'])
    self.mock_goofy.WaitForWebSocketUp.assert_called_once()
    self.mock_cpu_freq_manager.RestoreFrequency.assert_called_once()


if __name__ == '__main__':
  unittest.main()
