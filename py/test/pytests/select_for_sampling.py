# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Decide if this device is selected for certain sampling tests.

Description
-----------
For some sampling tests, the tests should only be run for a subset of
DUTs by a given sampling rate. This test uses a hash of the WLAN MAC
address (wlan0 or mlan0) to decide if we should sample this device or
not, and writes a "True" or "False" to the device data with the
(optionally) specified key.

Test Procedure
--------------
This is an automated test without user interaction.

Dependency
----------
Need the device to have a WiFi interface with non-fixed MAC address.

Examples
--------
To select about 10% of the devices and mark devices selected as
'selected_for_sampling' in device data, add this in test list::

  {
    "pytest_name": "select_for_sampling",
    "args": {
      "rate": 0.1
    }
  }

To select about 20% of the devices, and mark using 'run_audio' key::

  {
    "pytest_name": "select_for_sampling",
    "args": {
      "rate": 0.2,
      "device_data_key": "run_audio"
    }
  }
"""

import hashlib
import logging
import unittest

from cros.factory.test import device_data
from cros.factory.test import event_log  # TODO(chuntsen): Deprecate event log.
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import net_utils


class SelectForSamplingTest(unittest.TestCase):
  # yapf: disable
  related_components = tuple()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  ARGS = [
      Arg('rate', float,
          'Sampling rate (0 to never select any devices, 1 to select all, '
          '0.2 to select 20% of devices, etc.)'),
      Arg('device_data_key', str,
          'Key in the device data dictionary',
          default='selected_for_sampling'),
  ]

  def runTest(self):
    # yapf: disable
    self.assertGreaterEqual(self.args.rate, 0.0)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.assertLessEqual(self.args.rate, 1.0)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    mac_address = net_utils.GetWLANMACAddress()
    digest = hashlib.md5(mac_address.encode('utf-8')).hexdigest()
    value = int(digest, 16)

    max_value = 16 ** len(digest)
    fraction = value / max_value

    # yapf: disable
    selected = fraction < self.args.rate  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    logging.info('MAC address hash (as a fraction of 1): %.5f', fraction)
    # yapf: disable
    logging.info('Sampling rate: %.5f', self.args.rate)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    logging.info('Selected: %r', selected)

    event_log.Log('select_for_sampling',
                  # yapf: disable
                  device_data_key=self.args.device_data_key,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
                  # yapf: enable
                  # yapf: disable
                  fraction=fraction, rate=self.args.rate, selected=selected)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    testlog.LogParam('selected', selected)
    # yapf: disable
    testlog.CheckNumericParam('fraction', fraction, max=self.args.rate)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # yapf: disable
    device_data.UpdateDeviceData({self.args.device_data_key: selected})  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
