#!/usr/bin/env python3
#
# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

# yapf: disable
import serial  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

from cros.factory.test.fixture.robot import six_dof_calibration_robot


# yapf: enable



Robot = six_dof_calibration_robot.SixDoFCalibrationRobot


class SixDoFCalibrationRobotTest(unittest.TestCase):
  # pylint: disable=protected-access

  def setUp(self):
    self._timeout = 10
    self._speed = 30
    self._acceleration = 20
    self._url = 'socket://192.168.0.1:8000'

    self._robot = Robot(
        url=self._url,
        timeout=self._timeout,
        speed=self._speed,
        acceleration=self._acceleration)

    self._serial = None
    self._serial = mock.create_autospec(spec=serial.Serial)

  def tearDown(self):
    disconnect = mock.Mock(spec=self._robot.Disconnect)
    # yapf: disable
    self._robot.Disconnect = disconnect  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    del self._robot

    disconnect.assert_called_with()

  @mock.patch('cros.factory.test.fixture.robot.six_dof_calibration_robot'
              '.serial.serial_for_url', autospec=True)
  def testConnect(self, serial_for_url):
    self._robot.Connect()

    serial_for_url.assert_called_with(self._url,
                                      timeout=self._timeout,
                                      writeTimeout=self._timeout)

  def _MockConnect(self):
    self._robot._serial = self._serial

  def testDisconnect(self):
    self._MockConnect()

    self._robot.Disconnect()

    # yapf: disable
    self._serial.close.assert_called_with()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def testSendCommand(self):
    self._MockConnect()
    cmd = '5566'
    args = ['5', '5', '6', '6']
    data = f"{Robot._CMD_PREFIX}{cmd},{','.join(args)}"
    res = 'Cmd5566 OK'
    # yapf: disable
    self._serial.write.return_value = len(data)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self._serial.readline.return_value = res  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot._SendCommand(cmd, *args)

    # yapf: disable
    self._serial.write.assert_called_with(data)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self._serial.readline.assert_called_with()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def testSetMotorOn(self):
    # yapf: disable
    self._robot._SendCommand = mock.Mock(spec=self._robot._SendCommand)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot.SetMotor(True)

    calls = [
        mock.call(Robot.CMD_POWER_ON),
        mock.call(Robot.CMD_SET_SPEED, *([f'{int(self._speed)}'] * 2)),
        mock.call(Robot.CMD_SET_ACCELERATION,
                  *([f'{int(self._acceleration)}'] * 4))
    ]
    self._robot._SendCommand.assert_has_calls(calls)

  def testSetMotorOff(self):
    # yapf: disable
    self._robot._SendCommand = mock.Mock(spec=self._robot._SendCommand)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self._robot.LoadDevice = mock.Mock(spec=self._robot.LoadDevice)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot.SetMotor(False)

    self._robot.LoadDevice.assert_called_with(False)
    self._robot._SendCommand.assert_called_with(Robot.CMD_POWER_OFF)

  def testLoadDevice(self):
    # yapf: disable
    self._robot._SendCommand = mock.Mock(spec=self._robot._SendCommand)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot.LoadDevice(True)

    self._robot._SendCommand.assert_called_with(Robot.CMD_LOAD)

  def testUnloadDevice(self):
    # yapf: disable
    self._robot._SendCommand = mock.Mock(spec=self._robot._SendCommand)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot.LoadDevice(False)

    self._robot._SendCommand.assert_called_with(Robot.CMD_UNLOAD)

  def testMoveTo(self):
    position = Robot.POSITION_ORIGIN

    # yapf: disable
    self._robot._SendCommand = mock.Mock(spec=Robot._SendCommand)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot.MoveTo(position)

    self._robot._SendCommand.assert_called_with(Robot.CMD_MOVE_TO, position,
                                                Robot.MOVEMENT_STOP)

  def testSetLEDOn(self):
    # yapf: disable
    self._robot._SendCommand = mock.Mock(spec=Robot._SendCommand)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot.SetLED(True)

    self._robot._SendCommand.assert_called_with(Robot.CMD_LED, Robot.LED_ON)

  def testSetLEDOff(self):
    # yapf: disable
    self._robot._SendCommand = mock.Mock(spec=Robot._SendCommand)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self._robot.SetLED(False)

    self._robot._SendCommand.assert_called_with(
        Robot.CMD_LED, Robot.LED_OFF)


if __name__ == '__main__':
  unittest.main()
