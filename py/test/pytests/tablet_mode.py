# Copyright 2015 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tests that certain conditions are met when in tablet mode.

Description
-----------
Currently, it check that the lid switch is not triggered and tablet mode event
is triggered and in correct state.

Turning devices into tablet mode exercises the GMR sensor and the accelerometer.

Test Procedure
--------------

1. If prompt_flip_tablet is set:

  1. The operator flips the device to make it enter tablet mode.
  2. The operator clicks the button by using touch screen or external mouse.

2. If prompt_flip_notebook is set:

  1. The operator flips the device to make it enter notebook mode.
  2. The operator presses the space key.

Dependency
----------

* cros.factory.external.py_lib.evdev
* cros.factory.test.utils.evdev_utils

Examples
--------
To run the test, add this in test list:

.. test_list::

  generic_ec_component_accel_examples:AccelerometerIMUTests.
  GoToTabletModeAndGoBack

Set lid_filter to choose the lid sensor explicitly:

.. test_list::

  generic_ec_component_accel_examples:AccelerometerIMUTests.
  GoToTabletModeAndGoBackSetLid

To test screen rotation for Chrome and prompt operator to flip before and after
the test, we can combine the test with
`tablet_rotation.py <./tablet_rotation.html>`_:

.. test_list::

  generic_ec_component_accel_examples:AccelerometerIMUTests.ScreenRotation

"""

import logging

from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test.utils import evdev_utils
from cros.factory.utils.arg_utils import Arg

from cros.factory.external.py_lib import evdev


def FormatMultipleDevicesMessages(arg_name, candidates):
  """Returns message to guide partner for potential solution."""
  _message_template = (
      'Please set the {!r} argument in the test list to be one of the {!r}')
  names = [candidate.name for candidate in candidates]
  return _message_template.format(arg_name, names)


class TabletModeTest(test_case.TestCase):
  """Tablet mode factory test."""
  related_components = (test_case.TestCategory.ACCELEROMETER, )
  ARGS = [
      Arg('timeout_secs', int, 'Timeout value for the test.', default=30),
      Arg('lid_filter', (int, str),
          'Lid event ID or name for evdev. None for auto probe.',
          default=None),
      Arg('tablet_filter', (int, str),
          'Tablet event ID or name for evdev. None for auto probe.',
          default=None),
      Arg('prompt_flip_tablet', bool,
          'Assume the notebook is not yet in tablet mode, and operator should '
          'first be instructed to flip it as such. (This is useful to unset if '
          'the previous test finished in tablet mode.)',
          default=False),
      Arg('prompt_flip_notebook', bool,
          'After the test, prompt the operator to flip back into notebook '
          'mode. (This is useful to unset if the next test requires tablet '
          'mode.)',
          default=False),
  ]

  def setUp(self):
    self.tablet_mode_switch = False
    try:
      # yapf: disable
      self.lid_event_dev = evdev_utils.FindDevice(self.args.lid_filter,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
                                                  evdev_utils.IsLidEventDevice)
    except evdev_utils.MultipleDevicesFoundError as err:
      logging.exception('')
      self.FailTask(FormatMultipleDevicesMessages('lid_filter', err.candidates))

    try:
      self.tablet_event_dev = evdev_utils.FindDevice(
          # yapf: disable
          self.args.tablet_filter,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          evdev_utils.IsTabletEventDevice)
    except evdev_utils.DeviceNotFoundError:
      self.tablet_event_dev = None
    except evdev_utils.MultipleDevicesFoundError as err:
      logging.exception('')
      self.FailTask(
          FormatMultipleDevicesMessages('tablet_filter', err.candidates))

    self.assertTrue(
        # yapf: disable
        self.args.prompt_flip_tablet or self.args.prompt_flip_notebook,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        'One of prompt_flip_tablet or prompt_flip_notebook should be true.')

    # Create a thread to monitor evdev events.
    self.lid_dispatcher = evdev_utils.InputDeviceDispatcher(
        self.lid_event_dev, self.HandleSwitchEvent)
    self.lid_dispatcher.StartDaemon()
    self.tablet_dispatcher = None
    # It is possible that a single input device can support both of SW_LID and
    # SW_TABLET_MODE therefore we can just use the first thread above to
    # monitor these two EV_SW events. Or we need this second thread. Also we
    # can't have two InputDeviceDispatcher on the same device, or one of them
    # would read fail.
    # There's a bug in the python-evdev library that InputDevice only have
    # correct __eq__ operator, but not __ne__ operator, and
    # `self.tablet_event_dev != self.lid_event_dev` always return True, so we
    # need the `not (... == ...)` here.
    if self.tablet_event_dev and not (
        self.tablet_event_dev == self.lid_event_dev):
      self.tablet_dispatcher = evdev_utils.InputDeviceDispatcher(
          self.tablet_event_dev, self.HandleSwitchEvent)
      self.tablet_dispatcher.StartDaemon()

    # yapf: disable
    if self.args.prompt_flip_tablet:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.AddTask(self.FlipTabletMode)

    # yapf: disable
    if self.args.prompt_flip_notebook:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.AddTask(self.FlipNotebookMode)

  def tearDown(self):
    self.lid_dispatcher.Close()
    if self.tablet_dispatcher:
      self.tablet_dispatcher.Close()

  def HandleSwitchEvent(self, event):
    # yapf: disable
    if event.type == evdev.ecodes.EV_SW and event.code == evdev.ecodes.SW_LID:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      if event.value == 0:  # LID_OPEN
        self.ShowFailure()
        self.FailTask('Lid switch was triggered unexpectedly')

    # yapf: disable
    if (event.type == evdev.ecodes.EV_SW and  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        event.code == evdev.ecodes.SW_TABLET_MODE):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.tablet_mode_switch = event.value == 1

  def StartCountdown(self):
    # yapf: disable
    self.ui.StartFailingCountdownTimer(self.args.timeout_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def SetUIImage(self, image):
    # yapf: disable
    self.ui.SetView('main')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.RunJS(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        'document.getElementById("image").className = args.image;', image=image)

  def FlipTabletMode(self):
    self.SetUIImage('notebook-to-tablet')
    # yapf: disable
    self.ui.SetInstruction(_('Flip the lid into tablet mode'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    confirm_button = [
        '<button id="confirm-button" data-test-event="confirm-tablet">',
        _('Confirm tablet mode'), '</button>'
    ]
    # yapf: disable
    self.ui.SetHTML(confirm_button, id='confirm')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.event_loop.AddEventHandler('confirm-tablet',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                                    self.HandleConfirmTabletMode)
    self.StartCountdown()
    self.WaitTaskEnd()

  def HandleConfirmTabletMode(self, event):
    del event  # Unused.

    if self.tablet_event_dev and not self.tablet_mode_switch:
      self.ShowFailure()
      self.FailTask("Tablet mode switch is off")

    self.ShowSuccess()
    self.PassTask()

  def FlipNotebookMode(self):
    self.SetUIImage('tablet-to-notebook')
    # yapf: disable
    self.ui.SetInstruction(_('Open the lid back to notebook mode'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.SetHTML(_('Press SPACE to confirm notebook mode'), id='confirm')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # Ask OP to press space to verify the dut is in notebook mode.
    # Set virtual_key to False since the event callback should be triggered
    # from a real key press, not from a button on screen.
    # yapf: disable
    self.ui.BindKey(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        test_ui.SPACE_KEY, self.HandleConfirmNotebookMode, virtual_key=False)
    self.StartCountdown()
    self.WaitTaskEnd()

  def HandleConfirmNotebookMode(self, event):
    del event  # Unused.

    if self.tablet_event_dev and self.tablet_mode_switch:
      self.ShowFailure()
      self.FailTask('Tablet mode switch is on')

    self.ShowSuccess()
    self.PassTask()

  def _ShowStatus(self, status_label):
    # yapf: disable
    self.ui.SetView('status')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.SetHTML(status_label, id='status')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.Sleep(1)

  def ShowSuccess(self):
    self._ShowStatus(['<span class="success">', _('Success!'), '</span>'])

  def ShowFailure(self):
    self._ShowStatus(['<span class="failure">', _('Failure'), '</span>'])
