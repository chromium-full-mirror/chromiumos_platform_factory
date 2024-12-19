# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import os

from cros.factory.probe.lib import cached_probe_function
from cros.factory.test.utils import fpmcu_utils
from cros.factory.utils import sys_interface


_FPC_VENDOR_ID = '20435046'


class FingerprintFunction(cached_probe_function.CachedProbeFunction):
  """Probe the fingerprint information."""

  def GetCategoryFromArgs(self):
    return None

  @classmethod
  def ProbeAllDevices(cls):
    if not os.path.exists('/dev/cros_fp'):
      return None

    _fpmcu = fpmcu_utils.FpmcuDevice(sys_interface.SystemInterface())

    sensor_vendor, sensor_model_unmasked = _fpmcu.GetFpSensorInfo()
    fpmcu_name = _fpmcu.GetName()
    if sensor_vendor == _FPC_VENDOR_ID:
      try:
        # The last four bits are associated with the wafer ID, which does not
        # contribute to identification, and therefore they can be masked.
        int_sensor_model_masked = int(sensor_model_unmasked, 16) & ~0xf
      except ValueError:
        logging.error('Probed sensor model is not a hex string: %s',
                      sensor_model_unmasked)
        sensor_model = sensor_model_unmasked
      else:
        sensor_model = f'{int_sensor_model_masked:x}'
    else:
      sensor_model = sensor_model_unmasked

    results = [{
        'sensor_vendor': sensor_vendor,
        'sensor_model': sensor_model,
        'fpmcu_name': fpmcu_name
    }]
    return results
