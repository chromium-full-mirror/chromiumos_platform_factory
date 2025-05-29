# Copyright 2018 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A factory test for gyroscopes calibration.

Description
-----------
This is a calibration test for tri-axis (x, y, and z) gyroscopes.

Test Procedure
--------------
1. Put the device (base/lid) on a static plane then press space.
2. Wait for completion.

Dependency
----------
- Device API (``cros.factory.device.gyroscope``).

Examples
--------
To run calibration on base gyroscope::

  {
    "pytest_name": "gyroscope_calibration",
    "args": {
      "location": "base"
    }
  }
"""
import enum

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.utils.arg_utils import Arg


class Gyroscope(test_case.TestCase):

  related_components = (test_case.TestCategory.ACCELEROMETER, )
  ARGS = [
      Arg('capture_count', int,
          'Number of records to read to compute the average.', default=100),
      Arg('gyro_id', int,
          'Gyroscope ID.  Will read a default ID via ectool if not set.',
          default=None),
      Arg(
          'freq', int,
          'Gyroscope sampling frequency in mHz.  Will apply the minimal '
          'frequency from ectool info if not set.', default=None),
      Arg('sample_rate', int,
          'Sample rate in Hz to read data from the gyroscope sensor.',
          default=20),
      Arg('setup_time_secs', int, 'Seconds to wait before starting the test.',
          default=2),
      Arg('autostart', bool, 'Auto start this test.', default=True),
      Arg('setup_sensor', bool, 'Setup gyro sensor via ectool', default=True),
      Arg('location', enum.Enum('location', ['base', 'lid']),
          'Gyro is located in "base" or "lid".', default='base'),
      Arg('is_ish_enabled', bool, 'Whether the sensor data is sourced via ISH',
          default=False)
  ]

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    self.gyroscope = self.dut.gyroscope.GetController(
        # yapf: disable
        location=self.args.location,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        gyro_id=self.args.gyro_id,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        freq=self.args.freq)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.ToggleTemplateClass('font-large', True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def runTest(self):
    # yapf: disable
    if self.args.setup_sensor:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.gyroscope.SetupMotionSensor(
          is_ish_enabled=self.args.is_ish_enabled)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    # yapf: disable
    if not self.args.autostart:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          _('Please put device on a static plane then press space to '
            'start calibration.'))
      # yapf: disable
      self.ui.WaitKeysOnce(test_ui.SPACE_KEY)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # yapf: disable
    for i in range(self.args.setup_time_secs):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          _('Calibration will be started within {secs} seconds.'
            'Please do not move the device.',
            # yapf: disable
            secs=self.args.setup_time_secs - i))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.Sleep(1)

    # yapf: disable
    self.ui.SetState(_('Please do not move the device.'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.gyroscope.CleanUpCalibrationValues()
    # yapf: disable
    raw_data = self.gyroscope.GetData(self.args.capture_count,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
                                      # yapf: enable
                                      # yapf: disable
                                      self.args.sample_rate)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    calib_bias = self.gyroscope.CalculateCalibrationBias(raw_data)
    self.gyroscope.UpdateCalibrationBias(calib_bias)
