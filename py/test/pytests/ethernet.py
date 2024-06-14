# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A factory test for basic ethernet connectivity.

Description
-----------
A factory test for basic ethernet connectivity.

Test Procedure
--------------
This is an automated test without user interaction. It may require user
to press the space bar if not set to auto_start.

Dependency
----------
The pytest depends on the ethernet on the system.

Examples
--------
To use the test:

.. test_list::

  generic_ethernet_examples:EthernetTests.Ethernet

"""

import logging

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import net_utils
from cros.factory.utils import sync_utils


_LOCAL_FILE_PATH = '/tmp/test'


class EthernetTest(test_case.TestCase):
  """Test built-in ethernet port"""
  related_components = (test_case.TestCategory.ETHERNET, )
  ARGS = [
      Arg('auto_start', bool, 'Auto start option.', default=False),
      Arg('test_url', str, 'URL for testing data transmission.',
          default=None),
      Arg('md5sum', str, 'md5sum of the test file in test_url.',
          default=None),
      Arg('retry_interval_msecs', int,
          'Milliseconds before next retry.',
          default=1000),
      Arg('iface', str, 'Interface name for testing.', default=None),
      Arg('interface_name_patterns', list,
          'The ethernet interface name patterns',
          default=net_utils.DEFAULT_ETHERNET_NAME_PATTERNS),
      Arg('link_only', bool, 'Only test if link is up or not', default=False),
      Arg('use_swconfig', bool, 'Use swconfig for polling link status.',
          default=False),
      Arg('swconfig_switch', str, 'swconfig switch name.', default='switch0'),
      Arg('swconfig_ports', (int, list), 'swconfig port numbers. Either '
          'a single int or a list of int.', default=None),
      Arg('swconfig_expected_speed', (int, list),
          'expected link speed, if a list is given, each integer in the list '
          'will be paired with each port in swconfig_ports.',
          default=None)
  ]

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    # yapf: disable
    self.ui.ToggleTemplateClass('font-large', True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        _('Please plug ethernet cable into built-in ethernet port<br>'
          'Press space to start.'))

    # yapf: disable
    if bool(self.args.test_url) != bool(self.args.md5sum):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      raise ValueError('Should both assign test_url and md5sum.')
    # yapf: disable
    if self.args.use_swconfig:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      if not self.args.link_only:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        raise ValueError('Should set link_only=True if use_swconfig is set.')
      # yapf: disable
      if self.args.swconfig_ports is None:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        raise ValueError('Should assign swconfig_ports if use_swconfig is'
                         'set.')
    # yapf: disable
    elif self.args.link_only and not self.args.iface:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      raise ValueError('Should assign iface if link_only is set.')

  def GetEthernetInterfaces(self):
    interfaces = []
    # yapf: disable
    for pattern in self.args.interface_name_patterns:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      interfaces += [
          self.dut.path.basename(path)
          for path in self.dut.Glob('/sys/class/net/' + pattern)
      ]
    return interfaces

  def GetInterface(self):
    devices = self.GetEthernetInterfaces()
    # yapf: disable
    if self.args.iface:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      if self.args.iface in devices:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        if self.CheckNotUsbLanDongle(self.args.iface):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          # yapf: disable
          return self.args.iface  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
        session.console.info('Not a built-in ethernet device.')
        return None
      return None
    return self.GetCandidateInterface()

  def GetCandidateInterface(self):
    devices = self.GetEthernetInterfaces()
    if not devices:
      self.FailTask('No ethernet interface')
    for dev in devices:
      if self.CheckNotUsbLanDongle(dev):
        self.dut.CheckCall(['ifconfig', dev, 'up'], log=True)
        return dev
    return None

  def GetFile(self):
    self.dut.CheckCall(['rm', '-f', _LOCAL_FILE_PATH])
    # yapf: disable
    logging.info('Try connecting to %s', self.args.test_url)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    try:
      self.dut.CheckCall(['wget', '-O', _LOCAL_FILE_PATH, '-T', '2',
                          # yapf: disable
                          self.args.test_url], log=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    except Exception as e:
      session.console.info('Failed to get file: %s', e)
    else:
      md5sum_output = self.dut.CheckOutput(
          ['md5sum', _LOCAL_FILE_PATH], log=True).strip().split()[0]
      logging.info('Got local file md5sum %s', md5sum_output)
      # yapf: disable
      logging.info('Golden file md5sum %s', self.args.md5sum)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      if md5sum_output == self.args.md5sum:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        session.console.info('Successfully connected to %s', self.args.test_url)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        return True
      session.console.info('md5 checksum error')
    return False

  def CheckLinkSimple(self, dev):
    status = self.dut.ReadSpecialFile(f'/sys/class/net/{dev}/carrier').strip()
    speed = self.dut.ReadSpecialFile(f'/sys/class/net/{dev}/speed').strip()
    if not int(status):
      self.FailTask(f'Link is down on dev {dev}')

    if int(speed) != 1000:
      self.FailTask(f'Speed is {speed}Mb/s not 1000Mb/s on dev {dev}')

    self.PassTask()

  def CheckNotUsbLanDongle(self, device):
    if 'usb' not in self.dut.path.realpath(f'/sys/class/net/{device}'):
      session.console.info('Built-in ethernet device %s found.', device)
      return True
    return False

  def CheckLinkSWconfig(self):
    # yapf: disable
    if isinstance(self.args.swconfig_ports, int):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.args.swconfig_ports = [self.args.swconfig_ports]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # yapf: disable
    if not isinstance(self.args.swconfig_expected_speed, list):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      swconfig_expected_speed = (
          # yapf: disable
          [self.args.swconfig_expected_speed] * len(self.args.swconfig_ports))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    else:
      # yapf: disable
      swconfig_expected_speed = self.args.swconfig_expected_speed  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    self.assertEqual(
        # yapf: disable
        len(self.args.swconfig_ports),  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        len(swconfig_expected_speed),
        "Length of swconfig_ports and swconfig_expcted_speed doesn't match.")

    # yapf: disable
    for port, speed in zip(self.args.swconfig_ports, swconfig_expected_speed):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      status = self.dut.CheckOutput(
          # yapf: disable
          [
              'swconfig',
              'dev',
              self.args.swconfig_switch,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
              # yapf: enable
              'port',
              str(port),
              'get',
              'link'
          ])

      if 'up' not in status:
        self.FailTask(
            # yapf: disable
            f'Link is down on switch {self.args.swconfig_switch} port '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
            # yapf: enable
            f'{int(port)}')

      session.console.info('Link is up on switch %s port %d',
                           # yapf: disable
                           self.args.swconfig_switch, port)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      if speed:
        speed_str = f'{speed}baseT'
        if speed_str not in status:
          self.FailTask(
              f'The negotiated speed is not expected ({speed_str!r} not in '
              f'{status!r})')

    self.PassTask()

  def runTest(self):
    # yapf: disable
    if not self.args.auto_start:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.WaitKeysOnce(test_ui.SPACE_KEY)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # yapf: disable
    if self.args.use_swconfig:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.CheckLinkSWconfig()

    # yapf: disable
    interval_sec = self.args.retry_interval_msecs / 1000.0  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    @sync_utils.RetryDecorator(max_attempt_count=5, interval_sec=interval_sec,
                               exceptions_to_catch=[])
    def _CheckLink():
      eth = self.GetInterface()
      if eth:
        # yapf: disable
        if self.args.link_only:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          self.CheckLinkSimple(eth)
        # yapf: disable
        elif self.args.test_url:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          if self.GetFile():
            self.PassTask()
        else:
          ethernet_ip, unused_prefix_number = net_utils.GetEthernetIp(eth)
          if ethernet_ip:
            session.console.info('Get ethernet IP %s for %s', ethernet_ip, eth)
            self.PassTask()

    _CheckLink()

    # yapf: disable
    if self.args.link_only:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.FailTask(f'Cannot find interface {self.args.iface}')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    # yapf: disable
    elif self.args.test_url:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.FailTask(f'Failed to download url {self.args.test_url}')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    else:
      self.FailTask('Cannot get ethernet IP')
