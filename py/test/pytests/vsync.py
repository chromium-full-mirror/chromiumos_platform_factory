# Copyright 2018 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""VSync pin test.

Description
-----------
This pytest test if VSync pin is connected to EC and camera can receive VSync
signal.

Internal References
^^^^^^^^^^^^^^^^^^^
- `b/146452722 <http://b/146452722>`_
- `2021-2H_rfp_announcement <https://chromeos.google.com/partner/dlm/docs/\
device-rfp/2021-2H_rfp_announcement.html>`_

Test Procedure
--------------
This is an automatic test that doesn't need any user interaction.

Dependency
----------
- Yet Another V4L2 Test Application (``yavta``)

Examples
--------
To run a VSync pin test, add this in test list::

  {
    "pytest_name": "vsync"
  }
"""


import os
import stat

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.test.utils import camera_utils
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import sync_utils
from cros.factory.utils import type_utils


DEFAULT_CAPTURE_NUMBER = 10


class SpatialSensorCalibration(test_case.TestCase):
  related_components = (test_case.TestCategory.CAMERA, )
  ARGS = [
      Arg('capture_number', int, 'The number of capture frames.',
          default=DEFAULT_CAPTURE_NUMBER),
      Arg('camera_facing', camera_utils.CameraFacing,
          ('Direction the camera faces relative to device screen. Only allow '
           '"front", "rear" or None. None is automatically searching one.'),
          default=None),
      Arg('timeout_secs', int, 'Timeout in seconds when waiting for device.',
          default=60),
      Arg('repeat_times', int, 'Number of cycles to test.', default=5)
  ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self._vsync = self._dut.vsync_sensor.GetController()

    # yapf: disable
    self.ui.ToggleTemplateClass('font-large', True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertIsNotNone(self._vsync, 'VSync controller not found')

  def runTest(self):
    camera_path = self.GetDevicePath()
    self.WaitForDevice()
    # The "frequency" entry of a VSync sensor is actually being used as an
    # on/off switch, so this turns on the sensor.
    self._vsync.SetFrequency(1)
    start_count = 0
    # yapf: disable
    for idx in range(self.args.repeat_times):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          _('Verifying VSync pin... ({count}/{total})',
            # yapf: disable
            count=idx, total=self.args.repeat_times))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self._dut.CheckCall(
          # yapf: disable
          ['yavta', f'--capture={int(self.args.capture_number)}', camera_path])  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      end_count = self._vsync.GetCount()
      session.console.info('VSync device in_count_raw (%d/%d): %d',
                           # yapf: disable
                           idx, self.args.repeat_times, end_count)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      if not start_count + self.args.capture_number <= end_count:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        self.fail('in_count_raw is not growing')
      start_count = end_count
    # Turning off the sensor.
    self._vsync.SetFrequency(0)

  def GetDevicePath(self):
    # yapf: disable
    device_index = self._dut.camera.GetDeviceIndex(self.args.camera_facing)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    camera_path = f'/dev/video{int(device_index)}'
    if not stat.S_ISCHR(os.stat(camera_path)[stat.ST_MODE]):
      self.fail(f'{camera_path} is not a character special file')
    return camera_path

  def WaitForDevice(self):
    # yapf: disable
    self.ui.SetState(_('Waiting for device...'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    try:
      # yapf: disable
      sync_utils.WaitFor(self._dut.IsReady, self.args.timeout_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    except type_utils.TimeoutError:
      self.fail('failed to find deivce')
