# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A test to check PDC firmware information.

Description
-----------
This test checks the PDC firmware version, name, and driver against expected
values or minimum versions.

Test Procedure
--------------
This is an automated test without user interaction.

1. Retrieve the PDC firmware information using `ectool pdchipinfo usbpdid`.
2. Compare the retrieved information with the expected values (if provided).
3. Compare the retrieved version information with the minimum versions (if
   provided).


Dependency
----------
- ``ectool``

Examples
--------
To check if the PDC firmware version is "0.0.0.0.0.0.27.1"::

    {
      "pytest_name": "check_pdc_firmware",
      "args": {
        "expected_fw_version_dec": "0.0.0.0.0.0.27.1",
        "expected_fw_name_str": "GOOG0000",
        "expected_driver_name": "realtek_rts54_pdc",
        "usb_pd_id": 0
      }
    }

To check if the PDC firmware version is at least "0.0.0.0.0.0.27.0"::

    {
      "pytest_name": "check_pdc_firmware",
      "args": {
        "min_fw_version_dec": "0.0.0.0.0.0.27.0",
        "usb_pd_id": 0
      }
    }

"""
import logging
import re
from typing import Dict

from packaging import version

from cros.factory.device import device_utils
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg


class CheckPDCFirmwareArgs:
  expected_fw_version_dec: str
  min_fw_version_dec: str
  expected_fw_name_str: str
  expected_driver_name: str
  usb_pd_id: int


class CheckPDCFirmwareTest(test_case.TestCase):
  """Check the PDC firmware information."""
  related_components = tuple()

  ARGS = [
      Arg('expected_fw_version_dec', str, 'Expected PDC firmware version.',
          default=None),
      Arg('min_fw_version_dec', str, 'Minimum PDC firmware version.',
          default=None),
      Arg('expected_fw_name_str', str, 'Expected PDC firmware name string.',
          default=None),
      Arg('expected_driver_name', str, 'Expected PDC driver name.',
          default=None),
      Arg('usb_pd_id', int, 'USB PD ID of the PDC chip.', default=0),
  ]

  args: CheckPDCFirmwareArgs

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    self.expected_fw_version_dec = self.args.expected_fw_version_dec
    self.min_fw_version_dec = self.args.min_fw_version_dec
    self.expected_fw_name_str = self.args.expected_fw_name_str
    self.expected_driver_name = self.args.expected_driver_name
    self.usb_pd_id = self.args.usb_pd_id

  def runTest(self):
    """Retrieves and verifies the PDC firmware information."""
    fw_info = self._GetPDCFirmwareInfo()
    logging.info('DUT PDC firmware information: %s', fw_info)

    if self.expected_fw_version_dec:
      if self.min_fw_version_dec:
        self.FailTask(
            'If expected_fw_version_dec is set, min_fw_version_dec should not '
            'be set.')

      expected_version = version.parse(self.expected_fw_version_dec)
      if fw_info['fw_version_dec'] != expected_version:
        self.FailTask(
            f'DUT PDC firmware version is {fw_info["fw_version_dec"]}, '
            f'expected {expected_version}')
    elif self.min_fw_version_dec:
      min_version = version.parse(self.min_fw_version_dec)
      if version.parse(fw_info['fw_version_dec']) < min_version:
        self.FailTask(
            f'DUT PDC firmware version is {fw_info["fw_version_dec"]}, '
            f'should be at least {min_version}')

    if self.expected_fw_name_str and fw_info[
        'fw_name_str'] != self.expected_fw_name_str:
      self.FailTask(
          f'DUT PDC firmware name string is {fw_info["fw_name_str"]}, '
          f'expected {self.expected_fw_name_str}')

    if self.expected_driver_name and fw_info[
        'driver_name'] != self.expected_driver_name:
      self.FailTask(f'DUT PDC driver name is {fw_info["driver_name"]}, '
                    f'expected {self.expected_driver_name}')

  def _GetPDCFirmwareInfo(self) -> Dict[str, str]:
    """Retrieves and formats the PDC firmware information.

    Returns:
      dict: The formatted PDC firmware information.
    """
    output = self.dut.CheckOutput(['ectool', 'pdchipinfo', str(self.usb_pd_id)])
    fw_info: Dict[str, str] = {}

    match = re.search(r'fw_version_dec: (\S+)', output)
    if not match:
      raise ValueError(f"Couldn't find fw_version_dec in output: {output}")
    fw_info['fw_version_dec'] = match.group(1)

    match = re.search(r"fw_name_str: '(\S+)'", output)
    if not match:
      raise ValueError(f"Couldn't find fw_name_str in output: {output}")
    fw_info['fw_name_str'] = match.group(1)

    match = re.search(r"driver_name: '(\S+)'", output)
    if not match:
      raise ValueError(f"Couldn't find driver_name in output: {output}")
    fw_info['driver_name'] = match.group(1)

    return fw_info
