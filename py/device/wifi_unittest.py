#!/usr/bin/env python3
#
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unittest for WiFi component."""

import unittest
from unittest import mock

from cros.factory.device import device_types
from cros.factory.device import wifi


class WiFiTest(unittest.TestCase):
  """ Unittest for WiFi DUT APIs."""

  _IW_SCAN_OUTPUT = """
BSS 00:11:22:33:44:55 (on wlan0)
    TSF: 2984923701 usec (0d, 00:49:44)
    freq: 2412
    beacon interval: 100
    capability: ESS ShortPreamble ShortSlotTime (0x0421)
    signal: -45.00 dBm
    last seen: 429 ms ago
    SSID: AP1
    Supported rates: 1.0* 2.0* 5.5* 6.0 9.0 11.0* 12.0 18.0
    DS Parameter set: channel 1
    ERP: <no flags>
    Extended supported rates: 24.0 36.0 48.0 54.0
    WMM:     * Parameter version 1
         * u-APSD
         * BE: CW 15-1023, AIFSN 3
         * BK: CW 15-1023, AIFSN 7
         * VI: CW 7-15, AIFSN 2, TXOP 3008 usec
         * VO: CW 3-7, AIFSN 2, TXOP 1504 usec
BSS 12:34:56:78:9a:bc (on wlan0)
    TSF: 2968648942 usec (0d, 00:49:28)
    freq: 2462.0
    beacon interval: 102
    capability: ESS ShortPreamble ShortSlotTime (0x0421)
    signal: -70.00 dBm
    LAST seen: 328 ms ago
    SSID: AP2
    Supported rates: 1.0* 2.0* 5.5* 6.0 9.0 11.0* 12.0 18.0
    DS Parameter set: channel 11
    ERP: <no flags>
    Extended supported rates: 24.0 36.0 48.0 54.0
    WMM:     * Parameter version 1
         * u-APSD
         * BE: CW 15-1023, AIFSN 3
         * BK: CW 15-1023, AIFSN 7
         * VI: CW 7-15, AIFSN 2, TXOP 3008 usec
         * VO: acm CW 3-7, AIFSN 2, TXOP 1504 usec"""

  def setUp(self):
    self.board = mock.Mock(device_types.DeviceBoard)
    self.wifi = wifi.WiFi(self.board)

  def testParseAccessPoint(self):
    self.board.CheckOutput.return_value = self._IW_SCAN_OUTPUT

    aps = self.wifi.AllAccessPoints('wlan0', None)
    self.assertEqual(len(aps), 2)
    self.board.CheckOutput.assert_called_once_with(
        ['iw', 'dev', 'wlan0', 'scan'], log=True)
    self.assertEqual(aps[0].frequency, 2412)
    self.assertEqual(aps[0].frequency_khz, None)
    self.assertEqual(aps[1].frequency, 2462)
    self.assertEqual(aps[1].frequency_khz, 0)


if __name__ == '__main__':
  unittest.main()
