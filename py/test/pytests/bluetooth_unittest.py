#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
# pylint: disable=protected-access

import glob
import os
import shutil
import time
from typing import Dict, Optional, Tuple, Union
import unittest
from unittest import mock

from cros.factory.device import device_utils
from cros.factory.test import event_log
from cros.factory.test.pytests import bluetooth
from cros.factory.test import session
from cros.factory.test import state
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test.utils import bluetooth_utils
from cros.factory.testlog import testlog
from cros.factory.utils import file_utils
from cros.factory.utils import type_utils


class FakeArgs:

  def __init__(self, **kwargs):
    self.expected_adapter_count: int = 0
    self.manufacturer_id: Optional[int] = None
    self.detect_adapters_retry_times: int = 10
    self.detect_adapters_interval_secs: int = 2
    self.read_bluetooth_uuid_timeout_secs: int = 0
    self.scan_devices: bool = False
    self.prompt_scan_message: bool = True
    self.keyword: Optional[str] = None
    self.average_rssi_threshold: float = -70.0
    self.scan_counts: int = 3
    self.scan_timeout_secs: int = 10
    self.input_device_mac: Optional[str] = None
    self.input_device_mac_key: Optional[str] = None
    self.input_device_rssi_key: Optional[str] = None
    self.firmware_revision_string_key: Optional[str] = None
    self.firmware_revision_string: Optional[str] = None
    self.average_rssi_lower_threshold: Optional[Tuple[float, dict]] = None
    self.average_rssi_upper_threshold: Optional[Tuple[float, dict]] = None
    self.pair_with_match: bool = False
    self.finish_after_pair: bool = False
    self.unpair: bool = False
    self.check_shift_pair_keys: bool = False
    self.check_battery_charging: bool = False
    self.read_battery_level: Optional[int] = None
    self.check_battery_level: bool = False
    self.prompt_into_fixture: bool = False
    self.use_charge_fixture: bool = False
    self.reset_fixture: bool = False
    self.start_charging: bool = False
    self.enable_magnet: bool = False
    self.reset_magnet: bool = False
    self.stop_charging: bool = False
    self.base_enclosure_serial_number: Optional[str] = None
    self.battery_log: Optional[str] = None
    self.expected_battery_level: int = 100
    self.log_path: Optional[str] = None
    self.keep_raw_logs: bool = True
    self.test_host_id_file: Optional[str] = None

    for k, v in kwargs.items():
      setattr(self, k, v)


def i18n(text):
  return {
      'en-US': text
  }


class BluetoothUnitTest(unittest.TestCase):

  def setUp(self):
    self.test = bluetooth.BluetoothTest()
    self.ui = mock.create_autospec(test_ui.StandardUI)
    type_utils.LazyProperty.Override(self.test, 'ui', self.ui)
    self.fake_data_shelf: Dict[str, Union[str, int]] = {}

    def set_helper(key, val):
      self.fake_data_shelf[key] = val

    patcher = mock.patch.object(device_utils, 'CreateDUTInterface',
                                autospec=True)
    self.mock_dut = patcher.start().return_value
    patcher = mock.patch.object(test_ui, 'EventLoop', autospec=True)
    self.test.event_loop = patcher.start().return_value
    patcher = mock.patch.object(bluetooth_utils, 'VerifyAltSetting',
                                autospec=True)
    self.mock_verify_setting = patcher.start()
    patcher = mock.patch.object(bluetooth_utils, 'BtMgmt', autospec=True)
    self.btmgmt = patcher.start()
    self.mock_btmgmt = self.btmgmt.return_value
    self.mock_hci_device = self.mock_btmgmt.GetHciDevice.return_value
    self.mock_host_mac = self.mock_btmgmt.GetMac.return_value
    patcher = mock.patch.object(testlog, 'GroupParam', autospec=True)
    self.group_param = patcher.start()
    self.mock_group_checker = self.group_param.return_value
    patcher = mock.patch.object(file_utils, 'CreateTemporaryFile',
                                autospec=True)
    self.mock_create_tmp_file = patcher.start()
    self.mock_log_tmp_file = self.mock_create_tmp_file.return_value
    patcher = mock.patch.object(file_utils, 'ReadFile', autospec=True)
    self.mock_read_file = patcher.start()
    patcher = mock.patch.object(os.path, 'isfile', autospec=True)
    self.mock_is_file = patcher.start()
    patcher = mock.patch.object(os.path, 'join', autospec=True)
    self.mock_join = patcher.start()
    self.mock_log_file = self.mock_join.return_value
    patcher = mock.patch.object(state, 'DataShelfGetValue', autospec=True)
    self.mock_datashelf_get = patcher.start()
    self.mock_datashelf_get.side_effect = (
        lambda x: self.fake_data_shelf.get(x, None))
    patcher = mock.patch.object(state, 'DataShelfSetValue', autospec=True)
    self.mock_datshelf_set = patcher.start()
    self.mock_datshelf_set.side_effect = set_helper
    patcher = mock.patch.object(test_case.TestCase, 'AddTask', autospec=True)
    self.mock_add_task = patcher.start()
    patcher = mock.patch.object(test_case.TestCase, 'FailTask', autospec=True)
    self.mock_fail_task = patcher.start()
    patcher = mock.patch.object(test_case.TestCase, 'assertEqual',
                                autospec=True)
    self.mock_assert_equal = patcher.start()
    patcher = mock.patch.object(time, 'strftime', autospec=True)
    self.mock_strftime = patcher.start()
    self.addCleanup(mock.patch.stopall)

    self.test.args = FakeArgs()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.mock_bt_manager = self.mock_dut.bluetooth

  @mock.patch.object(glob, 'glob', autospec=True)
  def test_GetInputCount(self, mock_glob):
    mock_glob.return_value = ['/dev/input/event1', '/dev/input/event2']

    cnt = bluetooth.GetInputCount()

    self.assertEqual(cnt, 2)

  @mock.patch.object(os.path, 'dirname', autospec=True)
  @mock.patch.object(file_utils, 'TryMakeDirs', autospec=True)
  def test_AppendLog(self, mock_try_make_dir, mock_dirname):
    self.mock_strftime.return_value = '2024-01-01 01:02:03'
    mock_dirname.return_value = 'fake_log_dir'

    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
      bluetooth._AppendLog('fake_log_file', 'data1\ndata2\ndata3')
      mock_log = mock_file.return_value

      mock_dirname.assert_called_once_with('fake_log_file')
      mock_try_make_dir.assert_called_once_with('fake_log_dir')
      mock_file.assert_called_once_with('fake_log_file', 'a', encoding='utf8')
      mock_log.write.assert_called_once_with('2024-01-01 01:02:03 data1\n'
                                             '2024-01-01 01:02:03 data2\n'
                                             '2024-01-01 01:02:03 data3\n')

  def test_setUp_Init(self):
    self.test.args = FakeArgs(manufacturer_id=123)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_verify_setting.assert_called_once()
    self.ui.ToggleTemplateClass.assert_called_once_with('font-large', True)
    self.btmgmt.assert_called_once_with(123)
    self.mock_btmgmt.PowerOn.assert_called_once()
    self.group_param.assert_called_once_with('avg_rssi',
                                             ['mac', 'average_rssi'])

  def test_setUp_GetMacByKey(self):
    self.test.args = FakeArgs(input_device_mac_key='fake_key')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.fake_data_shelf['fake_key'] = 'ABCDEF012345'

    self.test.setUp()

    self.assertEqual(self.test._input_device_mac, 'AB:CD:EF:01:23:45')
    del self.fake_data_shelf['fake_key']

  def test_setUp_SetLogFile(self):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        base_enclosure_serial_number='fake_serial_num',
        test_host_id_file='fake_id_file', log_path='fake_log_path')
    self.mock_is_file.return_value = True
    self.mock_read_file.return_value = 'fake_test_host_id'

    self.test.setUp()

    self.mock_create_tmp_file.assert_called_once()
    self.mock_is_file.assert_called_once_with('fake_id_file')
    self.mock_read_file.assert_called_once_with('fake_id_file')
    self.mock_join.assert_called_once_with('fake_log_path',
                                           'fake_serial_num.fake_test_host_id')

  def test_setUp_DetectAdapter(self):
    self.test.args = FakeArgs(expected_adapter_count=3)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(self.test,
                                               self.test.DetectAdapter, 3)

  def test_setUp_ScanDevices(self):
    self.test.args = FakeArgs(scan_devices=True, prompt_scan_message=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_has_calls([
        mock.call(
            self.test, self.test.WaitKeyPressed,
            i18n('Enable the connection ability of bluetooth device '
                 'and press Enter')),
        mock.call(self.test, self.test.ScanDevices)
    ])

  def test_setUp_DetectRSSIofTargetMAC(self):
    self.test.args = FakeArgs(input_device_rssi_key='fake_rssi_key')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(self.test,
                                               self.test.DetectRSSIofTargetMAC)

  def test_setUp_PromptIntoFixture(self):
    self.test.args = FakeArgs(prompt_into_fixture=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.WaitKeyPressed,
        i18n('Place the base into the fixture, '
             'and press the space key on the test host.'), test_ui.SPACE_KEY)

  def test_setUp_ReadBatteryLevel_1(self):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        read_battery_level=1, input_device_mac='AB:CD:EF:01:23:45')

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.ReadBatteryLevel, 'AB:CD:EF:01:23:45',
        'read_battery_1')

  def test_setUp_EnableMagnet(self):
    self.test.args = FakeArgs(enable_magnet=True, use_charge_fixture=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.FixtureControl, 'ENABLE_MAGNET')

  def test_setUp_ResetMagnet_UseFixture(self):
    self.test.args = FakeArgs(reset_magnet=True, use_charge_fixture=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_has_calls([
        mock.call(self.test, self.test.FixtureControl, 'DISABLE_MAGNET',
                  post_sleep=1),
        mock.call(self.test, self.test.FixtureControl, 'ENABLE_MAGNET')
    ])

  def test_setUp_ResetMagnet_DoNotUseFixture(self):
    self.test.args = FakeArgs(reset_magnet=True, use_charge_fixture=False)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.WaitKeyPressed,
        i18n('Please re-attach the magnet, '
             'and press the space key on the test host.'), test_ui.SPACE_KEY)

  def test_setUp_StartCharging_UseFixture(self):
    self.test.args = FakeArgs(start_charging=True, use_charge_fixture=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.FixtureControl, 'START_CHARGING')

  def test_setUp_StartCharging_DoNotUseFixture(self):
    self.test.args = FakeArgs(start_charging=True, use_charge_fixture=False)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.WaitKeyPressed,
        i18n('Turn on charging by pressing the green button, '
             'take the keyboard out and put it back, '
             'and press the space key on the test host.'), test_ui.SPACE_KEY)

  def test_setUp_CheckPairKeys(self):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        check_shift_pair_keys=True, input_device_mac='AB:CD:EF:01:23:45')

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.CheckDisconnectionOfPairedDevice,
        'AB:CD:EF:01:23:45')

  def test_setUp_Unpair(self):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        unpair=True, input_device_mac='AB:CD:EF:01:23:45',
        keyword='fake_keyword')

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.Unpair, 'AB:CD:EF:01:23:45', 'fake_keyword')

  def test_setUp_CheckFirmwareRevision(self):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        firmware_revision_string='fake_fw_rev_str',
        input_device_mac='AB:CD:EF:01:23:45')

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.CheckFirmwareRevision, 'AB:CD:EF:01:23:45')

  def test_setUp_PairWithMatch(self):
    self.test.args = FakeArgs(pair_with_match=True, finish_after_pair=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(self.test, self.test.TestInput,
                                               True)

  def test_setUp_ReadBatteryLevel_2(self):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        read_battery_level=2, input_device_mac='AB:CD:EF:01:23:45')

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.ReadBatteryLevel, 'AB:CD:EF:01:23:45',
        'read_battery_2')

  def test_setUp_CheckBatteryLevel(self):
    self.test.args = FakeArgs(check_battery_level=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(self.test,
                                               self.test.CheckBatteryLevel)

  def test_setUp_StopCharging_UseFixture(self):
    self.test.args = FakeArgs(stop_charging=True, use_charge_fixture=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.FixtureControl, 'STOP_CHARGING')

  def test_setUp_StopCharging_DoNotUseFixture(self):
    self.test.args = FakeArgs(stop_charging=True, use_charge_fixture=False)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    self.test.setUp()

    self.mock_add_task.assert_called_once_with(
        self.test, self.test.WaitKeyPressed,
        i18n('Press the green button again to stop charging, '
             'and press the space key on the test host.'), test_ui.SPACE_KEY)

  @mock.patch.object(shutil, 'copyfile', autospec=True)
  @mock.patch.object(testlog, 'AttachFile', autospec=True)
  @mock.patch.object(os, 'remove', autospec=True)
  def test_tearDown(self, mock_remove, mock_attach_file, mock_copy_file):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        use_charge_fixture=True, base_enclosure_serial_number='fake_serial_num',
        test_host_id_file='fake_id_file', log_path='fake_log_path',
        keep_raw_logs=True)
    self.mock_is_file.return_value = True

    self.test.setUp()
    self.test.fixture = mock.Mock()
    self.test.tearDown()

    self.test.fixture.Close.assert_called_once()
    mock_copy_file.assert_called_once_with(self.mock_log_tmp_file,
                                           self.mock_log_file)
    mock_attach_file.assert_called_once_with(
        path=self.mock_log_tmp_file, mime_type='text/plain',
        name='bluetooth.log', description='plain text log of bluetooth',
        delete=False)
    mock_remove.assert_called_once_with(self.mock_log_tmp_file)

  def test_WaitKeyPressed(self):
    self.test.WaitKeyPressed('message', 'key')

    self.ui.SetState.assert_called_once_with('message')
    self.ui.WaitKeysOnce.assert_called_once_with('key')

  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_CheckFirmwareRevision(self, mock_append_log, mock_retry):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        read_bluetooth_uuid_timeout_secs=5,
        firmware_revision_string_key='fake_fw_rev_key',
        firmware_revision_string='fake_fw_rev_str')
    mock_retry.return_value = 'fake_fw'

    self.test.setUp()
    self.test.CheckFirmwareRevision('mac')

    self.ui.SetState.assert_called_once_with(
        i18n('Read firmware revision string.'))
    mock_retry.assert_called_once_with(
        self.test, 'reading firmware', 10, 1,
        bluetooth_utils.GattTool.GetDeviceInfo, 'mac',
        'firmware revision string', hci_device=self.mock_hci_device, timeout=5)
    self.assertEqual(self.fake_data_shelf['fake_fw_rev_key'], 'fake_fw')
    mock_append_log.assert_called_once_with(None, 'FW: fake_fw\n')
    self.mock_assert_equal.assert_called_once_with(
        self.test, 'fake_fw_rev_str', 'fake_fw',
        'Expected firmware: fake_fw_rev_str, actual firmware: fake_fw')

  def test_CheckBatteryLevel(self):
    self.test.args = FakeArgs(expected_battery_level=5)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.fake_data_shelf['read_battery_1'] = 10
    self.fake_data_shelf['read_battery_2'] = 20

    self.test.CheckBatteryLevel()

    self.ui.SetState.assert_called_once_with(
        i18n('Check if the battery has charged to a higher percentage'))
    self.mock_fail_task.assert_not_called()

  def test_CheckBatteryLevel_Fail_OnlyReadOneValue(self):
    self.test.args = FakeArgs(expected_battery_level=5)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.fake_data_shelf['read_battery_1'] = 10

    self.test.CheckBatteryLevel()

    self.mock_fail_task.assert_called_once_with(
        self.test,
        'Battery levels should be read twice. read_1: 10, read_2: None')

  def test_CheckBatteryLevel_Fail_NotChargeUp(self):
    self.test.args = FakeArgs(expected_battery_level=5)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.fake_data_shelf['read_battery_1'] = 10
    self.fake_data_shelf['read_battery_2'] = 9

    self.test.CheckBatteryLevel()

    self.mock_fail_task.assert_called_once_with(
        self.test, 'Base battery is not charged up. read_1: 10, read_2: 9')

  def test_CheckBatteryLevel_Fail_LessThanExpect(self):
    self.test.args = FakeArgs(expected_battery_level=15)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.fake_data_shelf['read_battery_1'] = 10
    self.fake_data_shelf['read_battery_2'] = 20

    self.test.CheckBatteryLevel()

    self.mock_fail_task.assert_called_once_with(
        self.test,
        'Measured battery level 10 is less than the expected level 15.')
    del self.fake_data_shelf['read_battery_1']
    del self.fake_data_shelf['read_battery_2']

  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_ReadBatteryLevel(self, mock_append_log, mock_retry):

    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
      self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          expected_battery_level=15, read_bluetooth_uuid_timeout_secs=3,
          battery_log='fake_battery_log',
          base_enclosure_serial_number='fake_serial_num')
      mock_retry.return_value = 10.0
      self.fake_data_shelf['read_battery_2'] = 20
      mock_log = mock_file.return_value
      self.mock_strftime.return_value = 'fake_time'

      self.test.setUp()
      self.test.ReadBatteryLevel('mac', 'read_battery_2')

      self.ui.SetState.assert_called_once_with(
          i18n(('Read battery level for the 2nd time.')))
      mock_retry.assert_called_once_with(
          self.test, 'read_battery_2', 10, 1,
          bluetooth_utils.GattTool.GetDeviceInfo, 'mac', 'battery level',
          hci_device=self.mock_hci_device, timeout=3)
      self.assertEqual(self.fake_data_shelf['read_battery_2'], 10)
      mock_append_log.assert_called_once_with(self.mock_log_tmp_file,
                                              'read_battery_2: 10\n')
      mock_file.assert_called_once_with('fake_battery_log', 'a',
                                        encoding='utf8')
      mock_log.write.assert_called_once_with('fake_time fake_serial_num mac'
                                             ' [read_battery_2]: 10\n')

  @mock.patch.object(test_case.TestCase, 'Sleep', autospec=True)
  def test_FixtureControl(self, mock_sleep):
    self.test.fixture = mock.MagicMock()
    mock_obj = mock.MagicMock()
    fake_func = mock_obj.func
    fake_func.__name__ = ''
    self.test.fixture.StartCharging = fake_func

    self.test.FixtureControl('START_CHARGING', 0)

    fake_func.assert_called_once()
    mock_sleep.assert_called_once_with(self.test, 0)

  def test_DetectAdapter(self):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        detect_adapters_retry_times=3, detect_adapters_interval_secs=1)
    self.mock_bt_manager.GetAdapters.return_value = ['adapter1', 'adapter2']

    self.test.setUp()
    self.test.DetectAdapter(2)

    self.ui.SetState.assert_called_once_with(i18n('Detect bluetooth adapter'))
    self.mock_bt_manager.GetAdapters.assert_called_once_with(3, 1)
    self.mock_assert_equal.assert_called_once_with(
        self.test, 2, 2, 'DetectAdapter: expect 2 and find 2 adapter(s).')

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  def test_Unpair(self, mock_wait, mock_get_input_count):
    mock_get_input_count.return_value = 2
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    self.mock_bt_manager.GetAllDevices.return_value = {
        'fake_device_1': {
            'Address': 123,
            'Paired': True
        },
        'fake_device_2': {
            'Address': 456,
            'Paired': True
        }
    }

    self.test.setUp()
    self.test.Unpair(None, None)

    self.ui.SetState.assert_called_once_with(i18n('Unpairing'))

    self.mock_bt_manager.GetFirstAdapter.assert_called_once_with(
        self.mock_host_mac)
    self.mock_bt_manager.GetAllDevices.assert_called_once_with('fake_adapter')
    self.mock_bt_manager.DisconnectAndUnpairDevice.assert_has_calls(
        [mock.call('fake_adapter', 123),
         mock.call('fake_adapter', 456)])
    self.mock_bt_manager.RemovePairedDevice.assert_has_calls(
        [mock.call('fake_adapter', 123),
         mock.call('fake_adapter', 456)])
    mock_wait.assert_called_once_with(0)

  @mock.patch.object(bluetooth.BluetoothTest, 'TimedProgressBar', autospec=True)
  @mock.patch.object(event_log, 'Log', autospec=True)
  @mock.patch.object(testlog, 'LogParam', autospec=True)
  @mock.patch.object(testlog, 'CheckNumericParam', autospec=True)
  def test_ScanDevices(self, mock_check_param, mock_testlog, mock_event_log,
                       mock_time_bar):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        keyword='fake_keyword', average_rssi_threshold=-50.0, scan_counts=1,
        scan_timeout_secs=10)
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    self.mock_bt_manager.ScanDevices.return_value = {
        'fake_mac_1': {
            'Name': 'fake_keyword_name_1',
            'RSSI': -46.0
        },
        'fake_mac_2': {
            'Name': 'fake_keyword_name_2',
            'RSSI': -48.0
        }
    }

    self.test.setUp()
    self.test.ScanDevices()

    self.mock_bt_manager.GetFirstAdapter.assert_called_once_with(
        self.mock_host_mac)
    self.ui.SetState.assert_called_once_with(i18n('Scanning...'))
    mock_time_bar.assert_called_once_with(self.test, 10)
    self.mock_bt_manager.ScanDevices.assert_called_once_with('fake_adapter', 10)
    mock_event_log.assert_has_calls([
        mock.call('avg_rssi', mac='fake_mac_1', average_rssi=-46),
        mock.call('avg_rssi', mac='fake_mac_2', average_rssi=-48),
        mock.call('bluetooth_scan_device', mac='fake_mac_1', rssi=-46,
                  meet=True)
    ])
    mock_testlog.assert_has_calls([
        mock.call('mac', 'fake_mac_1'),
        mock.call('average_rssi', -46.0),
        mock.call('mac', 'fake_mac_2'),
        mock.call('average_rssi', -48.0),
    ])
    mock_check_param.assert_called_once_with('max_average_rssi', -46, min=-50.0)

  @mock.patch.object(bluetooth.BluetoothTest, 'TimedProgressBar', autospec=True)
  @mock.patch.object(event_log, 'Log', autospec=True)
  @mock.patch.object(testlog, 'LogParam', autospec=True)
  @mock.patch.object(testlog, 'CheckNumericParam', autospec=True)
  def test_ScanDevices_Fail_LessThanThreshold(
      self, unused_mock_check_param, unused_mock_testlog, unused_mock_event_log,
      unused_mock_time_bar):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        keyword='fake_keyword', average_rssi_threshold=-45.0, scan_counts=1,
        scan_timeout_secs=10)
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    self.mock_bt_manager.ScanDevices.return_value = {
        'fake_mac_1': {
            'Name': 'fake_keyword_name_1',
            'RSSI': -46.0
        },
        'fake_mac_2': {
            'Name': 'fake_keyword_name_2',
            'RSSI': -48.0
        }
    }

    self.test.setUp()
    self.test.ScanDevices()

    self.mock_fail_task.assert_called_once_with(
        self.test, 'ScanDeviceTask: The largest average RSSI -46.000000 of '
        'device fake_mac_1 does not meet threshold -45.000000.')

  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_CheckDisconnectionOfPairedDevice(self, mock_append_log, mock_retry):
    mock_retry.return_value = True

    self.test.setUp()
    self.test.CheckDisconnectionOfPairedDevice('fake_mac')

    self.ui.SetState.assert_called_once_with(
        i18n('Press shift-p-a-i-r simultaneously on the base.'))
    mock_append_log.assert_called_once_with(None, 'Shift-P-A-I-R: done')

  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_CheckDisconnectionOfPairedDevice_Fail(self, mock_append_log,
                                                 mock_retry):
    mock_retry.return_value = False

    self.test.setUp()
    self.test.CheckDisconnectionOfPairedDevice('fake_mac')

    mock_append_log.assert_called_once_with(None, 'Shift-P-A-I-R: not done')
    self.mock_fail_task.assert_called_once_with(self.test,
                                                'Shift-P-A-I-R: not done')

  @mock.patch.object(session, 'GetDeviceID', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'TimedProgressBar', autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_DetectRSSIofTargetMAC(self, mock_append_log, mock_time_bar,
                                 mock_get_id):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        input_device_mac='fake_mac_1', scan_counts=1, scan_timeout_secs=10,
        input_device_rssi_key='fake_rssi_key',
        average_rssi_lower_threshold=-50.0, average_rssi_upper_threshold=-40.0)
    mock_get_id.return_value = 'fake_fid'
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    self.mock_bt_manager.ScanDevices.return_value = {
        'fake_mac_1': {
            'RSSI': -46.0
        },
        'fake_mac_2': {
            'RSSI': -48.0
        }
    }

    self.test.setUp()
    self.test.DetectRSSIofTargetMAC()

    mock_get_id.assert_called_once()
    self.mock_bt_manager.GetFirstAdapter.assert_called_once_with(
        self.mock_host_mac)
    self.ui.SetState.assert_called_once_with(i18n('Detect RSSI (count 1/1)'))
    mock_time_bar.assert_called_once_with(self.test, 10)
    self.mock_bt_manager.ScanDevices.assert_called_once_with(
        'fake_adapter', timeout_secs=10, match_address='fake_mac_1')
    self.assertEqual(self.fake_data_shelf['fake_rssi_key'], -46.0)
    mock_append_log.assert_called_once_with(
        None, 'Average RSSI: -46.00 [-46]  '
        '(pass exp: [-50.00, -40.00])\n')
    self.mock_fail_task.assert_not_called()

  @mock.patch.object(session, 'GetDeviceID', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'TimedProgressBar', autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_DetectRSSIofTargetMAC_NoRssis(self, unused_mock_append_log,
                                         unused_mock_time_bar, mock_get_id):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        input_device_mac='fake_mac_1', scan_counts=1, scan_timeout_secs=10,
        input_device_rssi_key='fake_rssi_key',
        average_rssi_lower_threshold=-50.0, average_rssi_upper_threshold=-40.0)
    mock_get_id.return_value = 'fake_fid'
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    self.mock_bt_manager.ScanDevices.return_value = {
        'fake_mac_1': {},
        'fake_mac_2': {}
    }

    self.test.setUp()
    with self.assertRaises(Exception):
      self.test.DetectRSSIofTargetMAC()

    self.mock_fail_task.assert_called_once_with(
        self.test,
        'DetectRSSIofTargetMAC: Fail to get RSSI from device fake_mac_1.')

  @mock.patch.object(session, 'GetDeviceID', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'TimedProgressBar', autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_DetectRSSIofTargetMAC_LessThanThreshold(
      self, unused_mock_append_log, unused_mock_time_bar, mock_get_id):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        input_device_mac='fake_mac_1', scan_counts=1, scan_timeout_secs=10,
        input_device_rssi_key='fake_rssi_key',
        average_rssi_lower_threshold=-50.0, average_rssi_upper_threshold=-40.0)
    mock_get_id.return_value = 'fake_fid'
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    self.mock_bt_manager.ScanDevices.return_value = {
        'fake_mac_1': {
            'RSSI': -56.0
        },
        'fake_mac_2': {
            'RSSI': -48.0
        }
    }

    self.test.setUp()
    self.test.DetectRSSIofTargetMAC()

    self.mock_fail_task.assert_called_once_with(
        self.test, 'Average RSSI -56.00 less than the lower threshold -50.00\n')

  @mock.patch.object(session, 'GetDeviceID', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'TimedProgressBar', autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_DetectRSSIofTargetMAC_GreaterThanThreshold(
      self, unused_mock_append_log, unused_mock_time_bar, mock_get_id):
    self.test.args = FakeArgs(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        input_device_mac='fake_mac_1', scan_counts=1, scan_timeout_secs=10,
        input_device_rssi_key='fake_rssi_key',
        average_rssi_lower_threshold=-50.0, average_rssi_upper_threshold=-40.0)
    mock_get_id.return_value = 'fake_fid'
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    self.mock_bt_manager.ScanDevices.return_value = {
        'fake_mac_1': {
            'RSSI': -36.0
        },
        'fake_mac_2': {
            'RSSI': -48.0
        }
    }

    self.test.setUp()
    self.test.DetectRSSIofTargetMAC()

    self.mock_fail_task.assert_called_once_with(
        self.test,
        'Average RSSI -36.00 greater than the upper threshold -40.00\n')

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_TestInput_FinishAfterPair(self, mock_append_log, mock_retry,
                                     mock_wait, mock_input_count):
    self.test.args = FakeArgs(input_device_mac='fake_mac')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    mock_input_count.return_value = 3
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    mock_retry.side_effect = [True] * 2

    self.test.setUp()
    self.test.TestInput(True)

    self.mock_bt_manager.GetFirstAdapter.assert_called_once_with(
        self.mock_host_mac)
    self.mock_bt_manager.DisconnectAndUnpairDevice.assert_called_once_with(
        'fake_adapter', 'fake_mac')
    self.ui.SetState.assert_has_calls([
        mock.call(i18n('Pairing to input device now...')),
        mock.call(i18n('Connecting to input device now...'))
    ])
    mock_wait.assert_called_once_with(4)
    mock_append_log.assert_called_once_with(None, 'Pairing finished\n')
    self.mock_fail_task.assert_not_called()

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_TestInput_NotFinishAfterPair(self, unused_mock_append_log,
                                        mock_retry, unused_mock_wait,
                                        mock_input_count):
    self.test.args = FakeArgs(input_device_mac='fake_mac')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    mock_input_count.return_value = 3
    self.mock_bt_manager.GetFirstAdapter.return_value = 'fake_adapter'
    mock_retry.side_effect = [True] * 2
    self.ui.WaitKeysOnce.return_value = test_ui.ENTER_KEY

    self.test.setUp()
    self.test.TestInput(False)

    self.ui.SetState.assert_has_calls([
        mock.call(i18n('Pairing to input device now...')),
        mock.call(i18n('Connecting to input device now...')),
        mock.call(
            i18n('Please test input. Press Escape to fail and Enter to pass'))
    ])
    self.ui.WaitKeysOnce.assert_called_once_with(
        [test_ui.ENTER_KEY, test_ui.ESCAPE_KEY])
    self.mock_bt_manager.SetDeviceConnected.assert_called_once_with(
        'fake_adapter', 'fake_mac', False)
    self.mock_bt_manager.RemovePairedDevice.assert_called_once_with(
        'fake_adapter', 'fake_mac')
    self.mock_fail_task.assert_not_called()

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_TestInput_Fail_NoMac(self, mock_append_log, mock_retry,
                                unused_mock_wait, unused_mock_input_count):
    self.test.args = FakeArgs(input_device_mac='')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    mock_retry.side_effect = [True] * 2
    self.ui.WaitKeysOnce.return_value = test_ui.ENTER_KEY

    self.test.setUp()
    self.test.TestInput(False)

    mock_append_log.assert_called_once_with(
        None, 'Pairing fail: InputTestTask: No MAC with which to pair\n')
    self.mock_fail_task.assert_called_once_with(
        self.test, 'InputTestTask: No MAC with which to pair')

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_TestInput_FailCreateDevice(self, mock_append_log, mock_retry,
                                      unused_mock_wait,
                                      unused_mock_input_count):
    self.test.args = FakeArgs(input_device_mac='fake_mac')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    mock_retry.side_effect = [False, True]
    self.ui.WaitKeysOnce.return_value = test_ui.ENTER_KEY

    self.test.setUp()
    self.test.TestInput(False)

    mock_append_log.assert_called_once_with(
        None, 'Pairing fail: InputTestTask: Fail to create paired device.\n')
    self.mock_fail_task.assert_called_once_with(
        self.test, 'InputTestTask: Fail to create paired device.')

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_TestInput_FailConnectDevice(self, mock_append_log, mock_retry,
                                       unused_mock_wait,
                                       unused_mock_input_count):
    self.test.args = FakeArgs(input_device_mac='fake_mac')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    mock_retry.side_effect = [True, False]
    self.ui.WaitKeysOnce.return_value = test_ui.ENTER_KEY

    self.test.setUp()
    self.test.TestInput(False)

    mock_append_log.assert_called_once_with(
        None, 'Pairing fail: InputTestTask: Fail to connect device.\n')
    self.mock_fail_task.assert_called_once_with(
        self.test, 'InputTestTask: Fail to connect device.')

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_TestInput_FailRemove(self, unused_mock_append_log, mock_retry,
                                unused_mock_wait, unused_mock_input_count):
    self.test.args = FakeArgs(input_device_mac='fake_mac')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    mock_retry.side_effect = [True] * 2
    self.ui.WaitKeysOnce.return_value = test_ui.ENTER_KEY
    self.mock_bt_manager.Error = Exception
    self.mock_bt_manager.SetDeviceConnected.side_effect = (
        self.mock_bt_manager.Error)

    self.test.setUp()
    self.test.TestInput(False)

    self.mock_fail_task.assert_called_once_with(
        self.test, 'InputTestTask: Fail to remove input')

  @mock.patch.object(bluetooth, 'GetInputCount', autospec=True)
  @mock.patch.object(bluetooth, 'WaitForInputCount', autospec=True)
  @mock.patch.object(bluetooth.BluetoothTest, 'RetryWithProgress',
                     autospec=True)
  @mock.patch.object(bluetooth, '_AppendLog', autospec=True)
  def test_TestInput_FailByOperator(self, unused_mock_append_log, mock_retry,
                                    unused_mock_wait, unused_mock_input_count):
    self.test.args = FakeArgs(input_device_mac='fake_mac')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    mock_retry.side_effect = [True] * 2
    self.ui.WaitKeysOnce.return_value = test_ui.ESCAPE_KEY

    self.test.setUp()
    self.test.TestInput(False)

    self.mock_fail_task.assert_called_once_with(self.test, 'Failed by operator')

  def test_TimedProgressBar(self):

    self.test.setUp()
    with self.test.TimedProgressBar(10):
      pass

    self.ui.DrawProgressBar.assert_called_once_with(10)
    self.test.event_loop.AddTimedHandler.assert_called_once()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

  def test_RetryWithProgress(self):
    self.fake_data_shelf['fake_key'] = 'fake_val'

    self.test.setUp()
    result = self.test.RetryWithProgress('fake_action_string', 3, 0.1,
                                         state.DataShelfGetValue, 'fake_key')

    self.ui.DrawProgressBar.assert_called_once_with(3)
    self.mock_datashelf_get.assert_called_once_with('fake_key')
    self.ui.AdvanceProgress.assert_called_once()
    self.ui.SetProgress.assert_called_once_with(3)
    self.assertEqual(result, 'fake_val')


if __name__ == '__main__':
  unittest.main()
