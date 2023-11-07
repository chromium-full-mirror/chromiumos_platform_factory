#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import textwrap
import unittest
from unittest import mock

from cros.factory.utils import process_utils

from cros.factory.external.chromeos_cli import cryptohome_utils


class CryptohomeUtilsTest(unittest.TestCase):

  _TEST_DEVELOPER_KEY_HASH = '0' * 64

  def setUp(self) -> None:
    self._cryptohome_util = cryptohome_utils.CryptohomeUtils()

  def _CheckCalledCommand(self, command_object, cmd):
    self.assertEqual(command_object.call_args[0][0], cmd)

  @mock.patch.object(cryptohome_utils.CryptohomeUtils,
                     '_DetermineDeviceManagementBinary', autospec=True)
  @mock.patch.object(process_utils, 'CheckOutput', autospec=True)
  def test_GetFwManagementParameters_Success(self, checkoutput_mock,
                                             binary_mock):
    binary_mock.return_value = 'cryptohome'
    checkoutput_mock.return_value = textwrap.dedent("""
        [user_data_auth.GetFirmwareManagementParametersReply] {
          error: CRYPTOHOME_ERROR_NOT_SET
          fwmp: [user_data_auth.FirmwareManagementParameters] {
            flags: 65 (0x00000041)
            developer_key_hash: 0000000000000000000000000000000000000000000000000000000000000000
          }

        }
        flags=0x00000041
        hash=0000000000000000000000000000000000000000000000000000000000000000
        GetFirmwareManagementParameters success.""")

    parameter = self._cryptohome_util.GetFirmwareManagementParameters()
    self._CheckCalledCommand(
        checkoutput_mock,
        ['cryptohome', '--action=get_firmware_management_parameters'])
    self.assertEqual(parameter.flags, 0x41)
    self.assertEqual(parameter.developer_key_hash,
                     self._TEST_DEVELOPER_KEY_HASH)

  @mock.patch.object(cryptohome_utils.CryptohomeUtils,
                     '_DetermineDeviceManagementBinary', autospec=True)
  @mock.patch.object(process_utils, 'CheckOutput', autospec=True)
  def test_GetFwManagementParameters_Failed(self, checkoutput_mock,
                                            binary_mock):
    binary_mock.return_value = 'cryptohome'
    checkoutput_mock.return_value = textwrap.dedent("""
        [user_data_auth.GetFirmwareManagementParametersReply] {
          error: CRYPTOHOME_ERROR_AUTHORIZATION_KEY_FAILED

        }
        Failed to call GetFirmwareManagementParameters: status 3""")

    with self.assertRaises(cryptohome_utils.CryptohomeUtilError):
      flags = self._cryptohome_util.GetFirmwareManagementParameters()
      self._CheckCalledCommand(
          checkoutput_mock,
          ['cryptohome', '--action=get_firmware_management_parameters'])
      self.assertIsNone(flags)

  @mock.patch.object(cryptohome_utils.CryptohomeUtils,
                     '_DetermineDeviceManagementBinary', autospec=True)
  @mock.patch.object(process_utils, 'CheckOutput', autospec=True)
  def test_SetFwManagementParameters_Flags_Success(self, checkoutput_mock,
                                                   binary_mock):
    binary_mock.return_value = 'cryptohome'
    checkoutput_mock.return_value = textwrap.dedent("""
        [user_data_auth.SetFirmwareManagementParametersReply] {
          error: CRYPTOHOME_ERROR_NOT_SET
        }
        SetFirmwareManagementParameters success.""")

    self._cryptohome_util.SetFirmwareManagementParameters(flags=65)
    self._CheckCalledCommand(checkoutput_mock, [
        'cryptohome', '--action=set_firmware_management_parameters',
        '--flags=65'
    ])

  @mock.patch.object(cryptohome_utils.CryptohomeUtils,
                     '_DetermineDeviceManagementBinary', autospec=True)
  @mock.patch.object(process_utils, 'CheckOutput', autospec=True)
  def test_SetFwManagementParameters_Failed(self, checkoutput_mock,
                                            binary_mock):
    binary_mock.return_value = 'cryptohome'
    checkoutput_mock.side_effect = process_utils.CalledProcessError(1, None)
    checkoutput_mock.return_value = textwrap.dedent("""
        [user_data_auth.SetFirmwareManagementParametersReply] {
          error: CRYPTOHOME_ERROR_FIRMWARE_MANAGEMENT_PARAMETERS_CANNOT_STORE
        }
        Failed to call SetFirmwareManagementParameters: status 27""")

    with self.assertRaises(process_utils.CalledProcessError):
      self._cryptohome_util.SetFirmwareManagementParameters(flags=65)


if __name__ == '__main__':
  unittest.main()
