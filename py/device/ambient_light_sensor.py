# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


import logging
import os
import time
from typing import List

from cros.factory.device import device_types
from cros.factory.device import sensor_utils


class AmbientLightSensorException(Exception):
  pass


class AmbientLightSensorController(sensor_utils.BasicSensorController):

  def __init__(self, dut, name, location):
    """Constructor.

    According to
    go/cros-ec-sensor-sysfs-docs-legacy#heading=h.xcok6d92lq03 or
    https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-bus-iio
    the unit of _raw data is lux.

    We can get raw data from one of below sysfs:
    -  /sys/bus/iio/devices/iio:deviceX/in_illuminance_input
    -  /sys/bus/iio/devices/iio:deviceX/in_illuminance_raw
    -  /sys/bus/iio/devices/iio:deviceX/in_illuminance0_input
    -  /sys/bus/iio/devices/iio:deviceX/in_illuminance0_raw

    Args:
      dut: The DUT instance.
      name: The name attribute of sensor.
      location: The location attribute of sensor.
    """
    possible_signal_names = ('in_illuminance', 'in_illuminance0')
    errors = []
    for signal_name in possible_signal_names:
      try:
        super().__init__(dut, name, location, signal_names=[signal_name])
      except Exception as err:
        errors.append(err)
      else:
        break
    else:
      errors_str = '\n'.join(map(str, errors))
      raise AmbientLightSensorException(
          f'Does not find any valid signal_name in {possible_signal_names!r}. '
          f'errors: {errors_str}')

    for input_entry_suffix in ('_input', '_raw'):
      input_entry = f'{signal_name}{input_entry_suffix}'
      # yapf: disable
      if self._device.Glob(self._device.path.join(self._iio_path, input_entry)):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        self.input_entry = input_entry
        break
    else:
      raise AmbientLightSensorException('Does not find any input entry.')

  def _SetSysfsValue(self, filename, value, check_call=True, path=None):
    del check_call, path  # Unused.
    try:
      self._device.WriteSpecialFile(
          os.path.join(self._iio_path, filename), value)
    except Exception as e:
      raise AmbientLightSensorException(str(e)) from None

  def _GetSysfsValue(self, filename, path=None):
    del path  # Unused.
    try:
      return self._device.ReadSpecialFile(os.path.join(
          self._iio_path, filename)).strip()
    except Exception as e:
      raise AmbientLightSensorException(str(e)) from None

  def CleanUpCalibrationValues(self):
    """Cleans up calibration values."""
    for signal_name in self.signal_names:
      self.SetCalibrationValue(signal_name, 0.0, 1.0)

  def SetCalibrationValue(self, signal_name, bias, scale):
    """Sets the calibration values to sysfs."""
    if signal_name not in self.signal_names:
      raise KeyError(signal_name)
    try:
      self._SetSysfsValue(f'{signal_name}_calibbias', str(bias))
      self._SetSysfsValue(f'{signal_name}_calibscale', str(scale))
    except Exception as e:
      raise AmbientLightSensorException(str(e)) from None

  def GetLuxValue(self):
    """Reads the LUX raw value from sysfs."""
    try:
      return int(self._GetSysfsValue(self.input_entry))
    except Exception as e:
      logging.exception('Failed to get illuminance value')
      raise AmbientLightSensorException(str(e)) from None

  def GetData(self, capture_count: int = 1, sample_rate: float = 20.0,
              average: bool = True):
    """Returns (averaged) sensor data.

    We cannot use iioservice_simpleclient because it often timeouts and the Tast
    test sensor_iioservice.go also skips light sensors.
    """
    buffers: List[int] = []
    delay = 1.0 / sample_rate
    # Retry at most 2 * capture_count times to prevent infinite loop.
    for unused_try_count in range(2 * capture_count):
      try:
        value = self.GetLuxValue()
      except AmbientLightSensorException:
        time.sleep(delay)
        continue
      buffers.append(value)
      if len(buffers) >= capture_count:
        break
      time.sleep(delay)
    else:
      raise AmbientLightSensorException(
          f'Failed to read channel "{self.input_entry}" from sysfs. '
          f'Expect {capture_count} data, but {len(buffers)} captured.')
    return {
        self.signal_names[0]:
            sum(buffers) // len(buffers) if average else buffers
    }

  def ForceLightInit(self):
    """Froce als to apply the vpd value."""
    try:
      device_name = os.path.basename(self._iio_path)
      self._device.CheckCall('/lib/udev/light-init.sh',
                             # yapf: disable
                             stdin=device_name, stdout='illuminance')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    except Exception as e:
      logging.exception('Failed to invoke light-init.sh (%s, illuminance)',
                        device_name)
      raise AmbientLightSensorException(str(e)) from None


class AmbientLightSensor(device_types.DeviceComponent):
  """AmbientLightSensor (ALS) component module."""

  def GetController(self, name='cros-ec-light', location=None):
    """Gets a controller with specified arguments.

    See AmbientLightSensorController for more information.
    """
    return AmbientLightSensorController(self._device, name, location)
