# Copyright 2020 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Connect to an AP.

Description
-----------
Connect to an AP.

Test Procedure
--------------
Auto.

Dependency
----------
- connection_manager goofy plugin

Examples
--------
To run this test on DUT, add a test item in the test list:

.. test_list::

  generic_wireless_examples:WirelessTests.ExampleWirelessConnect2G

To disconnect to all WiFi services.:

.. test_list::

  generic_wireless_examples:WirelessTests.WirelessDisconnect

"""

import re
from typing import List, Optional

from cros.factory.device import device_utils
from cros.factory.goofy.plugins import plugin_controller
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import sync_utils
from cros.factory.utils import type_utils


SSID_RE = re.compile('SSID: (.*)$', re.MULTILINE)


class WirelessConnectTestArgs:
  device_name: Optional[str]
  service_name: List[dict]
  retries: int
  sleep_interval: int


class WirelessConnectTest(test_case.TestCase):
  """Basic wireless test class."""
  related_components = tuple()
  ARGS = [
      Arg('device_name', str, 'The wifi interface', default=None),
      Arg('service_name', list,
          'A list of wlan config. See net_utils.WLAN for more information',
          default=[]),
      Arg('retries', int, 'Times to retry.', default=10),
      Arg('sleep_interval', int, 'Time to sleep.', default=3)
  ]
  args: WirelessConnectTestArgs

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self._device_name = None
    self._connection_manager = plugin_controller.GetPluginRPCProxy(
        'connection_manager')

  def _CheckConnected(self, ssid_list: List[str]) -> bool:
    result = self._dut.CheckOutput(['iw', 'dev', self._device_name, 'link'],
                                   log=True)
    match = SSID_RE.search(result)
    if match and match.group(1) in ssid_list:
      return True
    return False

  def _CheckNotConnected(self):
    result = self._dut.CheckOutput(['iw', 'dev', self._device_name, 'link'],
                                   log=True)
    return result.startswith('Not connected.')

  def runTest(self):
    self._device_name = self._dut.wifi.SelectInterface(self.args.device_name)
    session.console.info('Selected device_name is %s.', self._device_name)
    services = self.args.service_name
    session.console.info('service = %r', services)
    self._connection_manager.Reconnect(services)
    ssid_list = [service.get('ssid') for service in services]

    retry_wrapper = sync_utils.RetryDecorator(
        max_attempt_count=self.args.retries,
        interval_sec=self.args.sleep_interval, target_condition=bool)

    try:
      if ssid_list:
        retry_wrapper(self._CheckConnected)(ssid_list)
      else:
        retry_wrapper(self._CheckNotConnected)()
    except type_utils.MaxRetryError:
      self.FailTask('Reach maximum retries.')
    else:
      self.PassTask()
