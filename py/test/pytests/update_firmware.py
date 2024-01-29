# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Runs chromeos-firmwareupdate to force update Main(AP)/EC/PD firmwares.

Description
-----------
This test runs firmware updater from local storage or downloaded from remote
factory server to update Main(AP)/EC/PD firmware contents.

Test Procedure
--------------
This is an automatic test that doesn't need any user interaction.

1. If argument ``download_from_server`` is set to True, this test will try to
   download firmware updater from factory server and ignore argument
   ``firmware_updater``. If firmware update is not available, this test will
   just pass and exit. If argument ``download_from_server`` is set to False and
   the path indicated by argument ``firmware_updater`` doesn't exist, this test
   will abort.
2. This test will fail if there is another firmware updater running in the same
   time. Else, start running firmware updater.
3. If firmware updater finished successfully, this test will pass.
   Otherwise, fail.

Dependency
----------
- If argument ``download_from_server`` is set to True, firmware updater needs to
  be available on factory server. If ``download_from_server`` is set to False,
  firmware updater must be prepared in the path that argument
  ``firmware_updater`` indicated.

Examples
--------
To update all firmwares using local firmware updater, which is located in
'/usr/local/factory/board/chromeos-firmwareupdate'::

  {
    "pytest_name": "update_firmware"
  }

To update only RW Main(AP) firmware using remote firmware updater::

  {
    "pytest_name": "update_firmware",
    "args": {
      "download_from_server": true,
      "rw_only": true,
      "host_only": true
    }
  }

Not to update firmware if the version is the same with current one
in the DUT::

  {
    "pytest_name": "update_firmware",
    "args": {
      "force_update": false
    }
  }
"""

import contextlib
import logging
import os
import tempfile
from typing import List

from cros.factory.device import device_utils
from cros.factory.test.env import paths
from cros.factory.test import event
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test.utils import gsc_utils
from cros.factory.test.utils import update_utils
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import file_utils
from cros.factory.utils import process_utils
from cros.factory.utils import sys_utils

from cros.factory.external.chromeos_cli import futility
from cros.factory.external.chromeos_cli import ifdtool


_FIRMWARE_UPDATER_NAME = 'chromeos-firmwareupdate'
_FIRMWARE_RELATIVE_PATH = 'usr/sbin/chromeos-firmwareupdate'



class NoUpdatesException(Exception):
  pass


class IntelDescriptorHasLockedException(Exception):
  pass


class UpdateFirmwareTest(test_case.TestCase):
  related_components = (
      test_case.TestCategory.EC,
      test_case.TestCategory.SPIFLASH,
  )
  ARGS = [
      Arg('firmware_updater', str, f'Full path of {_FIRMWARE_UPDATER_NAME}.',
          default=paths.FACTORY_FIRMWARE_UPDATER_PATH),
      Arg('rw_only', bool, 'Update only RW firmware', default=False),
      # Updating only EC/PD is not supported.
      Arg('host_only', bool, 'Update only host (AP, BIOS) firmware.',
          default=False),
      Arg('download_from_server', bool, 'Download firmware updater from server',
          default=False),
      Arg('from_release', bool, 'Find the firmware from release rootfs.',
          default=False),
      Arg('force_update', bool,
          'force to update firmware even if the version is the same.',
          default=True),
      Arg(
          'unlock_csme', bool, 'Unlock the Intel CSME from the updater before '
          'flashing. Please read the comments in '
          'UpdateFirmwareForIntelTi50Device for the expected update results.',
          default=True),
  ]

  ui_class = test_ui.ScrollableLogUI

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self._is_ti50 = gsc_utils.GSCUtils().IsTi50()

  def DownloadFirmware(self, force_update, target_path):
    """Downloads firmware updater from server."""
    updater = update_utils.Updater(update_utils.Components.firmware)
    if not updater.IsUpdateAvailable():
      logging.warning('No firmware updater available on server.')
      return False

    rw_version = self._dut.info.firmware_version
    ro_version = self._dut.info.ro_firmware_version

    current_version = f'ro:{ro_version};rw:{rw_version}'

    if not updater.IsUpdateAvailable(
        current_version, match_method=update_utils.MatchMethod.substring):
      logging.info('Your firmware is already in same version as server (%s)',
                   updater.GetUpdateVersion())
      if not force_update:
        return False

    updater.PerformUpdate(destination=target_path)
    os.chmod(target_path, 0o755)
    return True

  def IsIntelFirmware(self, fw_image):
    return fw_image.GetFirmwareImage().has_section(ifdtool.IntelLayout.ME.value)

  def UpdateFirmwareForIntelTi50Device(
      self, command: List[str], fw_image: ifdtool.IntelMainFirmwareContent):
    """A special logic for handling FW update on an Intel device with Ti50.

    Below we summarize the possible descriptor status of the DUT and updater,
    the update result and the corresponding scenario.

    Terminology:
    - SI_DESC and SI_ME: Intel specific FW regions, which cannot be modified
      once SI_DESC is locked unless using servo.
    - RO: ChromeOS read-only FW, which is protected by the HW write-protection.
    - RW: ChromeOS read-write FW.
    - L: SI_DESC is locked; U: SI_DESC is unlocked.
    -----------------------------------------------------------
    | Updater  | DUT |      Update Result      |   Scenario   |
    -----------------------------------------------------------
    |    L     |  L  |        RO* + RW         |     RMA      |
    -----------------------------------------------------------
    |    L     |  U  |        SI_DESC**        |    Factory   |
    -----------------------------------------------------------
    |    U     |  L  |        Exception        |      X       |
    -----------------------------------------------------------
    |    U     |  U  |SI_DESC + SI_ME + RO + RW|    Factory   |
    -----------------------------------------------------------
    *:  RO will only be updated if the SI_DESC in the updater and the DUT
        are the same.
    **: To avoid overwriting provisioned data (e.g., PSR) in SI_ME, we lock
        the firmware by flashing only the SI_DESC region from the updater.
    """
    _, dut_locked = fw_image.GenerateAndCheckLockedDescriptor()
    updater_locked = not self.args.unlock_csme
    logging.info('Intel descriptor status: %s',
                 'Locked' if dut_locked else 'Unlocked')
    logging.info('Updater descriptor status: %s',
                 'Locked' if updater_locked else 'Unlocked')

    if updater_locked and dut_locked:
      self.RunUpdaterAndCheckResult(command)
    elif updater_locked and not dut_locked:
      logging.info('Locking the descriptor...')
      with file_utils.TempDirectory() as temp_dir:
        command += ['--mode=output', f'--output_dir={temp_dir}']
        self.RunUpdaterAndCheckResult(
            command, 'Fail to extract firmware from the updater')
        fw_image.WriteDescriptor(
            filename=self._dut.path.join(temp_dir, 'bios.bin'))
    elif not updater_locked and dut_locked:
      raise IntelDescriptorHasLockedException(
          'Descriptor has already been locked! Cannot flash unlocked FW. '
          'Please set argument `unlock_csme` to false.')
    else:
      command += ['--quirks=unlock_csme']
      self.RunUpdaterAndCheckResult(command)

  def RunUpdaterAndCheckResult(self, command: List[str],
                               error_msg: str = 'Firmware update failed'):
    returncode = self.ui.PipeProcessOutputToUI(command)

    # Updates system info so EC and Firmware version in system info box
    # are correct.
    self.event_loop.PostEvent(event.Event(event.Event.Type.UPDATE_SYSTEM_INFO))

    self.assertEqual(returncode, 0, f'{error_msg}: {int(returncode)}.')

  def UpdateFirmware(self):
    """Runs firmware updater.

    While running updater, it shows updater activity on factory UI.
    """
    # Remove /tmp/chromeos-firmwareupdate-running if the process
    # doesn't seem to be alive anymore.  (http://crosbug.com/p/15642)
    LOCK_FILE = f'/tmp/{_FIRMWARE_UPDATER_NAME}-running'
    if os.path.exists(LOCK_FILE):
      process = process_utils.Spawn(['pgrep', '-f', _FIRMWARE_UPDATER_NAME],
                                    call=True, log=True, read_stdout=True)
      if process.returncode == 0:
        # Found a chromeos-firmwareupdate alive.
        self.FailTask(
            f"Lock file {LOCK_FILE} is present and firmware update already "
            f"running (PID {', '.join(process.stdout_data.split())})")
        return
      logging.warning('Removing %s', LOCK_FILE)
      os.unlink(LOCK_FILE)

    command = [self.args.firmware_updater, '--force']
    if self.args.host_only:
      command += ['--host_only']
    if self.args.rw_only:
      command += ['--mode=recovery', '--wp=1']
    else:
      command += ['--mode=factory']

    # AP RO verification v2 protects RO as a whole, including Intel's SI_DESC.
    # We thus cannot update the firmware arbitrarily.
    # We use the special logic in UpdateFirmwareForIntelTi50Device to handle
    # Intel's firmware update.
    if self._is_ti50:
      fw_image = ifdtool.LoadIntelMainFirmware()
      if self.IsIntelFirmware(fw_image):
        logging.info('DUT is an Intel device with Ti50.')
        self.UpdateFirmwareForIntelTi50Device(command, fw_image)
        return

    self.RunUpdaterAndCheckResult(command)

  def runTest(self):
    # Either download_from_server or from_release can be True.
    self.assertFalse(self.args.download_from_server and self.args.from_release)
    if self._is_ti50:
      logging.info('Current RLZ code in RO_GSCVD: %s',
                   futility.Futility().GetRLZFromROGSCVD())

    @contextlib.contextmanager
    def GetUpdater():
      if self.args.download_from_server:
        # The temporary folder will not be removed after this test finished
        # for the convenient of debugging.
        temp_path = os.path.join(
            tempfile.mkdtemp(prefix='test_fw_update_', dir='/usr/local/tmp'),
            _FIRMWARE_UPDATER_NAME)
        if self.DownloadFirmware(
            self.args.force_update, temp_path):
          yield temp_path
        else:
          raise NoUpdatesException
      elif self.args.from_release:
        with sys_utils.MountPartition(
            self._dut.partitions.RELEASE_ROOTFS.path, dut=self._dut) as root:
          yield os.path.join(root, _FIRMWARE_RELATIVE_PATH)
      else:
        yield self.args.firmware_updater

    try:
      with GetUpdater() as updater_path:
        self.assertTrue(
            os.path.isfile(updater_path), msg=f'{updater_path} is missing.')
        self.args.firmware_updater = updater_path
        self.UpdateFirmware()
    except NoUpdatesException:
      pass
    else:
      if self._is_ti50:
        logging.info('New RLZ code in RO_GSCVD: %s',
                     futility.Futility().GetRLZFromROGSCVD())
        gsc_utils.GSCUtils().VerifyBrandCode()
