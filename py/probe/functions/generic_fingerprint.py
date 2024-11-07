# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os

from cros.factory.probe.lib import cached_probe_function
from cros.factory.test.utils import fpmcu_utils
from cros.factory.utils import sys_interface


# TODO(b/377616175): Remove the following vars from the main factory branch,
# once https://crrev.com/c/6000978 has landed in production buccaneer FW.
_ELAN_VENDOR_ID = '4e414c45'
"""The correct FOURCC version-id for ELAN.

It spells out "ELAN" in reverse order (little-endian int).
"""
_ELAN_VENDOR_ID_BAD = '4f3'
"""This is the incorrect vendor-id shipped with the initial MP buccaneer FW.

This version lives in the RW part of firmware and will be updated, post launch
of these devices.
"""

class FingerprintFunction(cached_probe_function.CachedProbeFunction):
  """Probe the fingerprint information."""

  def GetCategoryFromArgs(self):
    return None

  @classmethod
  def ProbeAllDevices(cls):
    if not os.path.exists('/dev/cros_fp'):
      return None

    _fpmcu = fpmcu_utils.FpmcuDevice(sys_interface.SystemInterface())

    sensor_vendor, sensor_model = _fpmcu.GetFpSensorInfo()
    fpmcu_name = _fpmcu.GetName()

    # TODO(b/377616175): Remove this workaround from the main factory branch,
    # once https://crrev.com/c/6000978 has landed in production buccaneer FW.
    if sensor_vendor == _ELAN_VENDOR_ID_BAD:
      sensor_vendor = _ELAN_VENDOR_ID

    results = [{
        'sensor_vendor': sensor_vendor,
        'sensor_model': sensor_model,
        'fpmcu_name': fpmcu_name
    }]
    return results
