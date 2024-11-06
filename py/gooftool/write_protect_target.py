# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import abc
import enum
import logging

from cros.factory.gooftool import common
from cros.factory.test.utils import fpmcu_utils
from cros.factory.utils import sys_interface
from cros.factory.utils.type_utils import Error


class UnsupportedOperationError(Error):
  """Exception for methods that are not supported."""


class WriteProtectError(Error):
  """Failed to enable write protection."""


class WriteProtectTargetType(enum.Enum):
  AP = 'ap'
  EC = 'ec'
  FPMCU = 'fpmcu'


def CreateWriteProtectTarget(
    target: WriteProtectTargetType) -> 'IWriteProtectTarget':
  if target == WriteProtectTargetType.AP:
    return _APWriteProtectTarget()
  if target == WriteProtectTargetType.EC:
    return _ECWriteProtectTarget()
  if target == WriteProtectTargetType.FPMCU:
    return _FPMCUWriteProtectTarget()
  raise TypeError(f'Cannot create IWriteProtectTarget for {target}.')


class IWriteProtectTarget(abc.ABC):

  @abc.abstractmethod
  def SetProtectionStatus(self, enable, skip_enable_check=False):
    """Enables or disables the write protection.

    Args:
      enable: Boolean value, true for enable, false for disable.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def GetStatus(self):
    """Gets the information of the write protection.

    Returns:
      Boolean value: true if WP is enabled, false if WP is disabled.
    """
    raise NotImplementedError


class _APWriteProtectTarget(IWriteProtectTarget):

  def _InvokeCommand(self, param, ignore_status=False):
    command = ' '.join(['futility flash', param])
    result = common.Shell(command)
    if not (ignore_status or result.success):
      raise WriteProtectError(f'Failed in command: {command}\n{result.stderr}')
    return result

  def SetProtectionStatus(self, enable, skip_enable_check=False):
    self._InvokeCommand('--wp-enable' if enable else '--wp-disable')

    # Verify new WP state
    if self.GetStatus() != enable:
      raise WriteProtectError(
          'AP Software write protection could not be changed')

    if enable and not skip_enable_check:
      # Try to verify write protection by attempting to disable it.
      self._InvokeCommand('--wp-disable', ignore_status=True)
      if not self.GetStatus():
        raise WriteProtectError(
            'AP Software write protection can be disabled. Please make '
            'sure hardware write protection is enabled.')

  def GetStatus(self):
    result = self._InvokeCommand('--wp-status --ignore-hw').stdout.strip()

    if result == 'WP status: enabled':
      return True
    if result == 'WP status: disabled':
      return False
    raise WriteProtectError(f'Unexpected WP status: {result}')


class _ECWriteProtectTarget(IWriteProtectTarget):

  def _InvokeCommand(self, param, ignore_status=False):
    command = ' '.join(['ectool flashprotect', param])
    result = common.Shell(command)
    if not (ignore_status or result.success):
      raise WriteProtectError(f'Failed in command: {command}\n{result.stderr}')
    return result

  def SetProtectionStatus(self, enable, skip_enable_check=False):
    self._InvokeCommand('enable now' if enable else 'disable')

    # Verify new WP state
    if self.GetStatus() != enable:
      raise WriteProtectError(
          'EC Software write protection could not be changed')

    if enable and not skip_enable_check:
      # Try to verify write protection by attempting to disable it.
      self._InvokeCommand('disable', ignore_status=True)
      if not self.GetStatus():
        raise WriteProtectError(
            'EC Software write protection can be disabled. Please make '
            'sure hardware write protection is enabled.')

  def GetStatus(self):
    result = self._InvokeCommand('').stdout
    lines = result.split('\n')

    # First line should be active flags
    if len(lines) < 1 or 'Flash protect flags' not in lines[0]:
      raise WriteProtectError(f'Unexpected ectool output: {result}')

    return 'ro_at_boot' in lines[0]


class _FPMCUWriteProtectTarget(IWriteProtectTarget):

  FILE_FPFRAME = 'fp.raw'
  FILE_FPFRAME_ERR_MSG = 'error_msg.txt'

  def __init__(self):
    self._fpmcu = fpmcu_utils.FpmcuDevice(sys_interface.SystemInterface())

  def SetProtectionStatus(self, enable, skip_enable_check=False):
    if enable:
      self._EnableWriteProtect()
    else:
      raise UnsupportedOperationError

  def GetStatus(self):
    raise UnsupportedOperationError

  def _EnableWriteProtect(self):
    """Enables the write protection of the FPMCU.

    The write protection, or more specifically, SWWP, is enabled by the
    following steps:

    1. Reboot the FPMCU. We need to make sure the FPMCU state matches the
       initial state.
    2. Do prerequisite checking:
       - HWWP is enabled.
       - SWWP is disabled.
    3. Request to enable SWWP and reboot FPMCU so that SWWP makes effect.
    4. Validate the final FPMCU state:
       - HWWP and SWWP are both enabled.
       - Image in use is 'RW'.
       - System is locked.

    Raises:
      WriteProtectError:
        when fail to enable write protection.
    """

    def _Assert(expected: bool, assert_message: str):
      if expected:
        logging.info('Check %r: OK', assert_message)
      else:
        raise WriteProtectError(f'Check {assert_message!r}: FAILED')

    # Reboot the FPMCU. We need to make sure the FPMCU state matches the initial
    # state.
    try:
      self._fpmcu.Reboot()
    except fpmcu_utils.FpmcuError as e:
      raise WriteProtectError(f'Failed to reboot FPMCU: {e.message}') from e

    # Do prerequisite checking.
    _Assert(self._fpmcu.IsHWWPEnabled(), 'FPMCU HWWP is enabled')
    _Assert(not self._fpmcu.IsSWWPEnabled(), 'FPMCU SWWP is disabled')

    # Request to enable SWWP and reboot FPMCU so that SWWP makes effect. But
    # before rebooting, check if flags are updated to the expected state.
    try:
      self._fpmcu.RequestToEnableSWWPOnBoot()
      _Assert(self._fpmcu.IsSWWPEnabledOnBoot(),
              'FPMCU SWWP is enabled on boot')
      self._fpmcu.Reboot()
    except fpmcu_utils.FpmcuError as e:
      raise WriteProtectError(f'Failed to reboot FPMCU: {e.message}') from e

    # Validate the final FPMCU state.
    _Assert(self._fpmcu.IsSWWPEnabled(), 'FPMCU SWWP is enabled')
    _Assert(self._fpmcu.IsHWWPEnabled(), 'FPMCU HWWP is enabled')
    _Assert(self._fpmcu.GetImageSlot() == fpmcu_utils.ImageSlot.RW,
            'FPMCU RW image is active')
    _Assert(self._fpmcu.IsSystemLocked(), 'FPMCU system is locked')
