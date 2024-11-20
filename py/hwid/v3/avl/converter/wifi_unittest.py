#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
from typing import Optional, Sequence
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


def _GetMatcher(
    probe_function: str, factory_branch: Optional[str],
    wifi_probe_attributes: Optional[Sequence[str]] = None) -> matcher.Matcher:
  wifi_probe_attributes = (
      wifi_probe_attributes or ['0x0001, 0x0002, 0x0003', '0x0004, 0x0005'])
  probe_info = v3_rule.AVLProbeInfo(
      probe_function,
      collections.OrderedDict(
          [('wifi_probe_attributes', wifi_probe_attributes)]))
  m = default_builder.GetDefaultBuilder().Build(
      probe_info, 'fake_model', factory_branch=factory_branch, cid=1, qid=1,
      is_probe_info_override=False)
  assert m is not None
  return m


class WifiTest(unittest.TestCase):

  def testMatch(self):
    for test_name, fields, probe_function, factory_branch, expected_result in (
        ('WifiWithPciPrefix', {
            'pci_vendor_id': '0x0001',
            'pci_device_id': '0x0002',
            'pci_subsystem': '0x0003',
        }, 'wireless.pci_wireless_network', None,
         matcher.MatchResult(True, 'WifiWithPciPrefix')),
        ('WifiWithPciPrefix_NoSubsystem', {
            'pci_vendor_id': '0x0004',
            'pci_device_id': '0x0005',
        }, 'wireless.pci_wireless_network', None,
         matcher.MatchResult(True, 'WifiWithPciPrefix')),
        ('WifiNoPciPrefix', {
            'vendor': '0x0001',
            'device': '0x0002',
            'subsystem_device': '0x0003',
        }, 'wireless.pci_wireless_network', 'factory-board-1.B',
         matcher.MatchResult(True, 'WifiNoPciPrefix')),
        ('WifiNoPciPrefix_NoSubsystem', {
            'vendor': '0x0004',
            'device': '0x0005',
        }, 'wireless.pci_wireless_network', 'factory-board-1.B',
         matcher.MatchResult(True, 'WifiNoPciPrefix')),
        ('WifiWithPciPrefix_NotMatch', {
            'pci_vendor_id': '0x0001',
            'pci_device_id': '0x0002',
        }, 'wireless.pci_wireless_network', None,
         matcher.MatchResult(False, 'WifiWithPciPrefix')),
        ('WifiWithSdioPrefix', {
            'sdio_vendor_id': '0x0004',
            'sdio_device_id': '0x0005',
        }, 'wireless.sdio_wireless_network', None,
         matcher.MatchResult(True, 'WifiWithSdioPrefix')),
        ('WifiNoSdioPrefix', {
            'vendor': '0x0004',
            'device': '0x0005',
        }, 'wireless.sdio_wireless_network', None,
         matcher.MatchResult(True, 'WifiNoSdioPrefix')),
        ('WifiWithSdioPrefix_NotMatch', {
            'sdio_vendor_id': '0x0003',
            'sdio_device_id': '0x0004',
        }, 'wireless.sdio_wireless_network', None,
         matcher.MatchResult(False, 'WifiNoSdioPrefix')),
    ):
      with self.subTest(test_name=test_name):
        m = _GetMatcher(probe_function, factory_branch)
        self.assertEqual(m.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement_Pci(self):
    m = _GetMatcher('wireless.pci_wireless_network', 'factory-board-1.B')
    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': [{
                        'operand': ['pci_vendor_id', '0x1'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['pci_device_id', '0x2'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['pci_subsystem', '0x3'],
                        'operator': 'HEX_EQUAL'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': [{
                        'operand': ['pci_vendor_id', '0x4'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['pci_device_id', '0x5'],
                        'operator': 'HEX_EQUAL'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'OR'
            }, {
                'operand': [{
                    'operand': [{
                        'operand': ['vendor', '0x1'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['device', '0x2'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['subsystem_device', '0x3'],
                        'operator': 'HEX_EQUAL'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': [{
                        'operand': ['vendor', '0x4'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['device', '0x5'],
                        'operator': 'HEX_EQUAL'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'OR'
            }],
            'operator': 'OR'
        })

  def testGenerateProbeConfigMatcherStatement_PciToT(self):
    m = _GetMatcher('wireless.pci_wireless_network', None)
    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['pci_vendor_id', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_device_id', '0x2'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_subsystem', '0x3'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['pci_vendor_id', '0x4'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_device_id', '0x5'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testGenerateProbeConfigMatcherStatement_Sdio(self):
    m = _GetMatcher('wireless.sdio_wireless_network', None, ['0x0004, 0x0005'])
    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': [{
                        'operand': ['sdio_vendor_id', '0x4'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['sdio_device_id', '0x5'],
                        'operator': 'HEX_EQUAL'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'OR'
            }, {
                'operand': [{
                    'operand': [{
                        'operand': ['vendor', '0x4'],
                        'operator': 'HEX_EQUAL'
                    }, {
                        'operand': ['device', '0x5'],
                        'operator': 'HEX_EQUAL'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'OR'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion_Pci(self):
    m = _GetMatcher('wireless.pci_wireless_network', None)
    self.assertIsNone(
        m.GetProbeInfoSuggestion({
            'pci_vendor_id': '0x0001',
            'pci_device_id': '0x0002',
            'pci_subsystem': '0x0003',
        }))
    suggestion = m.GetProbeInfoSuggestion({
        'pci_vendor_id': '0x0007',
        'pci_device_id': '0x0008',
        'pci_subsystem': '0x0009',
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='wifi_probe_attributes', value='0x7, 0x8, 0x9',
            suggestion="Expected AVL attribute 'wifi_probe_attributes' equals "
            "to one of ['0x1, 0x2, 0x3', '0x4, 0x5'], but got "
            "'0x7, 0x8, 0x9'(pci_vendor_id, pci_device_id, pci_subsystem).")
    ])

  def testGetProbeInfoSuggestion_Pci_SubsystemNotMatch(self):
    m = _GetMatcher('wireless.pci_wireless_network', None, ['0x0001, 0x0002'])
    suggestion = m.GetProbeInfoSuggestion({
        'pci_vendor_id': '0x0007',
        'pci_device_id': '0x0008',
        'pci_subsystem': '0x0009',
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='wifi_probe_attributes', value='0x7, 0x8',
            suggestion="Expected AVL attribute 'wifi_probe_attributes' equals "
            "to one of ['0x1, 0x2'], but got "
            "'0x7, 0x8'(pci_vendor_id, pci_device_id).")
    ])

  def testGetProbeInfoSuggestion_Sdio(self):
    m = _GetMatcher('wireless.sdio_wireless_network', None)
    self.assertIsNone(
        m.GetProbeInfoSuggestion({
            'sdio_vendor_id': '0x0004',
            'sdio_device_id': '0x0005',
        }))
    suggestion = m.GetProbeInfoSuggestion({
        'sdio_vendor_id': '0x0006',
        'sdio_device_id': '0x0007',
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='wifi_probe_attributes', value='0x6, 0x7',
            suggestion="Expected AVL attribute 'wifi_probe_attributes' equals "
            "to one of ['0x1, 0x2', '0x4, 0x5'], but got "
            "'0x6, 0x7'(sdio_vendor_id, sdio_device_id).")
    ])


if __name__ == '__main__':
  unittest.main()
