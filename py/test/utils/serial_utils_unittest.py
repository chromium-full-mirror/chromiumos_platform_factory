#!/usr/bin/env python3
#
# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittest for serial_utils."""

import unittest
from unittest import mock

from cros.factory.test.utils import serial_utils

from cros.factory.external.py_lib import serial


_DEFAULT_DRIVER = 'pl2303'
_DEFAULT_INDEX = '1-1'
_DEFAULT_PORT = '/dev/ttyUSB0'
_SEND_RECEIVE_INTERVAL_SECS = 0.2
_RETRY_INTERVAL_SECS = 0.5
_COMMAND = 'Command'
_RESPONSE = '.'
_RECEIVE_SIZE = 1


class OpenSerialTest(unittest.TestCase):

  def testOpenSerial(self):
    # Sequence matters: create a serial mock then stub out serial.Serial.
    # yapf: disable
    mock_serial = mock.Mock(serial.Serial)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    mock_serial.isOpen = lambda: True

    with mock.patch(
        'cros.factory.external.py_lib.serial.Serial') as serial_mock:
      serial_mock.return_value = mock_serial
      serial_utils.OpenSerial(port=_DEFAULT_PORT, baudrate=19200)

      serial_mock.assert_called_once_with(port=_DEFAULT_PORT, baudrate=19200)

  def testOpenSerialNoPort(self):
    self.assertRaises(ValueError, serial_utils.OpenSerial)


class FindTtyByDriverTest(unittest.TestCase):

  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByDriver(self, realpath_mock, glob_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.return_value = _DEFAULT_DRIVER

    self.assertEqual(_DEFAULT_PORT,
                     serial_utils.FindTtyByDriver(_DEFAULT_DRIVER))
    glob_mock.assert_called_once_with('/dev/tty*')
    realpath_mock.assert_called_once_with(
        '/sys/class/tty/ttyUSB0/device/driver')

  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByDriverSecondPort(self, realpath_mock, glob_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.side_effect = ['foo', _DEFAULT_DRIVER]
    realpath_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device/driver'),
        mock.call('/sys/class/tty/ttyUSB1/device/driver')]

    self.assertEqual('/dev/ttyUSB1',
                     serial_utils.FindTtyByDriver(_DEFAULT_DRIVER))
    glob_mock.assert_called_once_with('/dev/tty*')
    self.assertEqual(realpath_mock.call_args_list, realpath_calls)

  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByDriverNotFound(self, realpath_mock, glob_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.side_effect = ['foo', 'bar']
    realpath_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device/driver'),
        mock.call('/sys/class/tty/ttyUSB1/device/driver')]

    self.assertIsNone(serial_utils.FindTtyByDriver(_DEFAULT_DRIVER))
    glob_mock.assert_called_once_with('/dev/tty*')
    self.assertEqual(realpath_mock.call_args_list, realpath_calls)

  @mock.patch('cros.factory.test.utils.serial_utils.DeviceInterfaceProtocol')
  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByDriverInterfaceProtocol(self, realpath_mock, glob_mock,
                                           device_interface_protocol_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.side_effect = [_DEFAULT_DRIVER, _DEFAULT_DRIVER]
    realpath_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device/driver'),
        mock.call('/sys/class/tty/ttyUSB1/device/driver')]

    device_interface_protocol_mock.side_effect = ['00', '01']
    device_interface_protocol_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device'),
        mock.call('/sys/class/tty/ttyUSB1/device')]

    self.assertEqual('/dev/ttyUSB1',
                     serial_utils.FindTtyByDriver(_DEFAULT_DRIVER,
                                                  interface_protocol='01'))
    glob_mock.assert_called_once_with('/dev/tty*')
    self.assertEqual(realpath_mock.call_args_list, realpath_calls)
    self.assertEqual(device_interface_protocol_mock.call_args_list,
                     device_interface_protocol_calls)

  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByDriverMultiple(self, realpath_mock, glob_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.side_effect = [_DEFAULT_DRIVER, _DEFAULT_DRIVER]
    realpath_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device/driver'),
        mock.call('/sys/class/tty/ttyUSB1/device/driver')]

    self.assertEqual([_DEFAULT_PORT, '/dev/ttyUSB1'],
                     serial_utils.FindTtyByDriver(_DEFAULT_DRIVER,
                                                  multiple_ports=True))
    glob_mock.assert_called_once_with('/dev/tty*')
    self.assertEqual(realpath_mock.call_args_list, realpath_calls)


class FindTtyByPortIndexTest(unittest.TestCase):

  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByPortIndex(self, realpath_mock, glob_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.side_effect = [_DEFAULT_DRIVER, f'/{_DEFAULT_INDEX}/']
    realpath_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device/driver'),
        mock.call('/sys/class/tty/ttyUSB0/device')]

    self.assertEqual(_DEFAULT_PORT,
                     serial_utils.FindTtyByPortIndex(_DEFAULT_INDEX,
                                                     _DEFAULT_DRIVER))
    glob_mock.assert_called_once_with('/dev/tty*')
    self.assertEqual(realpath_mock.call_args_list, realpath_calls)

  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByPortIndexSecondPort(self, realpath_mock, glob_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.side_effect = ['foo', _DEFAULT_DRIVER, f'/{_DEFAULT_INDEX}/']
    realpath_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device/driver'),
        mock.call('/sys/class/tty/ttyUSB1/device/driver'),
        mock.call('/sys/class/tty/ttyUSB1/device')]

    self.assertEqual('/dev/ttyUSB1',
                     serial_utils.FindTtyByPortIndex(_DEFAULT_INDEX,
                                                     _DEFAULT_DRIVER))
    glob_mock.assert_called_once_with('/dev/tty*')
    self.assertEqual(realpath_mock.call_args_list, realpath_calls)

  @mock.patch('glob.glob')
  @mock.patch('os.path.realpath')
  def testFindTtyByPortIndexNotFound(self, realpath_mock, glob_mock):
    glob_mock.return_value = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    realpath_mock.side_effect = ['foo', 'bar']
    realpath_calls = [
        mock.call('/sys/class/tty/ttyUSB0/device/driver'),
        mock.call('/sys/class/tty/ttyUSB1/device/driver')]

    self.assertIsNone(serial_utils.FindTtyByPortIndex(_DEFAULT_INDEX,
                                                      _DEFAULT_DRIVER))
    glob_mock.assert_called_once_with('/dev/tty*')
    self.assertEqual(realpath_mock.call_args_list, realpath_calls)


class SerialDeviceCtorTest(unittest.TestCase):

  def testCtor(self):
    device = serial_utils.SerialDevice()
    self.assertEqual(0.2, device.send_receive_interval_secs)
    self.assertEqual(0.5, device.retry_interval_secs)
    self.assertFalse(device.log)

  @mock.patch('cros.factory.test.utils.serial_utils.OpenSerial')
  @mock.patch('cros.factory.test.utils.serial_utils.FindTtyByDriver')
  def testConnect(self, find_tty_by_driver_mock, open_serial_mock):
    find_tty_by_driver_mock.return_value = _DEFAULT_PORT
    # yapf: disable
    mock_serial = mock.Mock(serial.Serial)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    open_serial_mock.return_value = mock_serial

    device = serial_utils.SerialDevice()
    device.Connect(driver=_DEFAULT_DRIVER)

    find_tty_by_driver_mock.assert_called_once_with(_DEFAULT_DRIVER)
    open_serial_mock.assert_called_once_with(
        # yapf: disable
        port=_DEFAULT_PORT,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        parity=serial.PARITY_NONE,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        stopbits=serial.STOPBITS_ONE,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        timeout=0.5,
        writeTimeout=0.5)

  def testConnectPortDriverMissing(self):
    device = serial_utils.SerialDevice()
    # yapf: disable
    self.assertRaises(serial.SerialException, device.Connect)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  @mock.patch('cros.factory.test.utils.serial_utils.FindTtyByDriver')
  def testConnectDriverLookupFailure(self, find_tty_by_driver_mock):
    find_tty_by_driver_mock.return_value = ''

    device = serial_utils.SerialDevice()
    # yapf: disable
    self.assertRaises(serial.SerialException, device.Connect,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                      driver='UnknownDriver')
    find_tty_by_driver_mock.assert_called_once_with('UnknownDriver')

  @mock.patch('cros.factory.test.utils.serial_utils.OpenSerial')
  def testCtorNoPortLookupIfPortSpecified(self, open_serial_mock):
    # FindTtyByDriver isn't called.
    open_serial_mock.return_value = None

    device = serial_utils.SerialDevice()
    device.Connect(driver='UnknownDriver', port=_DEFAULT_PORT)
    open_serial_mock.assert_called_once_with(
        # yapf: disable
        port=_DEFAULT_PORT, baudrate=9600, bytesize=serial.EIGHTBITS,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        timeout=0.5, writeTimeout=0.5)


class SerialDeviceSendAndReceiveTest(unittest.TestCase):

  def setUp(self):
    self.device = serial_utils.SerialDevice()

    # Mock Serial and inject it.
    # yapf: disable
    self.mock_serial = mock.Mock(serial.Serial)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.device._serial = self.mock_serial  # pylint: disable=protected-access

  def tearDown(self):
    del self.device
    self.mock_serial.close.assert_called_once_with()

  def testSend(self):
    self.device.Send(_COMMAND)

    self.mock_serial.write.assert_called_once_with(_COMMAND)
    self.mock_serial.flush.assert_called_once_with()

  def testSendTimeout(self):
    # yapf: disable
    self.mock_serial.write.side_effect = serial.SerialTimeoutException  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.mock_serial.write_timeout = 0.5

    # yapf: disable
    self.assertRaises(serial.SerialTimeoutException, self.device.Send, _COMMAND)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.mock_serial.write.assert_called_once_with(_COMMAND)

  def testSendDisconnected(self):
    # yapf: disable
    self.mock_serial.write.side_effect = serial.SerialException  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # yapf: disable
    self.assertRaises(serial.SerialException, self.device.Send, _COMMAND)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.mock_serial.write.assert_called_once_with(_COMMAND)

  def testReceive(self):
    self.mock_serial.read.return_value = '.'

    self.assertEqual('.', self.device.Receive())

    self.mock_serial.read.assert_called_once_with(1)

  def testReceiveTimeout(self):
    self.mock_serial.read.return_value = ''
    self.mock_serial.timeout = 0.5

    # yapf: disable
    self.assertRaises(serial.SerialTimeoutException, self.device.Receive)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.mock_serial.read.assert_called_once_with(1)

  def testReceiveShortageTimeout(self):
    # Requested 5 bytes, got only 4 bytes.
    self.mock_serial.read.return_value = 'None'
    self.mock_serial.timeout = 0.5

    # yapf: disable
    self.assertRaises(serial.SerialTimeoutException, self.device.Receive, 5)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.mock_serial.read.assert_called_once_with(5)

  def testReceiveWhatsInBuffer(self):
    IN_BUFFER = 'InBuf'
    self.mock_serial.in_waiting = len(IN_BUFFER)
    self.mock_serial.read.return_value = IN_BUFFER

    self.assertEqual(IN_BUFFER, self.device.Receive(0))

    self.mock_serial.read.assert_called_once_with(len(IN_BUFFER))


class SerialDeviceSendReceiveTest(unittest.TestCase):

  def setUp(self):
    self.device = serial_utils.SerialDevice()

    # Mock methods to facilitate SendReceive testing.
    # yapf: disable
    self.device.Send = mock.Mock()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.device.Receive = mock.Mock()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.device.FlushBuffer = mock.Mock()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def tearDown(self):
    del self.device

  @mock.patch('time.sleep')
  def testSendReceive(self, sleep_mock):
    # yapf: disable
    self.device.Receive.return_value = _RESPONSE  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertEqual(_RESPONSE, self.device.SendReceive(_COMMAND))

    # yapf: disable
    self.device.Send.assert_called_once_with(_COMMAND)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    sleep_mock.assert_called_once_with(_SEND_RECEIVE_INTERVAL_SECS)
    # yapf: disable
    self.device.Receive.assert_called_once_with(_RECEIVE_SIZE)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.device.FlushBuffer.assert_called_once_with()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  @mock.patch('time.sleep')
  def testSendReceiveOverrideIntervalSecs(self, sleep_mock):
    override_interval_secs = 1
    # yapf: disable
    self.device.Receive.return_value = _RESPONSE  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertEqual(
        _RESPONSE,
        self.device.SendReceive(_COMMAND,
                                interval_secs=override_interval_secs))
    # yapf: disable
    self.device.Send.assert_called_once_with(_COMMAND)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    sleep_mock.assert_called_once_with(override_interval_secs)
    # yapf: disable
    self.device.Receive.assert_called_once_with(_RECEIVE_SIZE)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.device.FlushBuffer.assert_called_once_with()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  @mock.patch('time.sleep')
  def testSendReceiveWriteTimeoutRetrySuccess(self, sleep_mock):
    # Send timeout at first time & retry ok.
    # yapf: disable
    self.device.Send.side_effect = [serial.SerialTimeoutException, None]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    send_calls = [mock.call(_COMMAND), mock.call(_COMMAND)]
    sleep_calls = [
        mock.call(_SEND_RECEIVE_INTERVAL_SECS)]
    # yapf: disable
    self.device.Receive.return_value = _RESPONSE  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertEqual(_RESPONSE, self.device.SendReceive(_COMMAND, retry=1))
    # yapf: disable
    self.assertEqual(self.device.Send.call_args_list, send_calls)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.assertEqual(sleep_mock.call_args_list, sleep_calls)
    # yapf: disable
    self.assertEqual(2, self.device.FlushBuffer.call_count)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.device.Receive.assert_called_once_with(_RECEIVE_SIZE)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  @mock.patch('cros.factory.utils.sync_utils.GetPollingSleepFunction')
  @mock.patch('time.sleep')
  def testSendReceiveReadTimeoutRetrySuccess(self, sleep_mock,
                                             polling_sleep_mock):
    polling_sleep_mock.return_value = sleep_mock

    send_calls = [mock.call(_COMMAND), mock.call(_COMMAND)]
    sleep_calls = [
        mock.call(_SEND_RECEIVE_INTERVAL_SECS),
        mock.call(_RETRY_INTERVAL_SECS),
        mock.call(_SEND_RECEIVE_INTERVAL_SECS)]
    # Read timeout at first time & retry ok.
    # yapf: disable
    self.device.Receive.side_effect = [  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        serial.SerialTimeoutException,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        _RESPONSE]
    receive_calls = [mock.call(_RECEIVE_SIZE), mock.call(_RECEIVE_SIZE)]

    self.assertEqual(_RESPONSE, self.device.SendReceive(_COMMAND, retry=1))
    # yapf: disable
    self.assertEqual(self.device.Send.call_args_list, send_calls)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.assertEqual(sleep_mock.call_args_list, sleep_calls)
    # yapf: disable
    self.assertEqual(self.device.Receive.call_args_list, receive_calls)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.assertEqual(2, self.device.FlushBuffer.call_count)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  @mock.patch('cros.factory.utils.sync_utils.GetPollingSleepFunction')
  @mock.patch('time.sleep')
  def testSendRequestWriteTimeoutRetryFailure(self, sleep_mock,
                                              polling_sleep_mock):

    polling_sleep_mock.return_value = sleep_mock
    # Send timeout & retry still fail.
    # yapf: disable
    self.device.Send.side_effect = [  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        serial.SerialTimeoutException,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        serial.SerialTimeoutException]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    send_calls = [mock.call(_COMMAND), mock.call(_COMMAND)]

    # yapf: disable
    self.assertRaises(serial.SerialTimeoutException, self.device.SendReceive,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                      _COMMAND, retry=1)
    # yapf: disable
    self.assertEqual(self.device.Send.call_args_list, send_calls)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    sleep_mock.assert_called_once_with(_RETRY_INTERVAL_SECS)
    # yapf: disable
    self.assertEqual(2, self.device.FlushBuffer.call_count)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable


class SerialDeviceSendExpectReceiveTest(unittest.TestCase):

  def setUp(self):
    self.device = serial_utils.SerialDevice()

    # Mock methods to facilitate SendExpectReceive testing.
    # yapf: disable
    self.device.SendReceive = mock.Mock()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def tearDown(self):
    del self.device

  def testSendExpectReceive(self):
    # yapf: disable
    self.device.SendReceive.return_value = _RESPONSE  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertTrue(self.device.SendExpectReceive(_COMMAND, _RESPONSE))
    # yapf: disable
    self.device.SendReceive.assert_called_once_with(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        _COMMAND, _RECEIVE_SIZE, retry=0, interval_secs=None,
        suppress_log=True)

  def testSendExpectReceiveMismatch(self):
    # yapf: disable
    self.device.SendReceive.return_value = 'x'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertFalse(self.device.SendExpectReceive(_COMMAND, _RESPONSE))
    # yapf: disable
    self.device.SendReceive.assert_called_once_with(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        _COMMAND, _RECEIVE_SIZE, retry=0, interval_secs=None,
        suppress_log=True)

  def testSendExpectReceiveTimeout(self):
    # yapf: disable
    self.device.SendReceive.side_effect = serial.SerialTimeoutException  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertFalse(self.device.SendExpectReceive(_COMMAND, _RESPONSE))
    # yapf: disable
    self.device.SendReceive.assert_called_once_with(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        _COMMAND, _RECEIVE_SIZE, retry=0, interval_secs=None,
        suppress_log=True)


if __name__ == '__main__':
  unittest.main()
