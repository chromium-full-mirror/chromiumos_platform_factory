# -*- coding: utf-8 -*-
#
# Copyright 2015 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tests screen rotation through ChromeOS and accelerometer data.

Description
-----------
Tests that the accelerometer data matches the orientation when the device is
physically rotated.

Test Procedure
--------------
1. A picture would be shown on the screen. Operator should rotate the tablet to
   align with the image. This would repeat four times with each orientations,
   and the test automatically pass when the desired orientation is reached.

Dependency
----------
``chrome.display.system.getInfo`` in Chrome extension to get screen
information. Refer to https://developer.chrome.com/apps/system_display for
more information.

``cros.factory.device.accelerometer`` is used to determine device orientation.

Examples
--------
To test screen rotation, and have a timeout of an hour:

.. test_list::

  generic_ec_component_accel_examples:AccelerometerIMUTests.TabletRotation

To provide more parameters for accelerometer when testing:

.. test_list::

  generic_ec_component_accel_examples:AccelerometerIMUTests.
  ScreenRotation.TabletRotationAll

To test screen rotation for Chrome and prompt operator to flip before and after
the test, we can combine the test with `tablet_mode.py <./tablet_mode.html>`_:

.. test_list::

  generic_ec_component_accel_examples:AccelerometerIMUTests.ScreenRotation

"""

import enum
import math

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import state
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils.schema import JSONSchemaDict


_TEST_DEGREES = ['90', '180', '270', '0']
_POLL_ROTATION_INTERVAL = 0.01
_VALID_LOCATIONS = ['base', 'lid']
_RADIAN_TO_DEGREE = 180 / math.pi

_ARG_DEGREES_TO_ORIENTATION_SCHEMA = JSONSchemaDict(
    'degrees_to_orientation schema object', {
        'type': 'object',
        'patternProperties': {
            '(base|lid)': {
                'type': 'object',
                'patternProperties': {
                    '(0|90|180|270)': {
                        'type': 'object',
                        'patternProperties': {
                            'in_accel_(x|y|z)': {
                                'enum': [0, 1, -1]
                            }
                        },
                        'additionalProperties': False
                    }
                },
                'additionalProperties': False
            }
        },
        'additionalProperties': False
    })


class TabletRotationTest(test_case.TestCase):
  """Tablet rotation factory test."""
  related_components = (test_case.TestCategory.ACCELEROMETER, )
  ARGS = [
      Arg('timeout_secs', int, 'Timeout value for the test.', default=30),
      Arg(
          'degrees_to_orientations', dict,
          'The keys should be "base" or "lid", which are the locations of the '
          'accelerometer. And each value is a dict of (key, value) pair as '
          'follows: '
          'Keys: degrees of the orientations, ["0", "90", "180", "270"]. '
          'Values: a dictionary containing orientation configuration.  Keys '
          'should be the name of the accelerometer signal. The possible keys '
          'are "in_accel_(x|y|z)". Values should be one of [0, 1, -1], '
          'representing the ideal value for gravity under such orientation.',
          default={
              'base': {
                  '0': {
                      'in_accel_x': 0,
                      'in_accel_y': -1,
                      'in_accel_z': 0
                  },
                  '90': {
                      'in_accel_x': 1,
                      'in_accel_y': 0,
                      'in_accel_z': 0
                  },
                  '180': {
                      'in_accel_x': 0,
                      'in_accel_y': 1,
                      'in_accel_z': 0
                  },
                  '270': {
                      'in_accel_x': -1,
                      'in_accel_y': 0,
                      'in_accel_z': 0
                  }
              },
              'lid': {
                  '0': {
                      'in_accel_x': 0,
                      'in_accel_y': 1,
                      'in_accel_z': 0
                  },
                  '90': {
                      'in_accel_x': 1,
                      'in_accel_y': 0,
                      'in_accel_z': 0
                  },
                  '180': {
                      'in_accel_x': 0,
                      'in_accel_y': -1,
                      'in_accel_z': 0
                  },
                  '270': {
                      'in_accel_x': -1,
                      'in_accel_y': 0,
                      'in_accel_z': 0
                  }
              }
          }, schema=_ARG_DEGREES_TO_ORIENTATION_SCHEMA),
      Arg(
          'spec_offset', list, 'Two numbers, ex: [1.5, 1.5] '
          'indicating the tolerance for the digital output of sensors under '
          'zero gravity and one gravity.', default=[1, 1]),
      Arg('sample_rate_hz', int, 'The sample rate in Hz to get raw data from '
          'accelerometers.', default=200),
      Arg('mode', enum.Enum('mode', ['classic', 'animation']),
          'The mode for showing instruction of the test', default='classic'),
  ]

  def setUp(self):
    self.accel_controllers = {}
    self.dut = device_utils.CreateDUTInterface()
    # yapf: disable
    for location, dic in self.args.degrees_to_orientations.items():  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.accel_controllers[location] = self.dut.accelerometer.GetController(
          location=location)
      if (not set(dic).issubset(set(_TEST_DEGREES)) or
          location not in _VALID_LOCATIONS):
        self.fail(
            'Please provide proper arguments for degrees_to_orientations.')

    self.state = state.GetInstance()
    self._SetInternalDisplayRotation(0)

  def tearDown(self):
    self._SetInternalDisplayRotation(-1)

  def _GetInternalDisplayInfo(self):
    display_info = self.state.DeviceGetDisplayInfo()
    display_info = [info for info in display_info if info['isInternal']]
    if len(display_info) != 1:
      self.fail('Failed to get internal display.')
    return display_info[0]

  def _SetInternalDisplayRotation(self, degree):
    # degree should be one of [0, 90, 180, 270, -1], where -1 means auto-rotate
    display_id = self._GetInternalDisplayInfo()['id']
    self.state.DeviceSetDisplayProperties(display_id, {"rotation": degree})

  def _SetStyle(self, div_id, key, value):
    # yapf: disable
    self.ui.RunJS(f'document.getElementById("{div_id}")'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                  f'.style.{key} = "{value}"')

  def _PromptAndWaitForRotation(self, degree, need_test_locations):
    while need_test_locations:
      self.Sleep(_POLL_ROTATION_INTERVAL)
      if not self._GetInternalDisplayInfo()['isAutoRotationAllowed']:
        # Auto rotation is allowed when the device is in a physical tablet
        # state or kSupportsClamshellAutoRotation is set.
        # So, if kSupportsClamshellAutoRotation is set, the value would be
        # true even if the tablet mode switch is off (false).
        # But this should be fine, because we will run the "tablet_mode" test
        # before running this test, and the test will check the "tablet mode
        # switch" in evtest.
        # To set the `kSupportsClamshellAutoRotation`, one can edit the
        # `init/goofy.d/chrome_dev.conf` and add one line to enable the option
        # `--supports-clamshell-auto-rotation`.
        self.fail('Auto rotation is not allowed.')

      # yapf: disable
      for loc, dic in self.args.degrees_to_orientations.items():  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        if loc not in need_test_locations:
          continue
        orientations = dic[degree]
        cal_data = self.accel_controllers[loc].GetData(
            # yapf: disable
            sample_rate=self.args.sample_rate_hz)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        if self.args.mode == "animation":  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          rotate_x, rotate_y, rotate_z = self.CalculateRotateDegree(
              loc, cal_data)
          self.RotateImage(loc, rotate_x, rotate_y, rotate_z)

        if self.accel_controllers[loc].IsWithinOffsetRange(
            # yapf: disable
            cal_data, orientations, self.args.spec_offset):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          need_test_locations.remove(loc)
          self._SetStyle(loc, 'color', 'green')

  def runTest(self):
    # yapf: disable
    self.ui.StartFailingCountdownTimer(self.args.timeout_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.SetInstruction(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        _('Rotate the tablet to correctly align the picture, holding it at '
          'an upright 90-degree angle.'))
    self.SetImageAndMode('chromebook_lid_rotate.png',
                         'chromebook_base_rotate.png', 'chromebook_lid.png',
                         'chromebook_base.png')
    for degree in _TEST_DEGREES:
      need_test_locations = set()
      # yapf: disable
      for loc, dic in self.args.degrees_to_orientations.items():  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        if degree not in dic:
          self._SetStyle(loc, 'display', 'none')
          continue
        need_test_locations.add(loc)
        self._SetStyle(loc, 'color', '')
        self._SetStyle(loc, 'transform', f'rotate({degree}deg)')
        self._SetStyle(loc, 'display', 'block')
        self._SetStyle(f'{loc}_instruction', 'rotate', f'z {90-int(degree)}deg')
        self._SetStyle(f'{loc}_instruction', 'display', 'inline-block')
        self._SetStyle(f'chromebook_{loc}', 'display', 'inline-block')
      if not need_test_locations:
        continue

      # yapf: disable
      self.ui.SetView('main')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self._PromptAndWaitForRotation(degree, need_test_locations)
      # yapf: disable
      self.ui.SetView('success')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.Sleep(1)

  def SetImageAndMode(self, lid_instruction_url, base_instruction_url, lid_url,
                      base_url):
    """Sets the image src and the display mode."""
    # yapf: disable
    self.ui.RunJS('document.getElementById("lid_instruction").src = args.url;',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                  url=lid_instruction_url)
    # yapf: disable
    self.ui.RunJS('document.getElementById("base_instruction").src = args.url;',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                  url=base_instruction_url)
    # yapf: disable
    self.ui.RunJS('document.getElementById("chromebook_lid").src = args.url;',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                  url=lid_url)
    # yapf: disable
    self.ui.RunJS('document.getElementById("chromebook_base").src = args.url;',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                  url=base_url)

    # yapf: disable
    if self.args.mode == 'classic':  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self._SetStyle('animation', 'display', 'none')
    # yapf: disable
    elif self.args.mode == 'animation':  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self._SetStyle('classic', 'display', 'none')

  def RotateImage(self, loc, degree_x, degree_y, degree_z):
    """Rotates the image according to the degree captured."""
    if loc == 'lid':
      self._SetStyle(
          'chromebook_lid', 'transform', f'rotateX({degree_x}deg) '
          f'rotateY({degree_y}deg) rotateZ({degree_z}deg)')
    elif loc == 'base':
      self._SetStyle(
          'chromebook_base', 'transform', f'rotateX({degree_x}deg) '
          f'rotateY({degree_y}deg) rotateZ({degree_z}deg)')

  def CalculateRotateDegree(self, loc, cal_data):
    accel_x = cal_data['in_accel_x']
    accel_y = cal_data['in_accel_y']
    accel_z = cal_data['in_accel_z']
    degree_x = int(math.atan2(accel_y, accel_z) * _RADIAN_TO_DEGREE)
    degree_y = int(math.atan2(accel_x, accel_z) * _RADIAN_TO_DEGREE)
    degree_z = int(math.atan2(accel_y, accel_x) * _RADIAN_TO_DEGREE)
    if loc == 'lid':
      degree_x, degree_y, degree_z = 0, 0, degree_z - 90
    elif loc == 'base':
      degree_x, degree_y, degree_z = 0, 0, -90 - degree_z
    return degree_x, degree_y, degree_z
