# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A test to check if DUT can communicate with battery.

Description
-----------
The test uses device API to get battery design capacity, and check that the
capacity lies in the range given in `design_capacity_range`.

Test Procedure
--------------
This is an automated test without user interaction.

Dependency
----------
Device API `power.GetBatteryDesignCapacity`.

This is usually implemented in `/sys` with properties like `charge_full_design`
or command `ectool battery`.

Examples
--------
To check if the battery design capacity lies in default range ([1000, 10000]),
add this in test list:

.. test_list::

  generic_battery_examples:BatteryCapacity

To check if the battery design capacity lies in [4000, 5000], add this in test
list::

.. test_list::

  generic_battery_examples:BatteryCapacityBetween4000And5000

"""

import logging
import unittest

from cros.factory.device import device_utils
from cros.factory.test import test_tags
from cros.factory.utils.arg_utils import Arg


class BatteryCommunicationTest(unittest.TestCase):
  """Tests that DUT can communicate with battery."""
  related_components = (test_tags.TestCategory.BATTERY, )
  ARGS = [
      Arg('design_capacity_range', list,
          'Expected battery design capacity range in mAh.',
          default=[1000, 10000]),
  ]

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()

  def runTest(self):
    # yapf: disable
    lower, upper = self.args.design_capacity_range  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    capacity = self.dut.power.GetBatteryDesignCapacity()
    logging.info('Get battery design capacity: %d', capacity)
    self.assertTrue(
        lower <= capacity <= upper,
        # yapf: disable
        f'Battery design capacity {int(capacity)} out of range: '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        f'{str(self.args.design_capacity_range)}')
