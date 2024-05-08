#!/usr/bin/env python3
# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from cros.factory.test import device_data
from cros.factory.test.pytests import probe_cellular_info
from cros.factory.test.rf import cellular
from cros.factory.utils.arg_utils import Args


def MakeProbeModemInfoMock(mapping):

  def Get(fields):
    return [mapping.get(field, None) for field in fields]

  return mock.Mock(side_effect=Get)


def MakeProbeSimInfoMock(mapping):

  def Get(fields):
    return [[mapping.get(field, None) for field in fields]]

  return mock.Mock(side_effect=Get)

class ProbeCellularInfoTestTest(unittest.TestCase):

  def setUp(self):
    self.test = probe_cellular_info.ProbeCellularInfoTest()

  @mock.patch.object(cellular, 'ProbeModemInfo',
                     MakeProbeModemInfoMock({
                         'imei': '838293836198373',
                         'meid': 'Q9298301CDF827'
                     }))
  @mock.patch.object(cellular, 'ProbeSimInfo', mock.Mock(return_value=[]))
  @mock.patch('cros.factory.utils.process_utils.CheckOutput')
  @mock.patch('cros.factory.test.event_log.Log')
  @mock.patch('cros.factory.testlog.testlog.LogParam')
  @mock.patch('cros.factory.test.device_data.UpdateDeviceData')
  def testValid(self, update_device_data_mock, log_param_mock, log_mock,
                check_output_mock):
    stdout = 'test_modem_status_stdout'

    log_param_calls = [
        mock.call('modem_status_stdout', stdout),
        mock.call('imei', '838293836198373'),
        mock.call('meid', 'Q9298301CDF827')]

    check_output_mock.return_value = stdout

    # yapf: disable
    self.test.args = Args(*self.test.ARGS).Parse({})  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.test.runTest()

    check_output_mock.assert_called_once_with(['modem', 'status'], log=True)
    self.assertEqual(log_param_mock.call_args_list, log_param_calls)
    log_mock.assert_called_once_with(
        'cellular_info', modem_status_stdout=stdout,
        imei='838293836198373', meid='Q9298301CDF827')
    update_device_data_mock.assert_called_once_with(
        {'component.cellular.imei': '838293836198373',
         'component.cellular.meid': 'Q9298301CDF827'})

  @mock.patch.object(cellular, 'ProbeModemInfo',
                     MakeProbeModemInfoMock({'Imei': '359636040066332'}))
  @mock.patch.object(cellular, 'ProbeSimInfo',
                     MakeProbeSimInfoMock(
                         {'SimIdentifier': '89148000000328035895'}))
  @mock.patch('cros.factory.utils.process_utils.CheckOutput')
  @mock.patch('cros.factory.test.event_log.Log')
  @mock.patch('cros.factory.testlog.testlog.LogParam')
  @mock.patch('cros.factory.test.device_data.UpdateDeviceData')
  def testValidLTE(self, update_device_data_mock, log_param_mock, log_mock,
                   check_output_mock):
    stdout = 'test_modem_status_stdout'

    log_param_calls = [
        mock.call('modem_status_stdout', stdout),
        mock.call('lte_imei', '359636040066332'),
        mock.call('lte_iccid', '89148000000328035895')]

    check_output_mock.return_value = stdout

    # yapf: disable
    self.test.args = Args(*self.test.ARGS).Parse(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        {'probe_imei': False,
         'probe_meid': False,
         'probe_lte_imei': True,
         'probe_lte_iccid': True})
    self.test.runTest()

    check_output_mock.assert_called_once_with(['modem', 'status'], log=True)
    self.assertEqual(log_param_mock.call_args_list, log_param_calls)
    log_mock.assert_called_once_with(
        'cellular_info', modem_status_stdout=stdout,
        lte_imei='359636040066332', lte_iccid='89148000000328035895')
    update_device_data_mock.assert_called_once_with(
        {'component.cellular.lte_imei': '359636040066332',
         'component.cellular.lte_iccid': '89148000000328035895'})

  @mock.patch.object(cellular, 'ProbeModemInfo',
                     MakeProbeModemInfoMock({'meid': 'Q9298301CDF827'}))
  @mock.patch.object(cellular, 'ProbeSimInfo', mock.Mock(return_value=[]))
  @mock.patch('cros.factory.utils.process_utils.CheckOutput')
  @mock.patch('cros.factory.test.event_log.Log')
  @mock.patch('cros.factory.testlog.testlog.LogParam')
  @mock.patch.object(device_data, 'UpdateDeviceData', mock.Mock())
  def testMissingIMEI(self, log_param_mock, log_mock, check_output_mock):
    stdout = 'test_modem_status_stdout'

    log_param_calls = [
        mock.call('modem_status_stdout', stdout),
        mock.call('imei', None),
        mock.call('meid', 'Q9298301CDF827')]

    check_output_mock.return_value = stdout

    # yapf: disable
    self.test.args = Args(*self.test.ARGS).Parse({})  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.assertRaisesRegex(AssertionError, r"Missing elements.+: \['imei'\]",
                           self.test.runTest)

    check_output_mock.assert_called_once_with(['modem', 'status'], log=True)
    self.assertEqual(log_param_mock.call_args_list, log_param_calls)
    log_mock.assert_called_once_with(
        'cellular_info', modem_status_stdout=stdout,
        imei=None, meid='Q9298301CDF827')


  @mock.patch.object(cellular, 'ProbeModemInfo',
                     MakeProbeModemInfoMock(
                         {'EquipmentIdentifier': '862227050001326'}))
  @mock.patch.object(cellular, 'ProbeSimInfo', mock.Mock(return_value=[]))
  @mock.patch('cros.factory.utils.process_utils.CheckOutput')
  @mock.patch('cros.factory.test.event_log.Log')
  @mock.patch('cros.factory.testlog.testlog.LogParam')
  @mock.patch('cros.factory.test.device_data.UpdateDeviceData')
  def testSpecifiedFields(self, update_device_data_mock, log_param_mock,
                          log_mock, check_output_mock):
    stdout = 'test_modem_status_stdout'

    log_param_calls = [
        mock.call('modem_status_stdout', stdout),
        mock.call('imei', '862227050001326')
    ]

    check_output_mock.return_value = stdout

    # yapf: disable
    self.test.args = Args(*self.test.ARGS).Parse({  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        'probe_meid': False,
        'fields': {
            'imei': 'EquipmentIdentifier'
        }
    })
    self.test.runTest()

    check_output_mock.assert_called_once_with(['modem', 'status'], log=True)
    log_mock.assert_called_once_with(
        'cellular_info', modem_status_stdout=stdout, imei='862227050001326')
    self.assertEqual(log_param_mock.call_args_list, log_param_calls)
    update_device_data_mock.assert_called_once_with(
        {'component.cellular.imei': '862227050001326'})


if __name__ == '__main__':
  unittest.main()
