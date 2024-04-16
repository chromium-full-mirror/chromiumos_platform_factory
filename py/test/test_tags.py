# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import enum
from typing import Optional


CategoryProperties = collections.namedtuple(
    'CategoryProperties', ('subtype', 'avl_name', 'hwid_name'))


@enum.unique
class TestCategory(enum.Enum):
  """Tags for test categories.

  The reference for the name of a component in AVL is defined in
  go/cros-avl-component-types.

  The reference for the name of a component in HWID DB is defined in
  go/cros-runtime-probe-and-hardware-verifier?\
cl=head#name-policy-enforcements-and-runtime-probe-in-factories and
  go/AVL-HWID-component-mapping.
  """

  # avl test category
  ACCELEROMETER = enum.auto()
  AMBIENTLIGHTSENSOR = enum.auto()
  AUDIOCODEC = enum.auto()
  BATTERY = enum.auto()
  BRIDGE_PCIE_EMMC = enum.auto()
  CAMERA = enum.auto()
  CARD_READER = enum.auto()
  CPU = enum.auto()
  DRAM = enum.auto()
  EC = enum.auto()
  EMR_IC = enum.auto()
  ETHERNET = enum.auto()
  FINGERPRINT_SENSOR = enum.auto()
  GPU = enum.auto()
  HPS = enum.auto()
  LCD = enum.auto()
  MIPI_CAMERA = enum.auto()
  SAR_SENSOR = enum.auto()
  SECURE_ELEMENT = enum.auto()
  SMART_SPEAKER_AMPLIFIER = enum.auto()
  SPEAKERAMPLIFIER = enum.auto()
  SPIFLASH = enum.auto()
  STORAGE = enum.auto()
  TOUCHCONTROLLER = enum.auto()
  TPM = enum.auto()
  TRACKPAD = enum.auto()
  USB_INTEGRATED = enum.auto()
  USI_CONTROLLER = enum.auto()
  WIFI = enum.auto()
  WWAN = enum.auto()

  # device feature test category
  FAN = enum.auto()
  HARDWARE_BUTTON = enum.auto()
  HARDWARE_ID = enum.auto()
  KEYBOARD = enum.auto()
  LED = enum.auto()
  PSR = enum.auto()
  THERMAL_SENSOR = enum.auto()

  @property
  def _properties(self):
    return {
        TestCategory.ACCELEROMETER:
            CategoryProperties('avl', 'Accelerometer/IMU', None),
        TestCategory.AMBIENTLIGHTSENSOR:
            CategoryProperties('avl', 'Ambient Light Sensor',
                               'ec_component_als'),
        TestCategory.AUDIOCODEC:
            CategoryProperties('avl', 'Audio Jack Codec', 'audio_codec'),
        TestCategory.BATTERY:
            CategoryProperties('avl', 'Battery', 'battery'),
        TestCategory.BRIDGE_PCIE_EMMC:
            CategoryProperties('avl', 'Storage bridge (PCIE-eMMC)',
                               'storage_bridge'),
        TestCategory.CAMERA:
            CategoryProperties('avl', 'Camera - USB', 'camera'),
        TestCategory.CARD_READER:
            CategoryProperties('avl', 'Card Reader', 'sdcard_reader'),
        TestCategory.CPU:
            CategoryProperties('avl', 'CPU', 'cpu'),
        TestCategory.DRAM:
            CategoryProperties('avl', 'Memory', 'dram'),
        TestCategory.EC:
            CategoryProperties('avl', 'EC', 'ec_flash_chip'),
        TestCategory.EMR_IC:
            CategoryProperties('avl', 'Touch screen controller (EMR Stylus)',
                               'touchscreen'),
        TestCategory.ETHERNET:
            CategoryProperties('avl', 'Ethernet controller', 'ethernet'),
        TestCategory.FINGERPRINT_SENSOR:
            CategoryProperties('avl', 'Fingerprint Sensor', 'fingerprint'),
        TestCategory.HPS:
            CategoryProperties('avl', 'HPS (Human Presence Sensor)', 'hps'),
        TestCategory.LCD:
            CategoryProperties('avl', 'Display Panel', 'display_panel'),
        TestCategory.MIPI_CAMERA:
            CategoryProperties('avl', 'Camera - MIPI', 'camera'),
        TestCategory.SAR_SENSOR:
            CategoryProperties('avl', 'Proximity(SAR) Sensor', None),
        TestCategory.SECURE_ELEMENT:
            CategoryProperties('avl', 'Secure Element', 'tpm'),
        TestCategory.SMART_SPEAKER_AMPLIFIER:
            CategoryProperties('avl', 'Smart Speaker Amplifier', 'audio_codec'),
        TestCategory.SPEAKERAMPLIFIER:
            CategoryProperties('avl', 'Speaker Amplifier', 'audio_codec'),
        TestCategory.SPIFLASH:
            CategoryProperties('avl', 'SPI Flash', 'flash_chip'),
        TestCategory.STORAGE:
            CategoryProperties('avl', 'Storage', 'storage'),
        TestCategory.TOUCHCONTROLLER:
            CategoryProperties('avl', 'Touch screen Controller (non stylus)',
                               'touchscreen'),
        TestCategory.TPM:
            CategoryProperties('avl', 'TPM', 'tpm'),
        TestCategory.TRACKPAD:
            CategoryProperties('avl', 'Touchpad Controller', 'touchpad'),
        TestCategory.USB_INTEGRATED:
            CategoryProperties('avl', 'USB Composite Integrated Component',
                               None),
        TestCategory.USI_CONTROLLER:
            CategoryProperties('avl', 'Touch screen controller (USI Stylus)',
                               'touchscreen'),
        TestCategory.WIFI:
            CategoryProperties('avl', 'Wifi / Bluetooth', 'wireless'),
        TestCategory.WWAN:
            CategoryProperties('avl', 'WWAN', 'cellular'),
        TestCategory.FAN:
            CategoryProperties('device feature', None, None),
        TestCategory.HARDWARE_BUTTON:
            CategoryProperties('device feature', None, None),
        TestCategory.HARDWARE_ID:
            CategoryProperties('device feature', None, None),
        TestCategory.KEYBOARD:
            CategoryProperties('device feature', None, None),
        TestCategory.LED:
            CategoryProperties('device feature', None, None),
        TestCategory.PSR:
            CategoryProperties('device feature', None, None),
        TestCategory.THERMAL_SENSOR:
            CategoryProperties('device feature', None, None),
    }.get(self, CategoryProperties(None, None, None))

  @property
  def subtype(self) -> str:
    return self._properties.subtype

  @property
  def avl_name(self) -> Optional[str]:
    return self._properties.avl_name

  @property
  def hwid_name(self) -> Optional[str]:
    return self._properties.hwid_name
