# Copyright 2020 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Detachable base update test

Description
-----------
For detachable projects, the detachable base (as a USB device) may need to be
updated with its standalone EC and touchpad firmware.
This test leverages ``hammerd``, which is the dedicated daemon for updating
detachable base firmware, to help factory automize firmware update and basic
verification.

Test Procedure
--------------
1. Test will try to locate detachable base with the given USB device info.
   If the info is not provided from test lists, the test will try to get it
   from ``cros_config``.
2. Hammerd is invoked to update base's EC and touch firmware. If the path to EC
   or touch firmware is not specified, the test will extract the firmware from
   the release or test rootfs depending on ``from_release``.
3. Verify base is properly updated by probing base info and doing some
   preliminary checkings.

Note that one might want to disable hammerd being inited on boot by configuring
upstart. See `here
<https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/init/preinit.d/inhibit_jobs/README.md>`_
for detail.

In addition, it's recommended to configure detachable base info in
chromeos-config (instead of test lists) with following properties provided:

- ec-image-name
- touch-image-name
- vendor-id
- product-id
- usb-path

So that the it can be maintained in the standalone config and be easily shared
across the system.

Dependency
----------
- chromeos_config (cros_config)
- hammerd
- usb_updater2
- hammer_info.py

Examples
--------
If detachable base information is ready in cros_config and user would like to
update using the images extracted from release rootfs::

  {
    "pytest_name": "update_detachable_base"
  }

If explicitly supplying detachable base info (Krane for example)::

  {
    "pytest_name": "update_detachable_base",
    "args": {
      "from_release": false,
      "usb_path": "1-1.1",
      "product_id": 20540,
      "vendor_id": 6353,
      "ec_image_path": "/lib/firmware/masterball.fw",
      "touchpad_image_path": "/lib/firmware/masterball-touch.fw"
    }
  }
"""

import logging
import os.path
import re

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import process_utils
from cros.factory.utils import sync_utils
from cros.factory.utils import sys_utils


BASE_FW_DIR = '/lib/firmware'

ELAN_VENDOR_ID = 0x04f3
ST_VENDOR_ID = 0x0483
VENDOR_IDS = (ELAN_VENDOR_ID, ST_VENDOR_ID)

class UpdateDetachableBaseTest(test_case.TestCase):
  related_components = tuple()
  ARGS = [
      Arg('from_release', bool, 'Find the firmwares from release rootfs.',
          default=True),
      Arg('usb_path', str, 'USB path for searching the detachable base.',
          default=None),
      Arg('i2c_path', str, 'I2C path for searching the detachable base.',
          default=None),
      Arg('product_id', int, 'Product ID of the USB device.', default=None),
      Arg('vendor_id', int, 'Vendor ID of the USB device.', default=None),
      Arg('ec_image_path', str,
          f'Path to the EC firmware image file under {BASE_FW_DIR}.',
          default=None),
      Arg('touchpad_image_path', str,
          f'Path to the touchpad image file under {BASE_FW_DIR}.',
          default=None),
      Arg('update', bool, 'Update detachable base FW (hammerd is needed)',
          default=True),
      Arg('verify', bool,
          'Verify base info after FW update. (usb_updater2 is needed)',
          default=True),
  ]

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    self.ui.ToggleTemplateClass('font-large', True)

    # Read preconfigured values from cros_config if args are not provided.
    if self.args.usb_path is None:
      self.args.usb_path = self.CrosConfig('usb-path', check_output=False)
    if self.args.i2c_path is None:
      self.args.i2c_path = self.CrosConfig('i2c-path', check_output=False)
    if self.args.product_id is None:
      self.args.product_id = int(self.CrosConfig('product-id'))
    if self.args.vendor_id is None:
      self.args.vendor_id = int(self.CrosConfig('vendor-id'))
    if self.args.ec_image_path is None:
      self.args.ec_image_path = self.dut.path.join(
          BASE_FW_DIR, self.CrosConfig('ec-image-name'))
    if self.args.touchpad_image_path is None:
      self.args.touchpad_image_path = self.dut.path.join(
          BASE_FW_DIR, self.CrosConfig('touch-image-name'))


    assert self.args.usb_path or self.args.i2c_path

    self.device_id = f'{self.args.vendor_id:04x}:{self.args.product_id:04x}'

  def runDetachableTest(self):
    if self.args.update:
      self.ui.SetState(_('Updating base firmware. Do not remove the base.'))
      self.UpdateDetachableBase()
      session.console.info('Base firmware update done.')

    if self.args.verify:
      self.ui.SetState(_('Verifying detachable base information...'))
      # Sleep for a while, because usb_updater2 may not be able to read
      # touchpad info right after FW is flashed.
      self.Sleep(3)

      # Getting info of touchpad on base / EC on base / target EC image
      # respectively.  b/146536191: Must query touchpad info before base EC
      # info.

      ec_info = self.GetBaseInfo()
      fw_info = self.GetFirmwareInfo(self.args.ec_image_path)

      self.VerifyBaseInfo(ec=ec_info, fw=fw_info)
      session.console.info('Detachable base verification done.')

  def runTest(self):
    self.ui.SetState(_('Please connect the detachable base.'))
    sync_utils.PollForCondition(poll_method=self.BaseIsReady, timeout_secs=60,
                                poll_interval_secs=1)

    if self.args.from_release:
      with sys_utils.MountPartition(self.dut.partitions.RELEASE_ROOTFS.path,
                                    dut=self.dut) as root:
        logging.info('Get EC and touch FW images from the release rootfs.')
        self.args.ec_image_path = self.dut.path.join(
            root, self.args.ec_image_path[1:])
        self.args.touchpad_image_path = self.dut.path.join(
            root, self.args.touchpad_image_path[1:])
        self.runDetachableTest()
    else:
      self.runDetachableTest()

  @classmethod
  def CrosConfig(cls, key, check_output=True):
    """Helper method for cros_config key retrieval.

    Args:
      key: The key under detachable-base path.

    Returns:
      The value of the provided key.
    """
    return process_utils.SpawnOutput(['cros_config', '/detachable-base', key],
                                     check_output=check_output, log=True)

  def UpdateDetachableBase(self):
    """Main update method which calls hammerd to do base FW update.

    Raises:
      CalledProcessError if hammerd returns non-zero code.
    """
    minijail0_cmd = ['/sbin/minijail0', '-e', '-N', '-p', '-l',
                     '-u', 'hammerd', '-g', 'hammerd', '-c', '0002']
    if self.args.usb_path:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      device_path = f'--usb_path={self.args.usb_path}'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    else:
      device_path = f'--i2c_path={self.args.i2c_path}'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    hammerd_cmd = [
        '/usr/bin/hammerd',
        '--at_boot=true',
        '--force_inject_entropy=true',
        '--update_if=always',
        f'--product_id={int(self.args.product_id)}',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        f'--vendor_id={int(self.args.vendor_id)}',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        device_path,
        f'--ec_image_path={self.args.ec_image_path}',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        f'--touchpad_image_path={self.args.touchpad_image_path}'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    ]

    try:
      process_utils.Spawn(minijail0_cmd + hammerd_cmd,
                          log=True, check_call=True)
    except process_utils.CalledProcessError as e:
      # Note that hammerd prints log to stderr by default so reading stdout
      # does not help.
      # In addition, hammerd only prints log when stdin is a tty, so we can not
      # read log from stderr when hammerd is invoked by Spawn() either.
      # As a result, log can only be manually retrieved in hammerd.log.
      exit_reason = {
          1:  'kUnknownError',
          10: 'kNeedUsbInfo',
          11: 'kEcImageNotFound',
          12: 'kTouchpadImageNotFound',
          13: 'kUnknownUpdateCondition',
          14: 'kConnectionError',
          15: 'kInvalidFirmware',
          16: 'kTouchpadMismatched',
      }

      if e.returncode in exit_reason:
        logging.error('Hammerd exit reason: %s', exit_reason[e.returncode])
      else:
        logging.error('Hammerd exited due to unknown error.')

      self.FailTask(
          f'Hammerd update failed (exit status {int(e.returncode)}). Please '
          f'check /var/log/hammerd.log for detail.')

  def VerifyBaseInfo(self, ec, fw):
    """Verify base is updated properly by comparing its attributes with the
    target FW.

    Args:
      ec: A dictionary of the keyboard info from hammer_info.py.
      fw: A dictionary of the target EC FW info.
    """
    self.assertEqual(
        ec['ro_version'], fw['ro']['version'],
        f"Base EC may not be properly updated: Base RO version "
        f"{ec['ro_version']} ({fw['ro']['version']} expected).")
    self.assertEqual(
        ec['rw_version'], fw['rw']['version'],
        f"Base EC may not be properly updated: Base RW version "
        f"{ec['rw_version']} ({fw['rw']['version']} expected).")
    self.assertIn(
        int(ec['touchpad_pid'], 16), VENDOR_IDS,
        f"Touchpad may not be properly updated: Vendor {ec['touchpad_pid']} "
        f"(any of {[hex(x) for x in VENDOR_IDS]} expected).")
    self.assertNotEqual(
        ec['touchpad_fw_checksum'], '0x0000',
        f"Touchpad may not be properly updated: checksum "
        f"{ec['touchpad_fw_checksum']} (unexpected).")
    self.assertGreaterEqual(
        int(ec['key_version']), 3,
        f'key version not greater or higher than MP (>= 3), used key version: '
        f"{ec['key_version']}")
    self.assertEqual(ec['wp_screw'], 'True', 'Hardware WP not enabled')
    self.assertEqual(ec['wp_all'], 'True', 'Software WP not enabled')

  def BaseIsReady(self):
    if self.args.usb_path:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      try:
        process_utils.CheckCall(['lsusb', '-d', self.device_id])
      except process_utils.CalledProcessError:
        return 0
      return 1
    return os.path.exists(os.path.join("/sys/bus/i2c/devices/",
                                       self.args.i2c_path))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

  def GetBaseInfo(self):
    """Retrieve and parse on-board EC info.

    Returns:
      A dictionary containing on-board EC info.
    """
    output = process_utils.LogAndCheckOutput(['hammer_info.py'])
    return dict(re.findall(r'(\S+)="(\S+?)"', output))

  def GetFirmwareInfo(self, fw_path):
    """Retrieve and parse given EC FW info.

    Args:
      fw_path: The absolute path to target EC FW image.

    Returns:
      A dictionary containing target EC FW info.
    """
    key_trans = {
        'v': 'version',
        'rb': 'rollback',
        'off': 'offset',
        'kv': 'key_version',
    }
    res = {'ro': {}, 'rw': {}}

    for line in process_utils.LogAndCheckOutput(['usb_updater2', '-b',
                                                 fw_path]).splitlines():
      mode, *rest = line.split()
      if mode in ('RO', 'RW'):
        for kv in rest:
          k, v = kv.split('=', 1)
          if k in key_trans:
            res[mode.lower()][key_trans[k]] = v.strip()

    return res
