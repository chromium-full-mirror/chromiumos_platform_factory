# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test that waits the battery to be charged to specific level.

Description
-----------
The test waits until the battery is charged to the given level, and pass.

The ``target_charge_pct`` sets the target charge level in percentage.
``target_charge_pct`` can be set to some special values:

* ``"goofy"``: Use ``min_charge_pct`` from Goofy's charge_manager plugin as
  target charge level.
* ``"cutoff"``: Use ``CUTOFF_BATTERY_MIN_PERCENTAGE`` from cutoff.json as
  target charge level.

If ``target_charge_pct_is_delta`` is True, ``target_charge_pct`` would be
interpreted as difference to current charge level.

If battery doesn't reach the target level in ``timeout_secs`` seconds, the test
would fail.

Test Procedure
--------------
This is an automated test without user interaction.

1. A screen would be shown with current battery level, target battery level,
   and time remaining.
2. Test would pass when battery reach target level, or fail if test run longer
   than ``timeout_secs``.

Dependency
----------
Device API `cros.factory.device.power`.

Examples
--------
To charge the device to ``min_charge_pct`` in Goofy charge_manager (default
behavior), add this in test list:

.. test_list::

  generic_battery_examples:BatteryTests.BlockingCharge

To charge the device to minimum battery level needed for cutoff, add this in
test list:

.. test_list::

  generic_battery_examples:BatteryTests.BlockingChargeToCutOffSetting

To charge the device to 75 percent, add this in test list:

.. test_list::

  generic_battery_examples:BatteryTests.BlockingChargeTo75

To charge the device 10 percent more, and only allow 5 minutes time for
charging, add this in test list:

.. test_list::

  generic_battery_examples:BatteryTests.BlockingCharge10PercentMoreIn5Minutes

"""

import enum
import logging
import os
import re

from cros.factory.device import device_utils
from cros.factory.test.env import paths
from cros.factory.test import event_log  # TODO(chuntsen): Deprecate event log.
from cros.factory.test.i18n import _
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.test.utils import goofy_plugin_utils
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import config_utils
from cros.factory.utils.process_utils import CheckOutput
from cros.factory.utils.process_utils import LogAndCheckCall


_CHARGER_ERROR_KEYWORDS = ('OCP', 'OVP', 'TSD')
_DEFAULT_TARGET_CHARGE = 78


def FormatTime(seconds):
  return (f'{int(seconds // 3600)}:{int(seconds // 60 % 60):02}:'
          f'{int(seconds % 60):02}')


def MakeChargeTextLabel(start, current, target, elapsed, remaining):
  return _(
      'Charging to {target}% (Start: {start}%. Current: {current}%.)<br>'
      'Time elapsed: {elapsed} Time remaining: {remaining}',
      target=target,
      start=start,
      current=current,
      elapsed=FormatTime(elapsed),
      remaining=FormatTime(remaining))


def MakeSpriteHTMLTag(src, height, width):
  return (f'<div id="batteryIcon" style="background-image: url({src});'
          f'width: {width:d}px; height: {height:d}px; margin: auto;"></div>')


def _GetCutoffBatteryMinPercentage():
  config = config_utils.LoadConfig(
      config_name='cutoff',
      default_config_dirs=os.path.join(paths.FACTORY_DIR, 'sh', 'cutoff'))
  return config.get('CUTOFF_BATTERY_MIN_PERCENTAGE', _DEFAULT_TARGET_CHARGE)


def _GetGoofyBatteryMinPercentage():
  config = goofy_plugin_utils.GetPluginArguments('charge_manager') or {}
  return config.get('min_charge_pct', _DEFAULT_TARGET_CHARGE)


class ChargerTest(test_case.TestCase):
  related_components = (test_case.TestCategory.BATTERY, )
  ARGS = [
      Arg('target_charge_pct',
          (int, enum.Enum('TargetChargePct', ['goofy', 'cutoff'])),
          'Target charge level.', default='goofy'),
      Arg('target_charge_pct_is_delta', bool,
          'Specify target_charge_pct is a delta of current charge',
          default=False),
      Arg('timeout_secs', int, 'Maximum allowed time to charge battery',
          default=3600),
      Arg('dim_backlight', bool,
          'Turn backlight/screen brightness lower to charge faster.',
          default=True),
      Arg('dim_backlight_pct', float,
          'The brightness in linear % when charging.', default=3.0),
      Arg('log_check_interval', int, 'Period of Log checking in seconds',
          default=10),
  ]

  def setUp(self):
    self._power = device_utils.CreateDUTInterface().power

    # Group checker for Testlog.
    self._group_checker = testlog.GroupParam('charge', ['charge', 'elapsed'])

    self._ec_log = '/var/log/cros_ec.log'
    self._re_rule = re.compile('|'.join(_CHARGER_ERROR_KEYWORDS), re.IGNORECASE)
    self._last_log_size = 0

    # yapf: disable
    if self.args.dim_backlight:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # Get initial backlight brightness
      self._init_backlight_pct = float(
          CheckOutput(['backlight_tool', '--get_brightness_percent']).strip())
      LogAndCheckCall([
          'backlight_tool',
          # yapf: disable
          f'--set_brightness_percent={self.args.dim_backlight_pct:f}'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
      ])

  def tearDown(self):
    # yapf: disable
    if self.args.dim_backlight:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      LogAndCheckCall([
          'backlight_tool',
          f'--set_brightness_percent={self._init_backlight_pct:f}'
      ])

  def CheckChargerErrorLog(self):
    """Periodicly checks if the keywords of charger error show in ec log."""

    curr_log_size = os.path.getsize(self._ec_log)
    if curr_log_size < self._last_log_size:
      session.console.warning('Old log has been replaced, '
                              'will read from the beginning of the new file.')
      self._last_log_size = 0

    with open(self._ec_log, 'r', encoding='utf-8', errors='ignore') as f:
      f.seek(self._last_log_size)

      for line in f:
        result = self._re_rule.search(line)
        if result:
          self.FailTask(f'Detect {result.group()} hardware error in ec log, '
                        'please check the flex cable.')

      self._last_log_size = f.tell()

  def runTest(self):
    self.assertTrue(self._power.CheckBatteryPresent(), 'Cannot find battery.')
    self.assertTrue(self._power.CheckACPresent(), 'Cannot find AC power.')

    start_charge = self._power.GetChargePct()
    self.assertTrue(start_charge, 'Error getting battery state.')

    # yapf: disable
    target_charge = self.args.target_charge_pct  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    if self.args.target_charge_pct_is_delta:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.assertIsInstance(target_charge, int,
                            'target_charge must be int when '
                            'target_charge_pct_is_delta is True.')
      target_charge = min(target_charge + start_charge, 100)
    elif target_charge == 'cutoff':
      target_charge = _GetCutoffBatteryMinPercentage()
    elif target_charge == 'goofy':
      target_charge = _GetGoofyBatteryMinPercentage()

    logging.info('Target charge is %d%%', target_charge)
    testlog.LogParam('start_charge', start_charge)
    testlog.LogParam('target_charge', target_charge)
    if start_charge >= target_charge:
      return

    self._power.SetChargeState(self._power.ChargeState.CHARGE)
    # yapf: disable
    self.ui.SetState(MakeSpriteHTMLTag('charging_sprite.png', 256, 256))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    logging.info('Charging starting at %d%%', start_charge)
    self.event_loop.AddTimedHandler(self.CheckChargerErrorLog,
                                    self.args.log_check_interval, repeat=True)

    # yapf: disable
    for elapsed in range(self.args.timeout_secs):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      charge = self._power.GetChargePct()

      if charge >= target_charge:
        event_log.Log('charged', charge=charge, target=target_charge,
                      elapsed=elapsed)
        with self._group_checker:
          testlog.CheckNumericParam('charge', charge, min=target_charge)
          testlog.LogParam('elapsed', elapsed)
        return
      # yapf: disable
      self.ui.RunJS(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          f'document.getElementById("batteryIcon").style.backgroundPosition = '
          f'"-{int(elapsed % 4 * 256)}px 0px"')
      # yapf: disable
      self.ui.SetInstruction(MakeChargeTextLabel(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          start_charge,
          charge,
          target_charge,
          elapsed,
          # yapf: disable
          self.args.timeout_secs - elapsed))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

      if elapsed % 300 == 0:
        logging.info('Battery level is %d%% after %d minutes',
                     charge,
                     elapsed // 60)
      self.Sleep(1)

    event_log.Log('failed_to_charge', charge=charge, target=target_charge,
                  # yapf: disable
                  timeout_sec=self.args.timeout_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.FailTask(f'Cannot charge battery to {int(target_charge)}% in '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                  f'{int(self.args.timeout_secs)} seconds.')
