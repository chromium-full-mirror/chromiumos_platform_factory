# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Compass test which requires operator place the DUT heading north and south.
"""

import enum
import math

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import sync_utils
from cros.factory.utils import type_utils


_TEST_ITEMS = [(_('north'), (0, 1)), (_('south'), (0, -1))]

_FLASH_STATUS_TIME = 1


class CompassTest(test_case.TestCase):
  related_components = tuple()
  ARGS = [
      Arg('tolerance', int, 'The tolerance in degree.', default=5),
      Arg('location', enum.Enum('Location', ['base', 'lid']),
          'Where the compass is located.', default='base')
  ]

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    self.controller = self.dut.magnetometer.GetController(
        # yapf: disable
        location=self.args.location)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def runTest(self):
    for direction_label, direction in _TEST_ITEMS:
      # yapf: disable
      self.ui.SetView('main')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.SetInstruction(_(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          'Put the DUT towards {direction}', direction=direction_label))
      sync_utils.PollForCondition(
          poll_method=type_utils.BindFunction(self._CheckDirection, direction),
          timeout_secs=1000,
          poll_interval_secs=0.1)

      # yapf: disable
      self.ui.SetView('success')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.Sleep(_FLASH_STATUS_TIME)

  def _CalculateDirection(self, x, y):
    """Calculate the absolute direction of the compass in degree.

    Args:
      x: X-axis component of the direction. X-axis points towards east.
      y: Y-axis component of the direction. Y-axis points towards north.

    Returns:
      Directed angle relative to north (0, 1), in degree, clockwise.
      For example:
          North = 0
          East = 90
          South = 180 = -180
          West = -90
    """
    rad = math.atan2(x, y)
    return rad / math.pi * 180

  def _CalculateAngle(self, x1, y1, x2, y2):
    """Calculate the angle between two vectors (x1, y1) and (x2, y2)."""
    rad = math.acos(
        (x1 * x2 + y1 * y2) / math.hypot(x1, y1) / math.hypot(x2, y2))
    return rad / math.pi * 180

  def _CheckDirection(self, expected_direction):
    values = self.controller.GetData(capture_count=1)
    x, y = values['in_magn_x'], values['in_magn_y']
    if x == 0 and y == 0:
      # atan2(0, 0) returns 0, we need to avoid this case.
      self.FailTask('Sensor outputs (0, 0), possibly not working.')
    degree = self._CalculateDirection(x, y)
    self._UpdateUI(degree=degree, **values)
    return (
        # yapf: disable
        self._CalculateAngle(x, y, *expected_direction) < self.args.tolerance)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def _UpdateUI(self, degree, in_magn_x, in_magn_y, in_magn_z):
    # yapf: disable
    self.ui.SetHTML(f'{degree:.2f}', id='degree')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.SetHTML(in_magn_x, id='in-magn-x')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.SetHTML(in_magn_y, id='in-magn-y')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.SetHTML(in_magn_z, id='in-magn-z')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.RunJS(f'document.getElementById("compass").style.transform = '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                  f'"rotate({int(degree)}deg)";')
