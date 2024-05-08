# Copyright 2020 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tests stylus garage detection functionality.

Description
-----------
Verifies if stylus garage is functional by asking operator to insert and remove
the stylus.

Test Procedure
--------------
1. Operator inserts the stylus into the stylus garage.
2. Operator removes the stylus from the stylus garage.

Dependency
----------
- Based on Linux evdev.

Examples
--------
To run default test:

.. test_list::

  generic_touchscreen_examples:StylusGarage

To test both of the stylus and the garage with a test group:

.. test_list::

  generic_touchscreen_examples:StylusAndGarage

"""

import enum

from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.test.utils import evdev_utils
from cros.factory.utils.arg_utils import Arg

from cros.factory.external.py_lib import evdev


class StylusStatus(str, enum.Enum):
  inserted = 'inserted'
  ejected = 'ejected'

  def __str__(self):
    return self.name


class StylusGarageTest(test_case.TestCase):
  """Stylus garage detection factory test."""
  related_components = (
      test_case.TestCategory.EMR_IC,
      test_case.TestCategory.USI_CONTROLLER,
  )
  ARGS = [
      Arg('timeout_secs', int, 'Timeout value for the test.', default=180),
      Arg('device_filter', (int, str),
          'Event ID or name for evdev. None for auto probe.', default=None),
      Arg('garage_is_stylus', bool,
          'Deprecated. No effect. Leave for compatibility.', default=True),
      Arg(
          'target_state', StylusStatus, 'The test passes when reaches the '
          'target state. If not specified, pass after an insertion and then '
          'an ejection or an ejection and then an insertion.', default=None),
  ]

  def setUp(self):
    filters = []
    # yapf: disable
    if self.args.device_filter is not None:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      filters.append(self.args.device_filter)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    filters.append(evdev_utils.IsStylusGarageDevice)
    self.event_dev = evdev_utils.FindDevice(*filters)
    # yapf: disable
    self.ui.ToggleTemplateClass('font-large', True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self._current_status = None
    self.dispatcher = evdev_utils.InputDeviceDispatcher(
        # yapf: disable
        self.event_dev, self.event_loop.CatchException(self.HandleEvent))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def tearDown(self):
    self.dispatcher.Close()

  def HandleEvent(self, event):
    # yapf: disable
    if (event.type == evdev.ecodes.EV_SW and  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        event.code == evdev.ecodes.SW_PEN_INSERTED):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      if event.value == 1:  # Stylus inserted
        if self._current_status == StylusStatus.inserted:
          self.FailTask('Consecutive insertion')
        elif self._current_status == StylusStatus.ejected:
          self.PassTask()
        self._current_status = StylusStatus.inserted
      elif event.value == 0:  # Stylus ejected
        if self._current_status == StylusStatus.inserted:
          self.PassTask()
        elif self._current_status == StylusStatus.ejected:
          self.FailTask('Consecutive ejection')
        self._current_status = StylusStatus.ejected

      # yapf: disable
      if self._current_status == self.args.target_state:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        self.PassTask()
      elif self._current_status == StylusStatus.inserted:
        # yapf: disable
        self.ui.SetState(_('Remove stylus'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
      else:
        # yapf: disable
        self.ui.SetState(_('Insert stylus'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable

  def runTest(self):
    # yapf: disable
    self.ui.SetState(_('Insert or Remove stylus'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.dispatcher.StartDaemon()
    # yapf: disable
    self.ui.StartFailingCountdownTimer(self.args.timeout_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.WaitTaskEnd()
