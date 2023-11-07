# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from collections import namedtuple
import enum
import os
import re
from typing import List

from cros.factory.utils import process_utils
from cros.factory.utils.type_utils import Error


FWMP = namedtuple('FWMP', ['flags', 'developer_key_hash'])


class CryptohomeUtilError(Error):
  pass


class FirmwareManagementParametersFlags(enum.IntEnum):
  # pylint: disable=line-too-long
  """The definition to the FWMP flags.

  Please visit <https://source.chromium.org/chromium/chromium/src/+/main:third_party/cros_system_api/dbus/cryptohome/rpc.proto>
  to see where its originally defined.

  """
  DEVELOPER_DISABLE_BOOT = 1
  DEVELOPER_DISABLE_RECOVERY_INSTALL = 2
  DEVELOPER_DISABLE_RECOVERY_ROOTFS = 4
  DEVELOPER_ENABLE_USB = 8
  DEVELOPER_ENABLE_LEGACY = 16
  DEVELOPER_USE_KEY_HASH = 32
  DEVELOPER_DISABLE_CASE_CLOSED_DEBUGGING_UNLOCK = 64


class CryptohomeCmdActions(str, enum.Enum):
  SET_FW_MANAGEMENT_PARAM = 'set_firmware_management_parameters'
  GET_FW_MANAGEMENT_PARAM = 'get_firmware_management_parameters'

  def __str__(self):
    return self.value


class CryptohomeUtils:

  def _BuildCmd(self, binary, **kwargs) -> List[str]:
    cmd = [binary]
    for k, v in kwargs.items():
      cmd.append(f'--{k}={v}')
    return cmd

  def _DetermineDeviceManagementBinary(self):
    preferred_binary = '/usr/sbin/device_management_client'
    if os.path.exists(preferred_binary):
      return preferred_binary
    return 'cryptohome'  # fallback for older images

  def _ParseFirmwareManagementParameters(self, stdout: str) -> FWMP:
    match = re.search(r'flags=(?P<flags>.*)(\r\n|\r|\n)hash=(?P<hash>.*)',
                      stdout, re.MULTILINE)
    if match:
      return FWMP(
          flags=int(match.groupdict()['flags'], 16),
          developer_key_hash=match.groupdict()['hash'])
    raise CryptohomeUtilError(
        f'Cannot parse FW management flag from stdout:\n{stdout}')

  def GetFirmwareManagementParameters(self) -> FWMP:
    """Gets the firmware management parameters.

    Leverages `cryptohome` binary to get firmware management parameters.
    Please be noted that this part of functionality of `cryptohome` will be
    replaced by independent binary `device_management_client` so we will only
    use `cryptohome` as a fallback option.

    Returns:
      FWMP namedtuple with two field names: flags and developer_key_hash.

    Raises:
      process_utils.CalledProcessError if the command execution failed.

    """
    binary = self._DetermineDeviceManagementBinary()
    cmd = self._BuildCmd(binary,
                         action=CryptohomeCmdActions.GET_FW_MANAGEMENT_PARAM)
    stdout = process_utils.CheckOutput(cmd, log=True)
    return self._ParseFirmwareManagementParameters(stdout)

  def SetFirmwareManagementParameters(self, *, flags):
    """Sets the firmware management parameters.

    Leverages `cryptohome` binary to get firmware management parameters.
    Please be noted that this part of functionality of `cryptohome` will be
    replaced by independent binary `device_management_client` so we will only
    use `cryptohome` as a fallback option.

    Args:
      flags: The FirmwareManagementParametersFlags to be set.

    Raises:
      process_utils.CalledProcessError if the command execution failed.

    """

    binary = self._DetermineDeviceManagementBinary()
    cmd = self._BuildCmd(binary,
                         action=CryptohomeCmdActions.SET_FW_MANAGEMENT_PARAM,
                         flags=flags)
    process_utils.CheckOutput(cmd, log=True)
