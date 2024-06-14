# Copyright 2014 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A basic battery test.

Description
-----------
This is a basic battery test that charges and discharges the battery on DUT.
The goal of this factory test is to perform a quick basic verification of
battery functions (typically less than 30 seconds).

Test Procedure
--------------
1. Prompt the operator to plug in the AC power source.
2. The battery current is sampled periodically, and its value is checked.
3. Prompt the operator to unplug the AC power source.
4. The battery current is sampled periodically, and its value is checked.
5. Prompt the operator to plug in the AC power source, again.
6. The battery current is sampled periodically, and its value is checked.

Dependency
----------
Depend on the sysfs driver to control and read information from the battery.

Examples
--------
To perform a basic battery test, add this in test list:

.. test_list::

  generic_battery_examples:BatteryTests.BatteryBasic

To relax the limitation of battery cycle count to 5:

.. test_list::

  generic_battery_examples:BatteryTests.BatteryBasicCycleCountAtMost5

"""

import logging

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.test.utils import stress_manager
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import sync_utils
from cros.factory.utils import time_utils


class SimpleBatteryTest(test_case.TestCase):
  """A simple battery test."""
  related_components = (test_case.TestCategory.BATTERY, )
  ARGS = [
      Arg('charge_duration_secs', type=(int, float), default=5,
          help='the duration in seconds to charge the battery'),
      Arg('discharge_duration_secs', type=(int, float), default=5,
          help='the duration in seconds to discharge the battery'),
      Arg('min_charge_current_mA', type=(int, float), default=None,
          help=('the minimum charge current in mA that the battery needs to '
                'reach during charge test')),
      Arg('min_discharge_current_mA', type=(int, float), default=-2000,
          help=('the minimum discharge current in mA that the battery needs to '
                'reach during discharge test')),
      Arg('current_sampling_period_secs', type=(int, float), default=0.5,
          help=('the period in seconds to sample charge/discharge current '
                'during test')),
      Arg('max_cycle_count', type=int, default=1,
          help=('the maximum cycle count beyond which the battery is considered'
                'used')),
  ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()

    # yapf: disable
    if self.args.min_charge_current_mA:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.assertGreater(self.args.min_charge_current_mA, 0,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
                         'min_charge_current_mA must be greater than zero')

    # yapf: disable
    if self.args.min_discharge_current_mA:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.assertLess(self.args.min_discharge_current_mA, 0,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
                      'min_discharge_current_mA must be less than zero')

    # yapf: disable
    self.ui.ToggleTemplateClass('font-large', True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def SampleBatteryCurrent(self, duration_secs):
    """Samples battery current for a given duration.

    Args:
      duration_secs: The duration in seconds to sample battery current.

    Returns:
      A list of sampled battery current.
    """
    sampled_current = []
    end_time = time_utils.MonotonicTime() + duration_secs
    while time_utils.MonotonicTime() < end_time:
      sampled_current.append(self._dut.power.GetBatteryCurrent())
      # yapf: disable
      self.Sleep(self.args.current_sampling_period_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    logging.info('Sampled battery current: %s', sampled_current)
    return sampled_current

  def TestCharge(self, duration_secs):
    """Tests battery charging for a given duration.

    Args:
      duration_secs: The duration in seconds to test charging the battery.

    Raises:
      TestFailure if the sampled battery charge current does not pass
      the given threshold in dargs.
    """
    # yapf: disable
    self.ui.SetState(_('Plug AC to proceed'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    sync_utils.WaitFor(self._dut.power.CheckACPresent, timeout_secs=10)

    # yapf: disable
    self.ui.SetState(_('Testing battery charge...'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self._dut.power.SetChargeState(self._dut.power.ChargeState.CHARGE)
    sampled_current = self.SampleBatteryCurrent(duration_secs)

    # yapf: disable
    if self.args.min_charge_current_mA:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.assertGreaterEqual(
          # yapf: disable
          max(sampled_current),
          self.args.min_charge_current_mA,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          # yapf: disable
          f'Battery charge current did not reach defined threshold '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          f'{self.args.min_charge_current_mA:f} mA')
    else:
      self.assertGreater(
          max(sampled_current), 0,
          'Battery was not charging during charge test')

  def TestDischarge(self, duration_secs):
    """Tests battery discharging for a given duration.

    The test runs under high system load to maximize battery discharge current.

    Args:
      duration_secs: The duration in seconds to test discharging the battery.

    Raises:
      TestFailure if the sampled battery discharge current does not pass
      the given threshold in dargs.
    """
    # yapf: disable
    self.ui.SetState(_('Unplug AC to proceed'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    sync_utils.WaitFor(lambda: not self._dut.power.CheckACPresent(),
                       timeout_secs=10)

    # yapf: disable
    self.ui.SetState(_('Testing battery discharge...'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # Discharge under high system load.
    with stress_manager.StressManager(self._dut).Run(duration_secs):
      sampled_current = self.SampleBatteryCurrent(duration_secs)

    # yapf: disable
    if self.args.min_discharge_current_mA:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.assertLessEqual(
          # yapf: disable
          min(sampled_current),
          self.args.min_discharge_current_mA,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          # yapf: disable
          f'Battery discharge current did not reach defined threshold '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          f'{self.args.min_discharge_current_mA:f} mA')
    else:
      self.assertLess(
          min(sampled_current), 0,
          'Battery was not discharging during charge test')

  def runTest(self):
    self.assertTrue(self._dut.power.CheckBatteryPresent(),
                    'Cannot locate battery sysfs path. Missing battery?')

    cycle_count = self._dut.power.GetBatteryCycleCount()
    self.assertLessEqual(
        # yapf: disable
        cycle_count,
        self.args.max_cycle_count,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        f'Battery cycle count {int(cycle_count)} exceeds max '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        f'{int(self.args.max_cycle_count)}')

    # yapf: disable
    self.TestCharge(self.args.charge_duration_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.TestDischarge(self.args.discharge_duration_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.TestCharge(self.args.charge_duration_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
