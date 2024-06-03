#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
from typing import Optional
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


def _GetUSBMatcher(factory_branch: Optional[str],
                   qualified: bool = True) -> matcher.Matcher:
  probe_info = v3_rule.AVLProbeInfo(
      'camera.usb_camera',
      collections.OrderedDict([('usb_vendor_id', ['0xa123']),
                               ('usb_product_id', ['0xb456']),
                               ('usb_bcd_device', ['0xc789'])]))
  m = default_builder.GetDefaultBuilder().Build(
      probe_info, 'fake_model', factory_branch=factory_branch, cid=1,
      qid=1 if qualified else 0, is_probe_info_override=False)
  assert m is not None
  return m


def _GetMIPIMatcher(factory_branch: Optional[str],
                    qualified: bool = True) -> matcher.Matcher:
  probe_info = v3_rule.AVLProbeInfo(
      'camera.mipi_camera',
      collections.OrderedDict([
          ('module_vid', ['AB']),
          ('module_pid', ['0x1a2b']),
          ('sensor_vid', ['CD']),
          ('sensor_pid', ['0x3c4d']),
      ]))
  m = default_builder.GetDefaultBuilder().Build(
      probe_info, 'fake_model', factory_branch=factory_branch, cid=1,
      qid=1 if qualified else 0, is_probe_info_override=False)
  assert m is not None
  return m


class CameraTest(unittest.TestCase):

  def testUSBCamera_Match(self):
    m = _GetUSBMatcher('factory-board-1.B')

    for test_name, fields, expected_result in (
        ('USBCameraWithUSBPrefix', {
            'usb_vendor_id': '0xa123',
            'usb_product_id': '0xb456',
            'usb_bcd_device': '0xc789',
        }, matcher.MatchResult(True, 'USBCameraWithUSBPrefix')),
        ('USBCameraWithUSBPrefix_Without0xPrefix', {
            'usb_vendor_id': 'A123',
            'usb_product_id': 'B456',
            'usb_bcd_device': 'C789',
        }, matcher.MatchResult(True, 'USBCameraWithUSBPrefix')),
        ('USBCameraNoUSBPrefix', {
            'idVendor': '0xa123',
            'idProduct': '0xb456',
            'bcdDevice': '0xc789',
        }, matcher.MatchResult(True, 'USBCameraNoUSBPrefix')),
        ('NotMatch', {
            'usb_vendor_id': '0xa123',
            'usb_product_id': '0xb456',
            'usb_bcd_device': '0xc78',
        }, matcher.MatchResult(False, 'USBCameraNoUSBPrefix')),
        ('NotMatch_NoBCD', {
            'usb_vendor_id': '0xa123',
            'usb_product_id': '0xb456',
        }, matcher.MatchResult(False, 'USBCameraNoUSBPrefix')),
    ):
      with self.subTest(test_name):
        self.assertEqual(m.Match(fields), expected_result)

  def testUSBCamera_GenerateProbeConfigMatcherStatement(self):
    m = _GetUSBMatcher('factory-board-1.B')

    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['usb_vendor_id', '0xa123'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['usb_product_id', '0xb456'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['usb_bcd_device', '0xc789'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['idVendor', '0xa123'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['idProduct', '0xb456'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['bcdDevice', '0xc789'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testUSBCamera_GetProbeInfoSuggestion(self):
    m = _GetUSBMatcher('factory-board-1.B')

    suggestion = m.GetProbeInfoSuggestion({
        'idVendor': '0xa111',
        'idProduct': '0xb222',
        'bcdDevice': '0xc333',
    })
    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            'usb_vendor_id', '0xa111',
            "Expected AVL attribute 'usb_vendor_id'='0xa123', but got "
            "'0xa111'."),
        matcher.ProbeInfoSuggestion(
            'usb_product_id', '0xb222',
            "Expected AVL attribute 'usb_product_id'='0xb456', but got "
            "'0xb222'."),
        matcher.ProbeInfoSuggestion(
            'usb_bcd_device', '0xc333',
            "Expected AVL attribute 'usb_bcd_device'='0xc789', but got "
            "'0xc333'."),
    ])

  def testUSBCameraUnqualified(self):
    m = _GetUSBMatcher('factory-board-1.B', False)

    self.assertEqual(
        m.Match({
            'usb_vendor_id': '0xa123',
            'usb_product_id': '0xb456',
        }), matcher.MatchResult(True, 'USBCameraWithUSBPrefixUnqualified'))
    self.assertEqual(
        m.Match({
            'idVendor': '0xa123',
            'idProduct': '0xb456',
        }), matcher.MatchResult(True, 'USBCameraNoUSBPrefixUnqualified'))

    with self.subTest('GenerateProbeConfigMatcherStatement'):
      self.assertEqual(
          m.GenerateProbeConfigMatcherStatement(),
          {
              'operand': [{
                  'operand': [{
                      'operand': ['usb_vendor_id', '0xa123'],
                      'operator': 'HEX_EQUAL'
                  }, {
                      'operand': ['usb_product_id', '0xb456'],
                      'operator': 'HEX_EQUAL'
                  }, {
                      'operand': ['usb_bcd_device', '0xc789'],
                      'operator': 'HEX_EQUAL'
                  }],
                  'operator': 'AND'
              }, {
                  'operand': [{
                      'operand': ['idVendor', '0xa123'],
                      'operator': 'HEX_EQUAL'
                  }, {
                      'operand': ['idProduct', '0xb456'],
                      'operator': 'HEX_EQUAL'
                  }, {
                      'operand': ['bcdDevice', '0xc789'],
                      'operator': 'HEX_EQUAL'
                  }],
                  'operator': 'AND'
              }, {
                  'operand': [{
                      'operand': ['usb_vendor_id', '0xa123'],
                      'operator': 'HEX_EQUAL'
                  }, {
                      'operand': ['usb_product_id', '0xb456'],
                      'operator': 'HEX_EQUAL'
                  }],
                  'operator': 'AND'
              }, {
                  'operand': [{
                      'operand': ['idVendor', '0xa123'],
                      'operator': 'HEX_EQUAL'
                  }, {
                      'operand': ['idProduct', '0xb456'],
                      'operator': 'HEX_EQUAL'
                  }],
                  'operator': 'AND'
              }],
              'operator': 'OR'
          },
      )

  def testUSBCameraUnqualifiedToT(self):
    m = _GetUSBMatcher(None, False)

    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(),
        {
            'operand': [{
                'operand': [{
                    'operand': ['usb_vendor_id', '0xa123'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['usb_product_id', '0xb456'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['usb_bcd_device', '0xc789'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['usb_vendor_id', '0xa123'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['usb_product_id', '0xb456'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        },
    )

  def testMipiCamera_Match(self):
    m = _GetMIPIMatcher('factory-board-1.B')

    self.assertEqual(
        m.Match({
            'mipi_module_id': 'AB1a2b',
            'mipi_sensor_id': 'CD3c4d',
        }), matcher.MatchResult(True, 'MIPICameraWithMIPIPrefix'))
    self.assertEqual(
        m.Match({
            'module_id': 'AB1a2b',
            'sensor_id': 'CD3c4d',
        }), matcher.MatchResult(True, 'MIPICameraNoMIPIPrefix'))
    self.assertEqual(
        m.Match({
            'module_id': 'not_match',
            'sensor_id': 'not_match',
        }), matcher.MatchResult(False, 'MIPICameraNoMIPIPrefix'))

  def testMipiCamera_GenerateProbeConfigMatcherStatement(self):
    m = _GetMIPIMatcher('factory-board-1.B')

    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['mipi_module_id', 'AB1a2b'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['mipi_sensor_id', 'CD3c4d'],
                    'operator': 'STRING_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['module_id', 'AB1a2b'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['sensor_id', 'CD3c4d'],
                    'operator': 'STRING_EQUAL'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR',
        })

  def testMipiCameraToT(self):
    m = _GetMIPIMatcher(None)

    self.assertEqual(
        m.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': ['mipi_module_id', 'AB1a2b'],
                'operator': 'STRING_EQUAL'
            }, {
                'operand': ['mipi_sensor_id', 'CD3c4d'],
                'operator': 'STRING_EQUAL'
            }],
            'operator': 'AND'
        })


if __name__ == '__main__':
  unittest.main()
