#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from cros.factory.device import device_utils
from cros.factory.test import device_data
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test.i18n import _
from cros.factory.test.pytests import write_device_data_to_vpd
from cros.factory.utils import type_utils


class FakeArgs:

  def __init__(self, **kwargs):
    self.ro_key_map: dict = None
    self.rw_key_map: dict = None

    for k, v in kwargs.items():
      setattr(self, k, v)


class WriteDeviceDataToVPDUnitTest(unittest.TestCase):

  def setUp(self):
    self.test = write_device_data_to_vpd.WriteDeviceDataToVPD()
    self.ui = mock.create_autospec(test_ui.StandardUI)
    type_utils.LazyProperty.Override(self.test, 'ui', self.ui)

    def _GetFakeDeviceData(key='', default=None):
      return {
          key: key + '.data'
      } if key else default

    patcher = mock.patch.object(device_utils, 'CreateDUTInterface',
                                autospec=True)
    self.mock_dut = patcher.start().return_value
    patcher = mock.patch.object(device_data, 'GetDeviceData',
                                side_effect=_GetFakeDeviceData, autospec=True)
    self.mock_get_device_data = patcher.start()
    patcher = mock.patch.object(device_data, 'FlattenData',
                                side_effect=lambda dict: dict, autospec=True)
    self.mock_flatten_data = patcher.start()
    self.addCleanup(mock.patch.stopall)

    self.test.args = FakeArgs()

  def test_runTest_GetDeviceDataWithoutKeyMap(self):
    self.test.args = FakeArgs(ro_key_map=None, rw_key_map=None)

    self.test.setUp()
    self.test.runTest()

    self.mock_get_device_data.assert_has_calls(
        [mock.call('vpd.ro', {}),
         mock.call('vpd.rw', {})])

  def test_runTest_GetAdditionalDataWithoutKeyMap(self):
    self.test.args = FakeArgs(ro_key_map=None, rw_key_map=None)

    self.test.setUp()
    self.test.runTest()

    self.mock_get_device_data.assert_has_calls([
        mock.call('serials', {}),
        mock.call('oem_name'),
        mock.call('factory', {})
    ])
    self.mock_flatten_data.assert_called_once_with(
        {'factory': {
            'factory': 'factory.data'
        }})

  def test_runTest_GetDeviceDataWithKeyMap(self):
    self.test.args = FakeArgs(
        ro_key_map={
            'fake_vpd_name1': 'fake_device_data_key1',
            'fake_vpd_name2': 'fake_device_data_key2'
        }, rw_key_map={'fake_vpd_name3': 'fake_device_data_key3'})

    self.test.setUp()
    self.test.runTest()

    self.mock_get_device_data.assert_has_calls([
        mock.call('fake_device_data_key1'),
        mock.call('fake_device_data_key2'),
        mock.call('fake_device_data_key3')
    ])

  @mock.patch.object(test_case.TestCase, 'FailTask', autospec=True)
  def test_runTest_KeyMissing(self, mock_fail_task):

    def _GetFakeDeviceDataWithEmptyValue(key='', default=None):
      return {
          key: None
      } if key else default

    self.mock_get_device_data.side_effect = _GetFakeDeviceDataWithEmptyValue
    self.test.args = FakeArgs(ro_key_map=None, rw_key_map=None)

    self.test.setUp()
    self.test.runTest()

    mock_fail_task.assert_called_once_with(
        self.test, "Missing device data keys: ['serials', 'vpd.ro', 'vpd.rw']")

  def test_runTest_WriteDataToVPD(self):
    self.test.args = FakeArgs(ro_key_map=None, rw_key_map=None)
    ro_vpd = self.mock_dut.vpd.ro
    rw_vpd = self.mock_dut.vpd.rw

    self.test.setUp()
    self.test.runTest()

    self.ui.SetState.assert_has_calls([
        mock.call(
            _('Writing device data to {vpd_section} VPD...', vpd_section='RO')),
        mock.call(
            _('Writing device data to {vpd_section} VPD...', vpd_section='RW'))
    ])
    ro_vpd.Update.assert_called_once_with({
        'vpd.ro': 'vpd.ro.data',
        'serials': 'serials.data',
        'oem_name': "{'oem_name': 'oem_name.data'}"
    })
    rw_vpd.Update.assert_called_once_with({
        'vpd.rw': 'vpd.rw.data',
        'factory': "{'factory': 'factory.data'}"
    })

  def test_runTest_WriteDataToVPD_SkipEmptyEntries(self):
    # Only read RO VPD data.
    self.test.args = FakeArgs(
        ro_key_map={'fake_vpd_name': 'fake_device_data_key'}, rw_key_map=None)
    rw_vpd = self.mock_dut.vpd.rw

    self.test.setUp()
    self.test.runTest()

    rw_vpd.Update.assert_not_called()


if __name__ == '__main__':
  unittest.main()
