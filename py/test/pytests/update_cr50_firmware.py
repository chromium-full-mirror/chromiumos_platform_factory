# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# pylint: disable=line-too-long
"""Update Cr50 firmware.

Description
-----------
This test provides two functionalities, toggled by the test argument ``method``.

1. This test calls `gsctool` on DUT to update Cr50 firmware.
   By default, the update of RO happens if the version of the given firmware is
   newer than the version on the chip. The update of RW happens if the version
   of the given firmware is newer or the same as the version on the chip.
   In force RO mode (-q), it forces to update the RO even if the version of the
   given firmware is the same as the version on the chip. The chip will reboot
   automatically after the update.
   In upstart mode (-u), it prevents RW update if the version of the given
   firmware is the same as version on the chip. It also prevents the immediate
   reboot after the update.
2. In `check mode`, this test calls `gsctool` on DUT to check if the cr50
   firmware version is up-to-date.

The Cr50 firmware image to update or compare is either from a given path in
station or DUT, or from the release partition on DUT.

To prepare Cr50 firmware image on station, download the release image with
desired Cr50 firmware image and find the image in DEFAULT_FIRMWARE_PATH below.

Test Procedure
--------------
This is an automatic test that doesn't need any user interaction.

1. Firstly, this test will create a DUT link.
2. If Cr50 firmware image source is from station, the image would be sent to
   DUT.
3. If the Cr50 image is in release partition, the test mounts the release
   partition to get the Cr50 image.
4. If `method` is set to `UPDATE`, DUT runs `gsctool` to update
   Cr50 firmware using the specified Cr50 image.
5. If `method` is set to `CHECK_VERSION`, DUT runs `gsctool` to check
   whether the Cr50 firmware version is greater than or equals to the
   specified Cr50 image.

Dependency
----------
- DUT link must be ready before running this test.
- `gsctool` on DUT.
- Cr50 firmware image must be prepared.

Examples
--------
The standard way to update GSC firmware on the factory line is adding a
"UpdateCr50Firmware" test group or a "UpdateTi50Firmware" test group.

These test groups contain four steps:

1. Update the firmware (pytest: update_cr50_firmware)
2. Reboot (pytest: shutdown)
3. Check firmware version (pytest: update_cr50_firmware)
4. Clear inactivate slot. (for Ti50 only)

Step 1 (update firmware) checks the current firmware version, and decides
       whether to update the firmware or not. If the test updates the firmware,
       device data `device.factory.cr50_update_need_reboot` will be set to
       `True`. Otherwise, it will be set to `False`.
Step 2 (reboot) will be skipped if the device data is set to `False` while
       checking `run-if`.
Step 3 (check firmware) deletes the device data to clean up the state after
       the version is validated as up-to-date.
Step 4 (clear inactivate slot)
       Clear inactivate slot.

"UpdateCr50Firmware"

.. test_list::

  generic_tpm_examples:TPMTests.Cr50Tests.UpdateCr50Firmware

"UpdateTi50Firmware"

.. test_list::

  generic_tpm_examples:TPMTests.Ti50Tests.UpdateTi50Firmware

Sometimes, e.g. b/145973336, it's required to update GSC firmware without
upstart mode.

To update GSC firmware without upstart mode, unset `upstart_mode` argument and
set the pytest as `allow_reboot`. After updated and reboot, the test will be run
again and succeeds in the second run:

.. test_list::

  generic_tpm_examples:TPMTests.CommonTests.UpdateGSCFirmwareWithoutUpstart

To update Cr50 firmware with the Cr50 firmware image in station::

  {
    "pytest_name": "update_cr50_firmware",
    "args": {
      "firmware_file": "/path/on/station/to/cr50.bin.prod",
      "from_release": false
    }
  }

To check if Cr50 firmware version is greater than or equals to the Cr50 image
in the release image:

.. test_list::

  generic_tpm_examples:TPMTests.Cr50Tests.UpdateCr50Firmware.CheckCr50FirmwareVersion

To update the Ti50 firmware version from 0.0.15 (or earlier) to 0.0.16 (or
later) with prepvt firmware. See b/236793753 for more detail:

.. test_list::

  generic_tpm_examples:TPMTests.Ti50Tests.UpdateTi50From0o0o15To0o0o16

"""
# pylint: enable=line-too-long

import enum
import os

from cros.factory.device import device_utils
from cros.factory.test import device_data
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test.utils import gsc_utils
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import sys_utils
from cros.factory.utils import type_utils

from cros.factory.external.chromeos_cli import gsctool


KEY_CR50_UPDATE_NEED_REBOOT = device_data.JoinKeys(device_data.KEY_FACTORY,
                                                   'cr50_update_need_reboot')


class _MethodType(str, enum.Enum):
  UPDATE = 'UPDATE'
  CHECK_VERSION = 'CHECK_VERSION'

  def __str__(self):
    return self.name


class UpdateCr50FirmwareArgs:
  firmware_file: str
  from_release: bool
  skip_prepvt_flag_check: bool
  method: _MethodType
  upstart_mode: bool
  force_ro_mode: bool
  set_recovery_request_train_and_reboot: bool
  check_version_retry_timeout: int


class UpdateCr50FirmwareTest(test_case.TestCase):

  related_components = (test_case.TestCategory.SECURE_ELEMENT, )
  ARGS = [
      Arg(
          'firmware_file', str, 'The full path of the firmware. If not set, '
          'the test will use the default prod firmware path to update the '
          'firmware.', default=None),
      Arg('from_release', bool, 'Find the firmware from release rootfs.',
          default=True),
      Arg(
          'skip_prepvt_flag_check', bool,
          '(deprecated) This flag is deprecated and the firmware will only be '
          'check in finalize.', default=False),
      Arg(
          'method', _MethodType,
          'Specify whether to update the Cr50 firmware or to check the '
          'firmware version.', default=_MethodType.UPDATE),
      Arg(
          'upstart_mode', bool,
          'Use upstart mode to update Cr50 firmware. The DUT will not reboot '
          'automatically after the update.', default=True),
      Arg(
          'force_ro_mode', bool,
          'Force to update the inactive RO even if the RO version on DUT is '
          'the same as given firmware. The DUT will reboot automatically '
          'after the update', default=False),
      Arg(
          'set_recovery_request_train_and_reboot', bool,
          'Set recovery request to VB2_RECOVERY_TRAIN_AND_REBOOT. '
          'For some boards, the device will reboot into recovery mode with '
          'default (v0.0.22) cr50 firmware. Setting this will make the device '
          'update the cr50 firmware and then automatically reboot back to '
          'normal mode after updating cr50 firmware. '
          'See b/154071064 for more details', default=False),
      Arg(
          'check_version_retry_timeout', int,
          'If the version is not matched, retry the check after the specific '
          'seconds.  Set to `0` to disable the retry.', default=10)
  ]
  args: UpdateCr50FirmwareArgs
  ui: test_ui.StandardUI

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()

    self.gsc_utils = gsc_utils.GSCUtils()
    self.gsctool = gsctool.GSCTool(dut=self.dut)
    self.fw_ver = self.gsctool.GetGSCFirmwareVersion()
    self.board_id = self.gsctool.GetBoardID()

  def runTest(self):
    """Update Cr50 firmware."""
    if self.args.firmware_file is None:
      self.assertTrue(
          self.args.from_release,
          'Must set "from_release" to True if not specifiying firmware_file')
    else:
      self.assertEqual(self.args.firmware_file[0], '/',
                       'firmware_file should be a full path')

    self._LogCr50Info()

    if self.args.from_release:
      with sys_utils.MountPartition(self.dut.partitions.RELEASE_ROOTFS.path,
                                    dut=self.dut) as root:
        firmware_files = [
            os.path.join(root, firmware_file)
            for firmware_file in self.gsc_utils.image_paths
        ]
        self._CallMethod(firmware_files)
    else:
      if self.dut.link.IsLocal():
        self._CallMethod([self.args.firmware_file])
      else:
        with self.dut.temp.TempFile() as dut_temp_file:
          self.dut.SendFile(self.args.firmware_file, dut_temp_file)
          self._CallMethod([dut_temp_file])

  def _CallMethod(self, firmware_files):
    session.console.info('Firmware path: %s', firmware_files)
    image_infos = [self.gsctool.GetImageInfo(f) for f in firmware_files]
    msg = f'Image info: {image_infos!r}'
    self.ui.SetState(msg)
    session.console.info(msg)
    if self.args.method == _MethodType.UPDATE:
      self._UpdateCr50Firmware(firmware_files)
    else:
      self._CheckCr50FirmwareVersion(firmware_files)

  def _LogCr50Info(self):
    session.console.info('The DUT is using security chip: %s',
                         self.gsc_utils.device_type)
    session.console.info('Firmware version: %r', self.fw_ver)
    session.console.info('Board ID: %r', self.board_id)

  def _UpdateCr50Firmware(self, firmware_files):
    # If device data exists, it means the FW is updated in the last round and
    # the DUT has rebooted.
    if device_data.GetDeviceData(KEY_CR50_UPDATE_NEED_REBOOT):
      self.PassTask()

    if self.args.set_recovery_request_train_and_reboot:
      self.dut.CheckCall('crossystem recovery_request=0xC4')

    update_result = self.gsctool.UpdateCr50Firmware(
        firmware_files, self.args.upstart_mode, self.args.force_ro_mode)
    session.console.info('Cr50 firmware update complete: %s.', update_result)

    if update_result == gsctool.UpdateResult.NOOP:
      self.PassTask()

    device_data.UpdateDeviceData({KEY_CR50_UPDATE_NEED_REBOOT: True})

    # Wait for the chip to reboot itself.
    if not self.args.upstart_mode:
      self.WaitTaskEnd()

  def _CheckCr50FirmwareVersion(self, firmware_files):

    def _Check():
      update_result = self.gsctool.UpdateCr50Firmware(firmware_files,
                                                      upstart_mode=True)
      if update_result != gsctool.UpdateResult.NOOP:
        raise type_utils.TestFailure('Cr50 firmware is old.')

    try:
      _Check()
    except type_utils.TestFailure:
      if self.args.check_version_retry_timeout <= 0:
        raise
      self.ui.SetState(
          f'Version is old, sleep for '
          f'{int(self.args.check_version_retry_timeout)} seconds and re-check.')
      self.Sleep(self.args.check_version_retry_timeout)
      _Check()

    session.console.info('Cr50 firmware is up-to-date.')
    if device_data.GetDeviceData(KEY_CR50_UPDATE_NEED_REBOOT) is not None:
      device_data.DeleteDeviceData(KEY_CR50_UPDATE_NEED_REBOOT, True)
