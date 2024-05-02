#!/usr/bin/env python3
#
# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Networking-related utilities."""

import socket
import textwrap
import threading
import time
import unittest
from unittest import mock
import xmlrpc.server

from cros.factory.utils import net_utils
from cros.factory.utils import process_utils


class TimeoutXMLRPCTest(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.client = None

  def setUp(self):
    self.port = net_utils.FindUnusedTCPPort()
    self.server = xmlrpc.server.SimpleXMLRPCServer(
        (net_utils.LOCALHOST, self.port),
        allow_none=True)
    self.server.register_function(time.sleep)  # type: ignore #TODO(b/338318729) Fixit!
    self.thread = threading.Thread(target=self.server.serve_forever)
    self.thread.daemon = True
    self.thread.start()

  def tearDown(self):
    self.server.server_close()

  def MakeProxy(self, timeout):
    return net_utils.TimeoutXMLRPCServerProxy(
        f'http://{net_utils.LOCALHOST}:{int(self.port)}', timeout=timeout,
        allow_none=True)

  def runTest(self):
    self.client = self.MakeProxy(timeout=1)

    start = time.time()
    self.client.sleep(.001)  # No timeout
    delta = time.time() - start
    self.assertTrue(delta < 1, delta)

    start = time.time()
    try:
      self.client.sleep(2)  # Cause a timeout in 1 s
      self.fail('Expected exception')
    except socket.timeout:
      # Good!
      delta = time.time() - start
      self.assertTrue(delta > .25, delta)
      self.assertTrue(delta < 2, delta)


class IPTest(unittest.TestCase):
  def testInit(self):
    self.assertRaises(RuntimeError, net_utils.IP, 'invalid IP')
    assert net_utils.IP(0xc0a80000) == net_utils.IP('192.168.0.0')
    assert (net_utils.IP('2401:fa00:1:b:42a8:f0ff:fe3d:3ac1') ==
            net_utils.IP(0x2401fa000001000b42a8f0fffe3d3ac1, 6))

  def testIn(self):
    ip = net_utils.IP('192.168.1.50')
    cidr = net_utils.CIDR('192.168.0.0', 24)
    self.assertFalse(ip.IsIn(cidr))
    cidr = net_utils.CIDR('192.168.0.0', 16)
    self.assertTrue(ip.IsIn(cidr))


class CIDRTest(unittest.TestCase):
  def testSelectIP(self):
    cidr = net_utils.CIDR('192.168.0.0', 24)
    assert cidr.SelectIP(1) == net_utils.IP('192.168.0.1')
    assert cidr.SelectIP(2) == net_utils.IP('192.168.0.2')
    assert cidr.SelectIP(-3) == net_utils.IP('192.168.0.253')

  def testNetmask(self):
    cidr = net_utils.CIDR('192.168.0.0', 24)
    assert cidr.Netmask() == net_utils.IP('255.255.255.0')

    cidr = net_utils.CIDR('10.0.1.0', 22)
    assert cidr.Netmask() == net_utils.IP('255.255.252.0')


class UtilityFunctionTest(unittest.TestCase):
  def testGetUnusedIPRange(self):
    # Test 10.0.0.1/24 multiple
    network_cidr = net_utils.GetUnusedIPV4RangeCIDR(24, [
        ('10.0.0.1', 24),
        ('10.0.1.1', 24)])
    self.assertEqual(network_cidr, net_utils.CIDR('10.0.2.0', 24))

    # Test 10.0.0.1/16 used out and another 10.0.1.1/24 subnet in use.
    network_cidr = net_utils.GetUnusedIPV4RangeCIDR(24, [
        ('10.0.1.1', 24),
        ('10.0.0.1', 16)])
    self.assertEqual(network_cidr, net_utils.CIDR('10.1.0.0', 24))

    # Test 10.0.0.1/24 multiple
    network_cidr = net_utils.GetUnusedIPV4RangeCIDR(16, [
        ('10.0.0.1', 24),
        ('10.0.1.1', 24)])
    self.assertEqual(network_cidr, net_utils.CIDR('10.1.0.0', 16))

    # Test 10.0.0.1/8 used out
    network_cidr = net_utils.GetUnusedIPV4RangeCIDR(24, [
        ('10.0.0.1', 8),
        ('172.16.0.1', 24)])
    self.assertEqual(network_cidr, net_utils.CIDR('172.16.1.0', 24))

    # Test 10.0.0.1/8, 172.16.0.0/12 used out
    network_cidr = net_utils.GetUnusedIPV4RangeCIDR(24, [
        ('10.0.0.1', 8),
        ('172.16.0.0', 12)])
    self.assertEqual(network_cidr, net_utils.CIDR('192.168.0.0', 24))

    # Test 192.168.0.0/16 172.168.0./12 used out, 192.168.0.0/22
    network_cidr = net_utils.GetUnusedIPV4RangeCIDR(22, [
        ('10.0.0.1', 22),
        ('10.0.4.1', 22)])
    self.assertEqual(network_cidr, net_utils.CIDR('10.0.8.0', 22))

    exclude_ip_list = [('10.0.0.1', 8), ('172.16.0.0', 12)]
    ip = int(net_utils.IP('192.168.0.0'))
    for prefix_bits in range(17, 31):
      exclude_ip_list.append((str(net_utils.IP(ip)), prefix_bits))
      ip += 2 ** (32 - prefix_bits)
    network_cidr = net_utils.GetUnusedIPV4RangeCIDR(16, exclude_ip_list)
    self.assertEqual(network_cidr, net_utils.CIDR('192.168.255.252', 30))

    exclude_ip_list = [('10.0.0.1', 8), ('172.16.0.0', 12)]
    ip = int(net_utils.IP('192.168.0.0'))
    for prefix_bits in range(17, 33):
      exclude_ip_list.append((str(net_utils.IP(ip)), prefix_bits))
      ip += 2 ** (32 - prefix_bits)
    with self.assertRaises(RuntimeError):
      network_cidr = net_utils.GetUnusedIPV4RangeCIDR(16, exclude_ip_list)

  def testGetNetworkInterfaceByPath(self):
    func_under_test = net_utils.GetNetworkInterfaceByPath
    interface_table = {
        '/sys/class/net/eth0': '/REAL_PATH/0/net/eth0',
        '/sys/class/net/eth1': '/REAL_PATH/1/net/eth1'}
    def MockRealPath(path):
      return interface_table.get(path, '')

    with mock.patch('glob.glob', return_value=list(interface_table)):
      with mock.patch('os.path.realpath', side_effect=MockRealPath):
        self.assertEqual('eth0', func_under_test('eth0'))
        self.assertEqual('eth0', func_under_test('/REAL_PATH/0/net'))
        self.assertEqual('eth1', func_under_test('/REAL_PATH/1/net'))
        self.assertEqual(None, func_under_test('/WRONG_PATH'))

        self.assertIn(func_under_test('/REAL_PATH', True), ['eth0', 'eth1'])
        with self.assertRaises(ValueError):
          func_under_test('/REAL_PATH', False)

  def testGetDefaultGatewayInterface(self):
    # Successful case.
    mock_value = """\
    Kernel IP routing table
    Destination     Gateway         Genmask        Flags Metric Ref    Use Iface
    0.0.0.0         192.168.0.1     0.0.0.0        UG    600    0        0 wlan0
    """
    with mock.patch.object(process_utils, 'CheckOutput',
                           return_value=mock_value):
      ret = net_utils.GetDefaultGatewayInterface()
      self.assertEqual('wlan0', ret)

    # Duplicate case. It should return the first interface.
    mock_value = """\
    Kernel IP routing table
    Destination     Gateway         Genmask        Flags Metric Ref    Use Iface
    0.0.0.0         192.168.0.1     0.0.0.0        UG    600    0        0 wlan0
    0.0.0.0         192.168.1.1     0.0.0.0        UG    600    0        0 eth0
    """
    with mock.patch.object(process_utils, 'CheckOutput',
                           return_value=mock_value):
      ret = net_utils.GetDefaultGatewayInterface()
      self.assertEqual('wlan0', ret)

    # Empty case.
    mock_value = """\
    Kernel IP routing table
    Destination     Gateway         Genmask        Flags Metric Ref    Use Iface
    """
    with mock.patch.object(process_utils, 'CheckOutput',
                           return_value=mock_value):
      ret = net_utils.GetDefaultGatewayInterface()
      self.assertEqual(None, ret)

    # Failure case.
    mock_value = """Wrong content."""
    with mock.patch.object(process_utils, 'CheckOutput',
                           return_value=mock_value):
      with self.assertRaises(ValueError):
        ret = net_utils.GetDefaultGatewayInterface()


class LeasedIPTest(unittest.TestCase):

  ipv6_only_ap_output = """\
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 54:6c:eb:32:43:71 brd ff:ff:ff:ff:ff:ff
    inet6 2a00:ffff:ffff:ffff:ffff:ffff:183d:3a76/64 scope global temporary dynamic
       valid_lft 604787sec preferred_lft 86146sec
    inet6 2a00:ffff:ffff:ffff:ffff:ffff:fe32:4371/64 scope global dynamic mngtmpaddr
       valid_lft 2591987sec preferred_lft 604787sec
    inet6 fe80::ffff:ffff:ffff:4371/64 scope link
       valid_lft forever preferred_lft forever
"""

  def testBothIP_PreferIPv4(self):
    device = mock.Mock()
    device.CheckOutput = mock.Mock(return_value="""\
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 54:6c:eb:32:43:71 brd ff:ff:ff:ff:ff:ff
    inet 100.123.123.123/24 brd 100.123.123.255 scope global wlan0
       valid_lft forever preferred_lft forever
    inet6 2a00:ffff:ffff:ffff:ffff:ffff:183d:3a76/64 scope global temporary dynamic
       valid_lft 604787sec preferred_lft 86146sec
    inet6 2a00:ffff:ffff:ffff:ffff:ffff:fe32:4371/64 scope global dynamic mngtmpaddr
       valid_lft 2591987sec preferred_lft 604787sec
    inet6 fe80::ffff:ffff:ffff:4371/64 scope link
       valid_lft forever preferred_lft forever
""")

    result = net_utils.GetLeasedIP('wlan0', device)

    self.assertEqual(result, '100.123.123.123')

  def testIPv6OnlyAP_GetIPv6Address(self):
    device = mock.Mock()
    device.CheckOutput = mock.Mock(return_value=self.ipv6_only_ap_output)

    result = net_utils.GetLeasedIP('wlan0', device)

    self.assertIn(result, ('2a00:ffff:ffff:ffff:ffff:ffff:183d:3a76',
                           '2a00:ffff:ffff:ffff:ffff:ffff:fe32:4371'))

  def testIPv6OnlyAP_QueryIPv4Only_GetNone(self):
    device = mock.Mock()
    device.CheckOutput = mock.Mock(return_value=self.ipv6_only_ap_output)

    result = net_utils.GetLeasedIP(
        'wlan0', device, ip_address_family=net_utils.IpAddressFamily.ipv4)

    self.assertIsNone(result)

  def testIPv6OnlyAP_QueryIPv6Only_GetIPv6Address(self):
    device = mock.Mock()
    device.CheckOutput = mock.Mock(return_value=self.ipv6_only_ap_output)

    result = net_utils.GetLeasedIP(
        'wlan0', device, ip_address_family=net_utils.IpAddressFamily.ipv6)

    self.assertIn(result, ('2a00:ffff:ffff:ffff:ffff:ffff:183d:3a76',
                           '2a00:ffff:ffff:ffff:ffff:ffff:fe32:4371'))

  def testNoLease_GetNone(self):
    device = mock.Mock()
    device.CheckOutput = mock.Mock(return_value="""\
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 54:6c:eb:32:43:71 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::ffff:ffff:ffff:4371/64 scope link
       valid_lft forever preferred_lft forever
""")

    result = net_utils.GetLeasedIP('wlan0', device)

    self.assertIsNone(result)


class ConvertIPtoFamilyTest(unittest.TestCase):

  def testIPv4(self):
    result = net_utils.ConvertIPtoFamily('100.123.123.123')

    self.assertEqual(result, net_utils.IpAddressFamily.ipv4)

  def testIPv6(self):
    result = net_utils.ConvertIPtoFamily('fe80::ffff:ffff:ffff:4371')

    self.assertEqual(result, net_utils.IpAddressFamily.ipv6)

  def testNotIP_ThrowException(self):
    with self.assertRaises(ValueError):
      net_utils.ConvertIPtoFamily('Im.not.an.ip')


class ParseWirelessInterfaceStationDumpOutputTest(unittest.TestCase):

  def testSignalStrengthsForOneAntenna(self):

    output = """\
    Station 12:34:56:89:90:ab (on wlan0)
    \tsignal:\t-54 [-55] dBm
    \tsignal avg:\t-59 [-60] dBm
    \tbeacon signal avg:\t-64 dBm
    """
    result = net_utils.ParseWirelessInterfaceStationDumpOutput(
        textwrap.dedent(output))

    self.assertEqual(result.signal,
                     net_utils.WiFiConnectionStatus.Signal(-54, [-55]))  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(result.avg_signal,
                     net_utils.WiFiConnectionStatus.Signal(-59, [-60]))  # type: ignore #TODO(b/338318729) Fixit!

  def testSignalStrengthsForFourAntennas(self):

    output = """\
    Station 12:34:56:89:90:ab (on wlan0)
    \tsignal:\t-54 [-55, -56, -57, -58] dBm
    \tsignal avg:\t-59 [-60, -61, -62, -63] dBm
    \tbeacon signal avg:\t-64 dBm
    """
    result = net_utils.ParseWirelessInterfaceStationDumpOutput(
        textwrap.dedent(output))

    self.assertEqual(
        result.signal,
        net_utils.WiFiConnectionStatus.Signal(-54, [-55, -56, -57, -58]))  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(
        result.avg_signal,
        net_utils.WiFiConnectionStatus.Signal(-59, [-60, -61, -62, -63]))  # type: ignore #TODO(b/338318729) Fixit!

  def testSignalStrengthsWithoutValueForEachAntenna(self):

    output = """\
    Station 12:34:56:89:90:ab (on wlan0)
    \tsignal:\t-54 dBm
    \tsignal avg:\t-59 dBm
    \tbeacon signal avg:\t-64 dBm
    """
    result = net_utils.ParseWirelessInterfaceStationDumpOutput(
        textwrap.dedent(output))

    self.assertEqual(result.signal,
                     net_utils.WiFiConnectionStatus.Signal(-54, []))  # type: ignore #TODO(b/338318729) Fixit!
    self.assertEqual(result.avg_signal,
                     net_utils.WiFiConnectionStatus.Signal(-59, []))  # type: ignore #TODO(b/338318729) Fixit!

  def testBitRates(self):
    output = """\
    Station 12:34:56:89:90:ab (on wlan0)
    \ttx bitrate:\t400.0 MBit/s VHT-MCS 9 40MHz short GI VHT-NSS 2
    \trx bitrate:\t12.0 MBit/s
    """

    result = net_utils.ParseWirelessInterfaceStationDumpOutput(
        textwrap.dedent(output))

    self.assertEqual(result.tx_bitrate, 400.0)
    self.assertEqual(result.rx_bitrate, 12.0)

  def testEmptyStationDumpOutput(self):
    result = net_utils.ParseWirelessInterfaceStationDumpOutput('')
    self.assertEqual(result.signal, None)
    self.assertEqual(result.avg_signal, None)
    self.assertEqual(result.tx_bitrate, None)
    self.assertEqual(result.rx_bitrate, None)

  def testUnexpectedSignalOutput(self):
    output_cases = [
        # Non-integer value.
        """\
        Station 12:34:56:89:90:ab (on wlan0)
        \tsignal:\tfoo
        """,
        # Missing computed value.
        """\
        Station 12:34:56:89:90:ab (on wlan0)
        \tsignal:\t[ -54, -55 ] dBm
        """,
    ]
    for output in output_cases:
      with self.assertRaises(ValueError):
        net_utils.ParseWirelessInterfaceStationDumpOutput(
            textwrap.dedent(output))

  def textUnexpectedBitRateOutput(self):
    output_cases = [
        # Non-float value.
        """\
        Station 12:34:56:89:90:ab (on wlan0)
        \ttx bitrate:\tfoo
        """,
        # Unexpected unit.
        """\
        Station 12:34:56:89:90:ab (on wlan0)
        \ttx bitrate:\t200.0 foo/bar
        """,
        # Missing unit.
        """\
        Station 12:34:56:89:90:ab (on wlan0)
        \ttx bitrate:\t200.0
        """
    ]
    for output in output_cases:
      with self.assertRaises(ValueError):
        net_utils.ParseWirelessInterfaceStationDumpOutput(
            textwrap.dedent(output))


if __name__ == '__main__':
  unittest.main()
