# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import filecmp
import logging
import os
import re
import shlex
from subprocess import CalledProcessError
from subprocess import PIPE
from subprocess import STDOUT
from subprocess import TimeoutExpired
import tempfile
from typing import List

from cros.factory.utils import net_utils
from cros.factory.utils import process_utils


class FastbootUtil:
  """A utility wrapper class for fastboot commands."""

  serial_device = ''
  img_src_dir = ''

  def _FastbootCheckOutput(self, args: List) -> str:
    """Runs fastboot command and collect its output.

    Note that the `fastboot` raw command directs progress output to `stderr`
    so we'll need to handle it correctly in order to preserve information.

    Args:
      args: A list of arguments to be executed

    Raises:
      `process_utils.CalledProcessError` if the command call failed.

    Returns:
      Combined stdout / stderr output as string.
    """

    cmd = ['fastboot', '-s', self.serial_device] + args
    output = process_utils.CheckOutput(cmd, stderr=STDOUT)
    logging.debug('DUT [%s] finished fastboot cmd: %s\n--- OUTPUT ---\n%s',
                  self.serial_device, shlex.join(cmd), output)
    return output

  def _FastbootCheckOutputWithTimeout(self, args: List) -> str:
    """Runs fastboot command with timeout and collect its output.

    Runs a command and raises SubprocessIdleTimeoutError if there's no output
    for more than idle_timeout seconds.

    Note that the `fastboot` raw command directs progress output to `stderr`
    so we'll need to handle it correctly in order to preserve information.

    Args:
      args: A list of arguments to be executed
      idle_timeout: The idle time limit for executing a single fastboot command.

    Raises:
      `subprocess.CalledProcessError` if the command call failed.
      `subprocess.TimeoutExpired` if the subprocess becomes idle for too long.

    Returns:
      Combined stdout / stderr output as string.
    """

    cmd = ['fastboot', '-s', self.serial_device] + args
    try:
      process = process_utils.Spawn(
          cmd,
          stdout=PIPE,
          stderr=STDOUT,
          encoding='utf-8',
      )
      last_output_len = 0

      while process.poll() is None:
        try:
          # try to get process's output
          process.communicate(timeout=self.idle_timeout)
        except TimeoutExpired as e:
          partial_output = e.stdout
          # An increasing partial output indicates that the process is not idle
          if partial_output and len(partial_output) > last_output_len:
            last_output_len = len(partial_output)
          else:
            raise e

      # process.communicate() returns all stdout and stderr even though
      # we have called it before.
      stdout, unused_stderr = process.communicate()

      logging.debug('DUT [%s] fastboot cmd exited: %s\n--- OUTPUT ---\n%s',
                    self.serial_device, shlex.join(cmd), stdout)
      retcode = process.poll()
      if retcode and retcode != 0:
        raise CalledProcessError(retcode, cmd, output=stdout)

      if stdout:
        return stdout
      return ''
    finally:
      if process and process.poll() is None:
        process.terminate()

  def _FastbootSpawn(self, args: List, terminate_token: str = '') -> None:
    """Runs a fastboot command.

    Args:
      terminate_token: If not None, terminate process when reading the token.
    """

    process = process_utils.Spawn(['fastboot', '-s', self.serial_device] + args,
                                  stderr=PIPE)

    # Some commands will wait for the connection to be back up, such as
    # `reboot fastboot`, but it was tested that even though the connection
    # is coming back with the same DHCP leased IP, it still cannot get back
    # to work properly, and we have to manually terminate it.
    if terminate_token:
      for line in process.stderr:  # type: ignore
        if terminate_token in line:
          process.terminate()

  def FlashMbrAndGptTable(self):
    """Flashes custom made MBR & GPT partition table onto the disk."""

    logging.debug('DUT [%s] Flashing MBR & GPT', self.serial_device)
    gpt_file = os.path.join(self.img_src_dir, 'mbr-gpt.bin')
    self.FastbootCheckOutputExecutor(['flash', 'raw-sector:0', gpt_file])

  def SetActive(self, slot_name: str):
    """Sets the designated slot to be active."""
    self.FastbootCheckOutputExecutor(['set_active', slot_name])

  def FlashBootPartitions(self) -> None:
    """Flashes essential partitions to boot."""

    # TODO(stevesu): swap to fastboot-info or managed by configuration
    logging.debug('DUT [%s] Flashing boot partitions', self.serial_device)

    self.SetActive('a')
    self.Flash('boot')
    self.Flash('init_boot')
    self.Flash('pvmfw')
    self.Flash('vendor_boot')
    self.Flash('vbmeta')
    for partition_name, img_path in self.other_partitions_to_flash.items():
      self.Flash(partition_name, img_path)

  def FlashOtherPartitions(self) -> None:
    """Flashes non-boot essential partitions."""

    # TODO(stevesu): swap to fastboot-info or managed by configuration
    logging.debug('DUT [%s] Flashing non-boot partitions', self.serial_device)
    self.Flash('super')

  def RebootToUserSpaceFastboot(self) -> None:
    """Sends reboot fastboot command to boot into user space fastboot."""

    logging.debug('DUT [%s] Reboot to fastboot', self.serial_device)
    self._FastbootSpawn(['reboot', 'fastboot'],
                        terminate_token='OKAY')

  def RebootToBootloader(self) -> None:
    """Sends reboot fastboot command to reboot to bootloader."""

    logging.debug('DUT [%s] Reboot to bootloader', self.serial_device)
    self._FastbootCheckOutputWithTimeout(['reboot', 'bootloader'])

  def Reboot(self) -> None:
    """Reboots the device with fastboot command."""

    logging.debug('DUT [%s] Reboot', self.serial_device)
    self._FastbootCheckOutputWithTimeout(['reboot'])

  def GetAllVar(self) -> str:
    """Gets all variables via fastboot.

    Returns:
      String outputs of all variables collected via fastboot command.
    """

    return self.FastbootCheckOutputExecutor(['getvar', 'all'])

  def GetVarWithKey(self, key: str) -> str:
    """Gets the value of a specific key

    Args:
      key: A string to the key name

    Returns:
      The parsed value as string, or None if the key does not exist
    """

    out = self.FastbootCheckOutputExecutor(['getvar', f'{key}'])
    match = re.search(rf'{key}:\s*(\w+)', out)

    value = ''
    if match:
      value = match.group(1)
    return value

  def GetIsUserSpace(self) -> bool:
    """Gets the state of the fastboot session.

    Returns:
      `True` if it's now in the userspace fastboot, vise versa.
    """

    return 'yes' == self.GetVarWithKey('is-userspace')

  def GetProductName(self) -> str:
    """Gets the product name via fastboot command.

    Note that currently the product name may be different among firmware
    fastboot and userspace fastboot. For example, for brya-dochi device,
    firmware fastboot will return its firmware variant dochi, but userspace
    fastboot will return its board / product name as brya.
    """

    return self.GetVarWithKey('product')

  def ErasePartition(self, partition_name: str) -> None:
    """Erase the specified partition"""
    self.FastbootCheckOutputExecutor(['erase', partition_name])

  def EraseUserdata(self) -> None:
    """Erase the userdata partition.

    Erase the userdata by zero out the beginning of the userdata partition.
    """
    logging.debug('DUT [%s] Erasing userdata', self.serial_device)
    with tempfile.NamedTemporaryFile(dir='/tmp') as f:
      cmd = ['dd', 'if=/dev/zero', f'of={f.name}', 'bs=1M', 'count=2']
      process_utils.CheckCall(cmd)
      self.FastbootCheckOutputExecutor(['flash', 'userdata', f.name])

  def FlashAll(self, reboot=False) -> None:
    """Flashes all partitions.

    For `fastboot flashall`, it will try to locate the `ANDROID_PRODUCT_OUT`
    environment variable for the directory that stores the raw `.img` files.

    Note that this function can only be used under TCP fastboot as long
    as the DHCP leased ip is set to be static, otherwise the fastboot instance
    will try to wait for the connection to come back up but oftentime the
    DHCP leased ip would be different between firmware & userspace fastboot.

    Note that for `flashall` to work, the image source folder will have to
    include `fastboot-info.txt` and `android-info.txt`. The partition will
    be flashed sequentially according to the definition in fastboot-info.txt.

    Args:
      reboot: Whether to reboot after `flashall`.

    """
    logging.debug('DUT [%s] Flashing all partitions', self.serial_device)
    if reboot:
      self.FastbootCheckOutputExecutor(['flashall'])
    else:
      self.FastbootCheckOutputExecutor(['flashall', '--skip-reboot'])

  def Flash(self, partition_name: str, img_path: str = '') -> None:
    """Flashes a single partition.

    When `img_path` is provided, flash `image_path` onto the `partition_name`
    partition. Otherwise, flash `partition_name.img` onto the `partition_name`
    partition.
    """
    if img_path:
      self.FastbootCheckOutputExecutor(['flash', partition_name, img_path])
    else:
      self.FastbootCheckOutputExecutor(['flash', partition_name])

  def ReadUFSDescriptor(self, config_id: int, lun: int = 0) -> None:
    self.FastbootCheckOutputExecutor(
        ['oem', f'read-ufs-descriptor:{config_id},{lun}'])

  def WriteUFSDescriptor(self, config_id: int, lun: int = 0) -> None:
    self.FastbootCheckOutputExecutor(
        ['oem', f'write-ufs-descriptor:{config_id},{lun}'])

  def GetStaged(self, file_name: str) -> None:
    self.FastbootCheckOutputExecutor(['get_staged', file_name])

  def Stage(self, file_name: str) -> None:
    self.FastbootCheckOutputExecutor(['stage', file_name])

  def UFSProvision(self, factory_ufs_path) -> bool:
    """Provisions the UFS storage.

    Retrieves UFS descriptors via fastboot and generates a target configuration
    with factory_ufs binary. The device is provisioned only if the generated
    configuration differs from the one on device.

    Args:
      factory_ufs_path: The path to factory_ufs binary.

    Returns:
      True if provision was done by this command.
      False if provision was skipped since the config on device is same
      as target.
    """

    logging.debug('DUT [%s] Start provisioning UFS', self.serial_device)
    with tempfile.TemporaryDirectory() as temp_dir:
      device_descriptor_path = os.path.join(temp_dir, "device_descriptor.bin")
      geometry_descriptor_path = os.path.join(temp_dir,
                                              "geometry_descriptor.bin")
      config_descriptor_path = os.path.join(temp_dir, "config_descriptor.bin")
      output_path = os.path.join(temp_dir, "provision_config_descriptor.bin")

      self.ReadUFSDescriptor(0)
      self.GetStaged(device_descriptor_path)

      self.ReadUFSDescriptor(7)
      self.GetStaged(geometry_descriptor_path)

      self.ReadUFSDescriptor(1)
      self.GetStaged(config_descriptor_path)

      file_provision_cmd = [
          factory_ufs_path, 'provision-file', '-d', device_descriptor_path,
          '-g', geometry_descriptor_path, '-c', config_descriptor_path, '-o',
          output_path
      ]
      process_utils.CheckOutput(file_provision_cmd, stderr=STDOUT)

      if filecmp.cmp(config_descriptor_path, output_path, shallow=False):
        logging.debug(
            'DUT [%s] Provision skipped since the target configuration '
            'is identical to the one currently on the device',
            self.serial_device)
        return False

      self.Stage(output_path)
      self.WriteUFSDescriptor(1)
      logging.debug('DUT [%s] Finish provisioning UFS', self.serial_device)
      return True

  def __init__(self, _img_src_dir, _idle_timeout):
    self.img_src_dir = _img_src_dir
    self.idle_timeout = _idle_timeout
    os.environ['ANDROID_PRODUCT_OUT'] = self.img_src_dir

    self.other_partitions_to_flash = {}
    other_partitions_name = ['dtbo', 'bluetooth', 'dsp', 'modem', 'persist']
    for name in other_partitions_name:
      img_path = os.path.join(self.img_src_dir, f'{name}.img')
      if os.path.isfile(img_path):
        self.other_partitions_to_flash[name] = img_path

    if self.idle_timeout > 0:
      self.FastbootCheckOutputExecutor = self._FastbootCheckOutputWithTimeout
    else:
      self.FastbootCheckOutputExecutor = self._FastbootCheckOutput


class FastbootTcpUtil(FastbootUtil):
  """A util class wrapper for fastboot over TCP."""

  def __init__(self, ip, img_src, idle_timeout):
    super().__init__(img_src, idle_timeout)
    self.serial_device = f'tcp:{ip}:5554'
    logging.info('DUT [%s] Start the task.', self.serial_device)


class FastbootUsbUtil(FastbootUtil):
  """A util class wrapper for fastboot over USB."""

  # TODO(stevesu): Implement & test this. It should be as simple as supplying
  # the USB device name for the given cable.
  def __init__(self, cable_name, img_src, idle_timeout):
    super().__init__(img_src, idle_timeout)
    self.serial_device = f'{cable_name}'


def FastbootRunnerFactory(dut_info: str, img_src_dir: str,
                          idle_timeout: int) -> FastbootUtil:
  """A util factory function to create fastboot runner."""

  try:
    family = net_utils.ConvertIPtoFamily(ip_str=dut_info)
    if family == net_utils.IpAddressFamily.ipv4:
      return FastbootTcpUtil(dut_info, img_src_dir, idle_timeout)
  except ValueError:
    pass
  return FastbootUsbUtil(dut_info, img_src_dir, idle_timeout)
