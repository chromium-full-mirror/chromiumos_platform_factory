# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This is a factory test to check the LED brightness.

Description
-----------

This test is to test LED functionality.

Test Procedure
--------------

1. Changes the brightness and color of the specific LED.
2. Operators decide pass or fail.

Dependency
----------
- Device API ``cros.factory.device.led.SetColor``.

Examples
--------
An example::

  {
    "pytest_name": "brightness.led_brightness",
    "args": {
      "msg": "Check if the LED color is correct",
      "interval_secs": 1,
      "led_name": "LEFT",
      "levels": [1, 2]
    }
  }
"""

from cros.factory.device import led as led_module
from cros.factory.test.pytests.brightness import brightness
from cros.factory.test import test_tags
from cros.factory.utils import arg_utils
from cros.factory.utils.arg_utils import Arg


LEDColor = led_module.LED.Color


class LEDBrightnessTestArgs(brightness.BrightnessTestArgs):
  led_name: str
  color: str



class LEDBrightnessTest(brightness.BrightnessTest):
  related_components = (test_tags.TestCategory.LED, )

  ARGS = arg_utils.MergeArgs(brightness.BrightnessTest.ARGS, [
      Arg('led_name', str, 'The name of the LED to test.', default='battery'),
      Arg('color', str, 'The color to test.', default=LEDColor.WHITE)])

  args: LEDBrightnessTestArgs

  def tearDown(self):
    self.dut.led.SetColor(LEDColor.AUTO, led_name=self.args.led_name)

  def _SetBrightnessLevel(self, level):
    self.dut.led.SetColor(self.args.color, led_name=self.args.led_name,
                          brightness=level)
