#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import textwrap
import unittest
from unittest import mock

from cros.factory.utils import file_utils

from cros.factory.external.chromeos_cli import futility
from cros.factory.external.chromeos_cli import shell


class FutilityTest(unittest.TestCase):

  def setUp(self):
    self.futility = futility.Futility()
    self.shell = mock.Mock(spec=shell.Shell)
    self.futility._shell = self.shell  # pylint: disable=protected-access

  def testGetFlashSize(self):
    self._SetFutilityUtilityResult(
        stdout=textwrap.dedent("""
        ignored messages
        16777216
        """))
    flash_size = self.futility.GetFlashSize()
    self._CheckCalledCommand(['flashrom', '--flash-size'])
    self.assertEqual(flash_size, 16777216)

  def testGetFlashSizeError(self):
    self._SetFutilityUtilityResult(stdout='unknown messages')
    self.assertRaises(futility.FlashromError, self.futility.GetFlashSize)

  def testGetWriteProtectInfo(self):
    self._SetFutilityUtilityResult(
        stdout=textwrap.dedent("""
        ignored messages
        Expected WP SR configuration by FW image:(start = 0x00800000, length = 0x00700000)
        """))
    wp_conf = self.futility.GetWriteProtectInfo()
    self._CheckCalledCommand(['futility', 'flash', '--flash-info'])
    self.assertEqual(wp_conf['start'], '0x00800000')
    self.assertEqual(wp_conf['length'], '0x00700000')

  def testGetWriteProtectInfoError(self):
    self._SetFutilityUtilityResult(stdout='unknown messages')
    self.assertRaises(futility.FutilityError, self.futility.GetWriteProtectInfo)

  def testGetRegions(self):
    test_regions = ['RO_GSCVD', 'WP_RO']
    output_dir = 'unittest'
    prefix = 'bios'
    region_to_fw = self.futility.GetRegions(test_regions, output_dir, prefix)
    for region in test_regions:
      self.shell.assert_any_call(
          f'futility read --region {region} {region_to_fw[region]}')
      self.assertEqual(region_to_fw[region], f'{output_dir}/{prefix}_{region}')

  @mock.patch.object(futility.Futility, 'GetRegions', autospec=True)
  def testGetRLZFromROGSCVDSuccess(self, mock_regions):
    RO_GSCVD = b'5afe........RCZZ'
    mock_gscvd_file = file_utils.CreateTemporaryFile()
    file_utils.WriteFile(mock_gscvd_file, RO_GSCVD, encoding=None)
    mock_regions.return_value = {
        'RO_GSCVD': mock_gscvd_file
    }

  @mock.patch.object(futility.Futility, 'GetRegions', autospec=True)
  def testGetRLZFromROGSCVDFail(self, mock_regions):
    RO_GSCVD_NO_MAGIC_NUMBER = b'abcd........RCZZ'
    RO_GSCVD_INVALID_RLZ = b'5afe........ .@#'
    mock_gscvd_file = file_utils.CreateTemporaryFile()
    file_utils.WriteFile(mock_gscvd_file, RO_GSCVD_NO_MAGIC_NUMBER,
                         encoding=None)
    mock_regions.return_value = {
        'RO_GSCVD': mock_gscvd_file
    }
    self.assertRaisesRegex(
        ValueError, 'Failed to find magic number in GSCVD! '
        'Expected: b\'5afe\', Found: b\'abcd\'',
        self.futility.GetRLZFromROGSCVD)

    file_utils.WriteFile(mock_gscvd_file, RO_GSCVD_INVALID_RLZ, encoding=None)
    self.assertRaisesRegex(
        ValueError, 'Each char in the RLZ code should be a char between '
        'A~Z. Found: b\' .@#\'', self.futility.GetRLZFromROGSCVD)


  def _SetFutilityUtilityResult(self, stdout='', status=0):
    self.shell.return_value = shell.ShellResult(
        success=status == 0, status=status, stdout=stdout, stderr='')

  def _CheckCalledCommand(self, cmd):
    self.assertEqual(self.shell.call_args[0][0], cmd)


if __name__ == '__main__':
  unittest.main()
