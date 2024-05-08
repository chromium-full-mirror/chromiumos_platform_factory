# Copyright 2019 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""A factory test for reading accelerometers

Description
-----------
This is a test to check if values read back from accelerometers are within a
certain range.  If we put it on a flat table we can get (x, y, z) = (0, 0, 9.8)
at an ideal case. For upside down we'll have (x, y, z) = (0, 0, -9.8).

Since accelerometer is very sensitive, the digital output will be different
for each query. For example, (0.325, -0.278, 9.55).
In addition, temperature or the assembly quality may impact the accuracy
of the accelerometer during manufacturing (ex, position is tilt). To mitigate
this kind of errors, we'll sample several records of raw data and compute
its average value under an ideal environment.

Test Procedure
--------------
1. The test will auto start unless argument `autostart` is false, otherwise, it
   will wait for operators to press `SPACE`.
2. Check if values are within the threshold, pass / fail automatically.

Dependency
----------
- Device API (``cros.factory.device.accelerometer``)

Examples
--------
If the device is expected to be place horizontally on desk, this test can be
added as simple as:

.. test_list::

  generic_ec_component_accel_examples:BaseAccelerometers

.. test_list::

  generic_ec_component_accel_examples:LidAccelerometers

You can also change the limits of each axis to loose the criteria:

.. test_list::

  generic_ec_component_accel_examples:BaseAccelerometersLooserLimits

"""

import enum

from cros.factory.device import accelerometer
from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg


DEFAULT_LIMITS = {
    'x': [-0.5, 0.5],
    'y': [-0.5, 0.5],
    'z': [8.8, 10.8],
}


class AccelerometersTest(test_case.TestCase):
  related_components = (test_case.TestCategory.ACCELEROMETER, )
  ARGS = [
      Arg(
          'autostart', bool,
          'If this is false, this test will not start until operators press '
          'space', default=True),
      Arg(
          'limits', dict,
          'A dictionary of expected range for x, y, z values.  For example, '
          '{"x": [-0.5, 0.5], "y": [-0.5, 0.5], "z": [8.8, 10.8]}',
          default=None),
      Arg('sample_rate_hz', int, 'The sample rate in Hz to get raw data from '
          'accelerometers.', default=20),
      Arg(
          'capture_count', int, 'How many times to capture the raw data to '
          'calculate the average value.', default=100),
      Arg('setup_time_secs', int, 'How many seconds to wait before starting '
          'to calibration.', default=2),
      Arg('location', enum.Enum('location', ['base', 'lid']),
          'The location for the accelerometer', default='base'),
  ]

  def setUp(self):
    # yapf: disable
    self.ui.ToggleTemplateClass('font-large', True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # yapf: disable
    if self.args.limits is None:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.args.limits = DEFAULT_LIMITS  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    # yapf: disable
    assert self.args.limits.keys() == {'x', 'y', 'z'}, (  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        'Limits should be a dictionary with keys "x", "y" and "z"')
    # yapf: disable
    for unused_axis, [limit_min, limit_max] in self.args.limits.items():  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      assert limit_min <= limit_max

    self.dut = device_utils.CreateDUTInterface()
    self.accelerometer_controller = (
        # yapf: disable
        self.dut.accelerometer.GetController(self.args.location))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def runTest(self):
    # yapf: disable
    if not self.args.autostart:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.SetState(_('Press SPACE to continue'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.WaitKeysOnce(test_ui.SPACE_KEY)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # Waits for a few seconds to let machine become stable.
    # yapf: disable
    for i in range(self.args.setup_time_secs):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          _('Test will be started within {secs} seconds. '
            'Please do not move the device.',
            # yapf: disable
            secs=self.args.setup_time_secs - i))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.Sleep(1)

    # yapf: disable
    self.ui.SetState(_('Test is in progress, please do not move the device.'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    try:
      # yapf: disable
      raw_data = self.accelerometer_controller.GetData(self.args.capture_count)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    except accelerometer.AccelerometerException:
      self.FailTask('Read raw data failed.')

    passed = True
    # yapf: disable
    for axis, [limit_min, limit_max] in self.args.limits.items():  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      key = 'in_accel_' + axis  # in_accel_(x|y|z)
      passed &= testlog.CheckNumericParam(
          name=key, value=raw_data[key], min=limit_min, max=limit_max)
    if not passed:
      self.FailTask(f'Sensor value out of limit {raw_data!r}')
