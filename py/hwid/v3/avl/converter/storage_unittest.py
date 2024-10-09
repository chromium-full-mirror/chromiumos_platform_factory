#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import unittest

from cros.factory.hwid.v3.avl import default_builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule


class NvmeStorageTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'storage.nvme_storage',
        collections.OrderedDict([
            ('size_in_gb', ['4']),
            ('nvme_model', ['ABCDE']),
            ('pci_class', ['0x123456']),
            ('pci_device', ['0x0002']),
            ('pci_vendor', ['0x0001']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('NvmeStorage', {
            'pci_vendor': '0x0001',
            'pci_device': '0x0002',
            'pci_class': '0x123456',
            'nvme_model': 'ABCDE',
            'size': '4000000000',
        }, matcher.MatchResult(True, 'NvmeStorage')),
        ('NvmeStorageNoSize', {
            'pci_vendor': '0x0001',
            'pci_device': '0x0002',
            'pci_class': '0x123456',
            'nvme_model': 'ABCDE',
            'sectors': '7812500',
        }, matcher.MatchResult(True, 'NvmeStorageNoSize')),
        ('NvmeStorageNoPciPrefix', {
            'vendor': '0x0001',
            'device': '0x0002',
            'class': '0x123456',
            'nvme_model': 'ABCDE',
            'sectors': '7812500',
        }, matcher.MatchResult(True, 'NvmeStorageNoPciPrefix')),
        ('NvmeStorage_SizeNotMatch', {
            'pci_vendor': '0x0001',
            'pci_device': '0x0002',
            'pci_class': '0x123456',
            'nvme_model': 'ABCDE',
            'size': '8000000000',
        }, matcher.MatchResult(False, 'NvmeStorageNoPciPrefix')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['nvme_model', 'ABCDE'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['pci_class', '0x123456'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_device', '0x2'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_vendor', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['size', '4003999999'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['size', '3800000000'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['nvme_model', 'ABCDE'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['pci_class', '0x123456'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_device', '0x2'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_vendor', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['nvme_model', 'ABCDE'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['class', '0x123456'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['device', '0x2'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['vendor', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'pci_vendor': '0x0001',
            'pci_device': '0x0002',
            'pci_class': '0x123456',
            'nvme_model': 'ABCDE',
            'size': '4000000000',
        }))

    for (size_unit, size_value) in (
        ('size', '8000000000'),
        ('sectors', '15625000'),
    ):
      with self.subTest(size_unit):
        suggestion = self.matcher.GetProbeInfoSuggestion({
            'pci_vendor': '0x0003',
            'pci_device': '0x0004',
            'pci_class': '0x123789',
            'nvme_model': 'AAAAA',
            size_unit: size_value,
        })

        assert suggestion is not None
        self.assertCountEqual(suggestion, [
            matcher.ProbeInfoSuggestion(
                key='nvme_model', value='AAAAA',
                suggestion="Expected AVL attribute 'nvme_model'='ABCDE', but "
                "got 'AAAAA'."),
            matcher.ProbeInfoSuggestion(
                key='pci_class', value='0x123789',
                suggestion="Expected AVL attribute 'pci_class'='0x123456', but "
                "got '0x123789'."),
            matcher.ProbeInfoSuggestion(
                key='pci_device', value='0x4',
                suggestion="Expected AVL attribute 'pci_device'='0x2', but got "
                "'0x4'."),
            matcher.ProbeInfoSuggestion(
                key='pci_vendor', value='0x3',
                suggestion="Expected AVL attribute 'pci_vendor'='0x1', but got "
                "'0x3'."),
            matcher.ProbeInfoSuggestion(
                key='size_in_gb', value='8',
                suggestion="Expected AVL attribute 'size_in_gb'=4GB, but got "
                f"8GB({size_value} in {size_unit}).")
        ])


class EmmcStorageTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'storage.mmc_storage',
        collections.OrderedDict([
            ('size_in_gb', ['4']),
            ('mmc_name', ['0x414141424242']),
            ('mmc_manfid', ['0x0001']),
            ('mmc_prv', ['0x0002']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('EmmcStorage', {
            'mmc_manfid': '0x0001',
            'mmc_prv': '0x0002',
            'mmc_name': 'AAABBB',
            'size': '4000000000',
        }, matcher.MatchResult(True, 'EmmcStorage')),
        ('EmmcStorageNoSize', {
            'mmc_manfid': '0x0001',
            'mmc_prv': '0x0002',
            'mmc_name': 'AAABBB',
            'sectors': '7812500',
        }, matcher.MatchResult(True, 'EmmcStorageNoSize')),
        ('EmmcStorageNoMmcPrefix', {
            'manfid': '0x0001',
            'prv': '0x0002',
            'name': 'AAABBB',
            'sectors': '7812500',
        }, matcher.MatchResult(True, 'EmmcStorageNoMmcPrefix')),
        ('EmmcStorage_NoPRV', {
            'mmc_manfid': '0x0001',
            'mmc_name': 'AAABBB',
            'size': '4000000000',
        }, matcher.MatchResult(False, 'EmmcStorageNoMmcPrefix')),
        ('EmmcStorage_SizeNotMatch', {
            'mmc_manfid': '0x0001',
            'mmc_prv': '0x0002',
            'mmc_name': 'AAABBB',
            'size': '8000000000',
        }, matcher.MatchResult(False, 'EmmcStorageNoMmcPrefix')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['mmc_manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['size', '4003999999'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['size', '3800000000'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': ['mmc_prv', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['mmc_manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': ['mmc_prv', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': ['prv', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'mmc_manfid': '0x0001',
            'mmc_prv': '0x0002',
            'mmc_name': 'AAABBB',
            'size': '4000000000',
        }))

    for (size_unit, size_value) in (
        ('size', '8000000000'),
        ('sectors', '15625000'),
    ):
      with self.subTest(size_unit):
        suggestion = self.matcher.GetProbeInfoSuggestion({
            'mmc_manfid': '0x0003',
            'mmc_prv': '0x0004',
            'mmc_name': 'AAACCC',
            size_unit: size_value,
        })

        assert suggestion is not None
        self.assertCountEqual(suggestion, [
            matcher.ProbeInfoSuggestion(
                key='mmc_manfid', value='0x3',
                suggestion="Expected AVL attribute 'mmc_manfid'='0x1', but got "
                "'0x3'."),
            matcher.ProbeInfoSuggestion(
                key='mmc_prv', value='0x4',
                suggestion="Expected AVL attribute 'mmc_prv'='0x2', but got "
                "'0x4'."),
            matcher.ProbeInfoSuggestion(
                key='mmc_name', value='AAACCC',
                suggestion="Expected AVL attribute 'mmc_name'='AAABBB', "
                "but got 'AAACCC'."),
            matcher.ProbeInfoSuggestion(
                key='size_in_gb', value='8',
                suggestion="Expected AVL attribute 'size_in_gb'=4GB, but got "
                f"8GB({size_value} in {size_unit}).")
        ])


class EmmcStorageUnqualifiedTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'storage.mmc_storage',
        collections.OrderedDict([
            ('size_in_gb', ['4']),
            ('mmc_name', ['0x414141424242']),
            ('mmc_manfid', ['0x0001']),
            ('mmc_prv', ['0x0002']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=0,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('EmmcStorage', {
            'mmc_manfid': '0x0001',
            'mmc_name': 'AAABBB',
            'size': '4000000000',
        }, matcher.MatchResult(True, 'EmmcStorageUnqualified')),
        ('EmmcStorageNoSize', {
            'mmc_manfid': '0x0001',
            'mmc_name': 'AAABBB',
            'sectors': '7812500',
        }, matcher.MatchResult(True, 'EmmcStorageNoSizeUnqualified')),
        ('EmmcStorageNoMmcPrefix', {
            'manfid': '0x0001',
            'name': 'AAABBB',
            'sectors': '7812500',
        }, matcher.MatchResult(True, 'EmmcStorageNoMmcPrefixUnqualified')),
        ('EmmcStorage_SizeNotMatch', {
            'mmc_manfid': '0x0001',
            'mmc_name': 'AAABBB',
            'size': '8000000000',
        }, matcher.MatchResult(False, 'EmmcStorageNoMmcPrefixUnqualified')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['mmc_manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['size', '4003999999'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['size', '3800000000'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': ['mmc_prv', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['mmc_manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': ['mmc_prv', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }, {
                    'operand': ['prv', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['mmc_manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['size', '4003999999'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['size', '3800000000'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['mmc_manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['manfid', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'mmc_manfid': '0x0001',
            'mmc_name': 'AAABBB',
            'size': '4000000000',
        }))

    for (size_unit, size_value) in (
        ('size', '8000000000'),
        ('sectors', '15625000'),
    ):
      with self.subTest(size_unit):
        suggestion = self.matcher.GetProbeInfoSuggestion({
            'mmc_manfid': '0x0003',
            'mmc_name': 'AAACCC',
            size_unit: size_value,
        })

        assert suggestion is not None
        self.assertCountEqual(suggestion, [
            matcher.ProbeInfoSuggestion(
                key='mmc_manfid', value='0x3',
                suggestion="Expected AVL attribute 'mmc_manfid'='0x1', but got "
                "'0x3'."),
            matcher.ProbeInfoSuggestion(
                key='mmc_name', value='AAACCC',
                suggestion="Expected AVL attribute 'mmc_name'='AAABBB', "
                "but got 'AAACCC'."),
            matcher.ProbeInfoSuggestion(
                key='size_in_gb', value='8',
                suggestion="Expected AVL attribute 'size_in_gb'=4GB, but got "
                f"8GB({size_value} in {size_unit}).")
        ])


class UfsStorageTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'storage.ufs_storage',
        collections.OrderedDict([
            ('size_in_gb', ['4']),
            ('ufs_model', ['AAA']),
            ('ufs_vendor', ['BBB']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('UfsStorage', {
            'ufs_model': 'AAA',
            'ufs_vendor': 'BBB',
            'size': '4000000000',
        }, matcher.MatchResult(True, 'UfsStorage')),
        ('UfsStorageSizeIsWrong', {
            'ufs_model': 'AAA',
            'ufs_vendor': 'BBB',
            'sectors': '7812500',
        }, matcher.MatchResult(True, 'UfsStorageSizeIsWrong')),
        ('UfsStorage_SizeNotMatch', {
            'ufs_model': 'AAA',
            'ufs_vendor': 'BBB',
            'size': '8000000000',
        }, matcher.MatchResult(False, 'UfsStorageSizeIsWrong')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['ufs_model', 'AAA'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['ufs_vendor', 'BBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['size', '4003999999'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['size', '3800000000'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['ufs_model', 'AAA'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['ufs_vendor', 'BBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': [{
                        'operand': ['sectors', '7820312'],
                        'operator': 'INTEGER_LESS'
                    }, {
                        'operand': ['sectors', '7421875'],
                        'operator': 'INTEGER_GREATER'
                    }],
                    'operator': 'AND'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'ufs_model': 'AAA',
            'ufs_vendor': 'BBB',
            'size': '4000000000',
        }))

    for (size_unit, size_value) in (
        ('size', '8000000000'),
        ('sectors', '15625000'),
    ):
      with self.subTest(size_unit):
        suggestion = self.matcher.GetProbeInfoSuggestion({
            'ufs_model': 'CCC',
            'ufs_vendor': 'DDD',
            size_unit: size_value,
        })

        assert suggestion is not None
        self.assertCountEqual(suggestion, [
            matcher.ProbeInfoSuggestion(
                key='ufs_model', value='CCC',
                suggestion="Expected AVL attribute 'ufs_model'='AAA', but got "
                "'CCC'."),
            matcher.ProbeInfoSuggestion(
                key='ufs_vendor', value='DDD',
                suggestion="Expected AVL attribute 'ufs_vendor'='BBB', but got "
                "'DDD'."),
            matcher.ProbeInfoSuggestion(
                key='size_in_gb', value='8',
                suggestion="Expected AVL attribute 'size_in_gb'=4GB, but got "
                f"8GB({size_value} in {size_unit}).")
        ])


class PcieEmmcStorageBridgeAssemblyTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'emmc_pcie_assembly.generic',
        collections.OrderedDict([
            ('size_in_gb', ['4']),
            ('bridge_pcie_device', ['0x0001']),
            ('bridge_pcie_vendor', ['0x0002']),
            ('mmc_manfid', ['0x0003']),
            ('bridge_pcie_class', ['0x0004']),
            ('mmc_name', ['0x414141424242']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('PciEmmcStorageBridgeAssembly', {
            'bridge_pcie_device': '0x0001',
            'bridge_pcie_vendor': '0x0002',
            'mmc_manfid': '0x0003',
            'bridge_pcie_class': '0x0004',
            'mmc_name': 'AAABBB',
        }, matcher.MatchResult(True, 'PciEmmcStorageBridgeAssembly')),
        ('PciEmmcStorageBridgeAssemblyNoPrefix', {
            'device': '0x0001',
            'vendor': '0x0002',
            'manfid': '0x0003',
            'name': 'AAABBB',
        }, matcher.MatchResult(True, 'PciEmmcStorageBridgeAssemblyNoPrefix')),
        ('NotMatch', {
            'bridge_pcie_device': '0x0001',
            'bridge_pcie_vendor': '0x0002',
            'mmc_manfid': '0x0003',
            'bridge_pcie_class': '0x0004',
            'mmc_name': 'AAACCC',
        }, matcher.MatchResult(False, 'PciEmmcStorageBridgeAssemblyNoPrefix')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['bridge_pcie_device', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['bridge_pcie_vendor', '0x2'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_manfid', '0x3'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['mmc_name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }, {
                    'operand': ['bridge_pcie_class', '0x4'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['device', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['vendor', '0x2'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['manfid', '0x3'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['name', 'AAABBB'],
                    'operator': 'STRING_EQUAL'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'bridge_pcie_device': '0x0001',
            'bridge_pcie_vendor': '0x0002',
            'mmc_manfid': '0x0003',
            'bridge_pcie_class': '0x0004',
            'mmc_name': 'AAABBB',
        }))
    suggestion = self.matcher.GetProbeInfoSuggestion({
        'bridge_pcie_device': '0x0005',
        'bridge_pcie_vendor': '0x0006',
        'mmc_manfid': '0x0007',
        'bridge_pcie_class': '0x0008',
        'mmc_name': 'AAACCC',
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='bridge_pcie_device', value='0x5',
            suggestion="Expected AVL attribute 'bridge_pcie_device'='0x1', "
            "but got '0x5'."),
        matcher.ProbeInfoSuggestion(
            key='bridge_pcie_vendor', value='0x6',
            suggestion="Expected AVL attribute 'bridge_pcie_vendor'='0x2', "
            "but got '0x6'."),
        matcher.ProbeInfoSuggestion(
            key='mmc_manfid', value='0x7',
            suggestion="Expected AVL attribute 'mmc_manfid'='0x3', but got "
            "'0x7'."),
        matcher.ProbeInfoSuggestion(
            key='mmc_name', value='AAACCC',
            suggestion="Expected AVL attribute 'mmc_name'='AAABBB', but got "
            "'AAACCC'."),
        matcher.ProbeInfoSuggestion(
            key='bridge_pcie_class', value='0x8',
            suggestion="Expected AVL attribute 'bridge_pcie_class'='0x4', "
            "but got '0x8'.")
    ])


class NvmeEmmcStorageBridgeAssemblyTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'emmc_pcie_assembly.generic',
        collections.OrderedDict([
            ('size_in_gb', ['4']),
            ('bridge_pcie_device', ['0x0001']),
            ('bridge_pcie_vendor', ['0x0002']),
            ('bridge_pcie_class', ['0x0004']),
            ('nvme_model', ['ABCDE']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch=None, cid=1, qid=1,
        is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('Match', {
            'pci_device': '0x0001',
            'pci_vendor': '0x0002',
            'pci_class': '0x0004',
            'nvme_model': 'ABCDE',
        }, matcher.MatchResult(True, 'NvmeEmmcStorageBridgeAssembly')),
        ('NotMatch', {
            'pci_device': '0x0001',
            'pci_vendor': '0x0002',
            'pci_class': '0x0004',
            'nvme_model': 'ABCDF',
        }, matcher.MatchResult(False, 'NvmeEmmcStorageBridgeAssembly')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': ['pci_class', '0x4'],
                'operator': 'HEX_EQUAL'
            }, {
                'operand': ['pci_device', '0x1'],
                'operator': 'HEX_EQUAL'
            }, {
                'operand': ['pci_vendor', '0x2'],
                'operator': 'HEX_EQUAL'
            }, {
                'operand': ['nvme_model', 'ABCDE'],
                'operator': 'STRING_EQUAL'
            }],
            'operator': 'AND'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'pci_device': '0x0001',
            'pci_vendor': '0x0002',
            'pci_class': '0x0004',
            'nvme_model': 'ABCDE',
        }))
    suggestion = self.matcher.GetProbeInfoSuggestion({
        'pci_device': '0x0005',
        'pci_vendor': '0x0006',
        'pci_class': '0x0007',
        'nvme_model': 'ABCDF',
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='bridge_pcie_class', value='0x7',
            suggestion="Expected AVL attribute 'bridge_pcie_class'='0x4', but "
            "got '0x7'."),
        matcher.ProbeInfoSuggestion(
            key='bridge_pcie_device', value='0x5',
            suggestion="Expected AVL attribute 'bridge_pcie_device'='0x1', but "
            "got '0x5'."),
        matcher.ProbeInfoSuggestion(
            key='bridge_pcie_vendor', value='0x6',
            suggestion="Expected AVL attribute 'bridge_pcie_vendor'='0x2', but "
            "got '0x6'."),
        matcher.ProbeInfoSuggestion(
            key='nvme_model', value='ABCDF',
            suggestion="Expected AVL attribute 'nvme_model'='ABCDE', but got "
            "'ABCDF'.")
    ])


class PciEmmcStorageBridgeHostOnlyTest(unittest.TestCase):

  def setUp(self):
    probe_info = v3_rule.AVLProbeInfo(
        'emmc_pcie_storage_bridge.mmc_host',
        collections.OrderedDict([
            ('pci_device_id', ['0x0001']),
            ('pci_vendor_id', ['0x0002']),
        ]))
    m = default_builder.GetDefaultBuilder().Build(
        probe_info, 'fake_model', factory_branch='factory-board-1.B', cid=1,
        qid=1, is_probe_info_override=False)
    assert m is not None
    self.matcher = m

  def testMatch(self):
    for test_name, fields, expected_result in (
        ('PciEmmcStorageBridgeHostOnly', {
            'pci_device_id': '0x0001',
            'pci_vendor_id': '0x0002',
        }, matcher.MatchResult(True, 'PciEmmcStorageBridgeHostOnly')),
        ('PciEmmcStorageBridgeHostOnlyNoPciPrefix', {
            'device': '0x0001',
            'vendor': '0x0002',
        }, matcher.MatchResult(True,
                               'PciEmmcStorageBridgeHostOnlyNoPciPrefix')),
        ('NotMatch', {
            'pci_device_id': '0x0003',
            'pci_vendor_id': '0x0004',
        }, matcher.MatchResult(False,
                               'PciEmmcStorageBridgeHostOnlyNoPciPrefix')),
    ):
      with self.subTest(test_name=test_name):
        self.assertEqual(self.matcher.Match(fields), expected_result)

  def testGenerateProbeConfigMatcherStatement(self):
    self.assertEqual(
        self.matcher.GenerateProbeConfigMatcherStatement(), {
            'operand': [{
                'operand': [{
                    'operand': ['pci_device_id', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['pci_vendor_id', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }, {
                'operand': [{
                    'operand': ['device', '0x1'],
                    'operator': 'HEX_EQUAL'
                }, {
                    'operand': ['vendor', '0x2'],
                    'operator': 'HEX_EQUAL'
                }],
                'operator': 'AND'
            }],
            'operator': 'OR'
        })

  def testGetProbeInfoSuggestion(self):
    self.assertIsNone(
        self.matcher.GetProbeInfoSuggestion({
            'pci_device_id': '0x0001',
            'pci_vendor_id': '0x0002',
        }))
    suggestion = self.matcher.GetProbeInfoSuggestion({
        'pci_device_id': '0x0003',
        'pci_vendor_id': '0x0004',
    })

    assert suggestion is not None
    self.assertCountEqual(suggestion, [
        matcher.ProbeInfoSuggestion(
            key='pci_device_id', value='0x3',
            suggestion="Expected AVL attribute 'pci_device_id'='0x1', but got "
            "'0x3'."),
        matcher.ProbeInfoSuggestion(
            key='pci_vendor_id', value='0x4',
            suggestion="Expected AVL attribute 'pci_vendor_id'='0x2', but got "
            "'0x4'.")
    ])


if __name__ == '__main__':
  unittest.main()
