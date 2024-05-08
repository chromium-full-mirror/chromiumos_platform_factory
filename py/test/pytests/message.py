# Copyright 2014 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Displays a message.

Description
-----------
This test displays a HTML message to the operator, and wait for the operator
pressing space key to pass the test.

If ``manual_check`` is True, the operator can also press escape key to fail the
test.

If ``seconds`` is given, the test would pass automatically after ``seconds``
seconds.

Test Procedure
--------------
When started, the test will show a message and wait for operator to press space
to pass the test, or press escape to fail the test (if ``manual_check`` is set).

Dependency
----------
None.

Examples
--------
To show a message, add this in test list::

  {
    "pytest_name": "message",
    "args": {
      "html": "i18n! Hello world!"
    }
  }

To show a message with some formatting, and give operator ability to fail the
test::

  {
    "pytest_name": "message",
    "args": {
      "text_size": 300,
      "manual_check": true,
      "show_press_button_hint": true,
      "html": "i18n! Please check if the result is <b>correct</b>.",
      "text_color": "red"
    }
  }

To show a message for 20 seconds, and automatically pass::

  {
    "pytest_name": "message",
    "args": {
      "seconds": 20,
      "html": "i18n! Waiting for something..."
    }
  }
"""

from cros.factory.test.i18n import _
from cros.factory.test.i18n import arg_utils as i18n_arg_utils
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg


CSS_TEMPLATE = """
.message { font-size: %(text_size)s%%; color: %(text_color)s; }
test-template { --template-background-color: %(background_color)s; }
"""


class MessageTest(test_case.TestCase):
  """A factory test to display a message."""
  related_components = tuple()

  ARGS = [
      i18n_arg_utils.I18nArg('html', 'Message in HTML'),
      Arg('text_size', str, 'size of message in percentage', default='200'),
      Arg('text_color', str, 'color of message (in CSS)', default='black'),
      Arg('background_color', str, 'background color (in CSS)',
          default='white'),
      Arg('seconds', int, 'duration to display message. '
          'Specify None to show until key press.',
          default=None),
      Arg('manual_check', bool, 'If set to true, operator can press ESC to '
          'fail the test case.', default=False),
      Arg('show_press_button_hint', bool, 'If set to true, will show '
          'addition message to ask operators to press the button.',
          default=False)
  ]

  def setUp(self):
    css = (CSS_TEMPLATE %
           # yapf: disable
           dict(text_size=self.args.text_size,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
                # yapf: enable
                # yapf: disable
                text_color=self.args.text_color,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
                # yapf: enable
                # yapf: disable
                background_color=self.args.background_color))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.AppendCSS(css)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    press_button_hint = ''
    # yapf: disable
    if self.args.show_press_button_hint:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      if self.args.manual_check:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        press_button_hint = _(
            '<div>Press <strong>Enter</strong> to continue, '
            'or <strong>ESC</strong> if things are not going right.</div>')
      else:
        press_button_hint = _(
            '<div>Press <strong>Enter</strong> to continue.</div>')

    # yapf: disable
    self.ui.SetState([  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        '<span class="message">', self.args.html, '</span>', press_button_hint  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
    ])

    # yapf: disable
    self.ui.BindStandardPassKeys()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    if self.args.manual_check:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.BindStandardFailKeys()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

  def runTest(self):
    # yapf: disable
    if self.args.seconds:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.StartCountdownTimer(self.args.seconds, self.PassTask)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    self.WaitTaskEnd()
