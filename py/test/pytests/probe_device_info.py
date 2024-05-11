# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A factory test for probing device information and updating device data.

Description
-----------
Probes device information, including Wi-Fi MAC address, Bluetooth MAC
address, RW firmware version, release image version, and manufacturer date.
The probed information is then updated to the device data factory section.
Allows for customization of data names via the `data_names` argument.

Test Procedure
--------------
This is an automated test without user interaction.

Dependency
----------
- Device Data API (``cros.factory.test.device_data``).
- Bluetooth utility (``cros.factory.test.utils.bluetooth_utils``).
- Device utility (``cros.factory.device.device_utils``).

Examples
--------
Probe Wi-Fi and Bluetooth MAC address, rw firmware version, release image
version, manufacturer date, update to device data factory section using default
names::

  {
    "pytest_name": "probe_device_info"
  }

Probe Wi-Fi and Bluetooth MAC address, rw firmware version, release image
version, manufacturer date, filter MAC address colon, update to device data
factory section using custom names::

  {
    "pytest_name": "probe_device_info",
    "label": "Probe Device Info",
    "args": {
      "filter_colon": true,
      "data_names": {
        "wifi_mac": "factory.WLANID",
        "bluetooth_mac": "factory.BTMAC",
        "rw_fwid": "factory.BIOS",
        "mfg_date": "factory.manufacture_date",
        "release_image_version": "factory.FSI"
      }
    }
  }

Probe WI-FI MAC address, rw firmware version, release image version,
manufacturer date, and Bluetooth MAC address with specified manufacturer id,
update to device data factory section::

  {
    "pytest_name": "probe_device_info",
    "label": "Probe Device Info",
    "args": {
      "filter_colon": false,
      "manufacturer_id": 29
    }
  }
"""

import datetime
from typing import Dict, Optional

from cros.factory.device import device_utils
from cros.factory.test import device_data
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.test.utils import bluetooth_utils
from cros.factory.utils.arg_utils import Arg


class ProbeDeviceInfoArgs:
  """Arguments for the ProbeDeviceInfoTest."""
  filter_colon: bool
  manufacturer_id: Optional[int]
  uppercase_mac: bool
  data_names: Dict[str, str]


class ProbeDeviceInfo(test_case.TestCase):
  """Probe device information and update to device data."""
  related_components = (test_case.TestCategory.WIFI, )

  ARGS = [
      Arg('filter_colon', bool,
          'If True, the Wi-Fi and Bluetooth MAC will filter out the colon.',
          default=False),
      Arg('manufacturer_id', int,
          'Specified manufacturer id of the bluetooth hci device adapter.',
          default=None),
      Arg('uppercase_mac', bool,
          'If True, the Wi-Fi and Bluetooth MAC are converted to uppercase.',
          default=True),
      Arg(
          'data_names', dict,
          'Custom names to store data in device data. The key should be one of '
          '["wifi_mac", "bluetooth_mac", "rw_fwid", "mfg_date", '
          '"release_image_version"]. For example, to store RW firmware version '
          'in "factory.BIOS", set `"rw_fwid": "factory.BIOS"`.', default={})
  ]
  args: ProbeDeviceInfoArgs

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    if bluetooth_utils.IsFlossBluetoothStack():
      bluetooth_utils.SwitchToBluez(self.dut)

  def runTest(self):
    """Probes device information and updates device data."""
    device_data.UpdateDeviceData({
        self._GetDeviceDataName('wifi_mac'):
            self._GetMacAddress('Wi-Fi'),
        self._GetDeviceDataName('bluetooth_mac'):
            self._GetMacAddress('Bluetooth'),
        self._GetDeviceDataName('rw_fwid'):
            self.dut.CheckOutput(['crossystem', 'fwid']),
        self._GetDeviceDataName('mfg_date'):
            datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3],
        self._GetDeviceDataName('release_image_version'):
            self.dut.info.release_image_version
    })
    session.console.info('Device data has been updated.')

  def _GetDeviceDataName(self, data_type: str) -> str:
    """Gets the device data name for a specific data type.
    Args:
        data_type: The type of data to retrieve the name for.
            Should be one of ["wifi_mac", "bluetooth_mac", "rw_fwid",
            "mfg_date", "release_image_version"].
    Returns:
        str: The device data name, either custom or default.
    """
    return self.args.data_names.get(data_type, f'factory.{data_type}')

  def _GetMacAddress(self, mac_type: str) -> str:
    """Gets and formats the MAC address.
    Args:
        mac_type: The type of MAC address ('Wi-Fi' or 'Bluetooth').
    Returns:
        The formatted MAC address string.
    """
    if mac_type == 'Wi-Fi':
      mac_address = self.dut.info.wlan0_mac
    elif mac_type == 'Bluetooth':
      mac_address = bluetooth_utils.BtMgmt(self.args.manufacturer_id).GetMac()
    else:
      raise ValueError(f'Unsupported MAC type: {mac_type}')

    if mac_address is None:
      self.FailTask(f'Test failed due to missing {mac_type} MAC address.')

    if self.args.filter_colon:
      mac_address = mac_address.replace(':', '')
    if self.args.uppercase_mac:
      mac_address = mac_address.upper()
    return mac_address
