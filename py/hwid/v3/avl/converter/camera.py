# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

from typing import ClassVar, Iterable, Mapping

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl.converter import common
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import converters as runtime_probe_converters
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class _USBCamera(builder.IProbeInfoConverter):
  RUNTIME_PROBE_KEY_MAPPING: ClassVar[Mapping[str, str]]

  def Build(self, probe_info: v3_rule.AVLProbeInfo):
    keys = ['usb_vendor_id', 'usb_product_id']
    if self.COMPONENT_STATUS != builder.AVLComponentStatus.UNQUALIFIED:
      keys.append('usb_bcd_device')
    return common.JoinFieldConverters(
        common.GetFieldConverter(
            probe_info, key, runtime_probe_matchers.HexEqualMatcher,
            self.RUNTIME_PROBE_KEY_MAPPING) for key in keys)


class USBCameraWithUSBPrefix(_USBCamera):
  IDENTIFIER = 'USBCameraWithUSBPrefix'
  RUNTIME_PROBE_KEY_MAPPING = {}


class USBCameraNoUSBPrefix(_USBCamera):
  IDENTIFIER = 'USBCameraNoUSBPrefix'
  RUNTIME_PROBE_KEY_MAPPING = {
      'usb_bcd_device': 'bcdDevice',
      'usb_product_id': 'idProduct',
      'usb_vendor_id': 'idVendor',
  }
  # crrev/c/4041981. Until SKYRIM.
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(15384)])


class USBCameraWithUSBPrefixUnqualified(USBCameraWithUSBPrefix):
  IDENTIFIER = 'USBCameraWithUSBPrefixUnqualified'
  COMPONENT_STATUS = builder.AVLComponentStatus.UNQUALIFIED


class USBCameraNoUSBPrefixUnqualified(USBCameraNoUSBPrefix):
  IDENTIFIER = 'USBCameraNoUSBPrefixUnqualified'
  COMPONENT_STATUS = builder.AVLComponentStatus.UNQUALIFIED


_MIPI_PID_HEX_CONVERTER = runtime_probe_converters.HexConverter(
    prefix=False, padding_size=4)


def _GetMIPIFieldConverter(
    probe_info: v3_rule.AVLProbeInfo, vid_key: str, pid_key: str,
    runtime_probe_key: str) -> builder.IProbeInfoConverterBuildResult:
  vid_values = probe_info.params.get(vid_key)
  pid_values = probe_info.params.get(pid_key)
  if vid_values is None or pid_values is None:
    return None
  if len(vid_values) != 1 or len(pid_values) != 1:
    builder.LogBuilderError(
        'MIPI camera must have only 1 vid and 1 pid per field per model. '
        f'But got {vid_values!r} {pid_values!r}')
    return None
  pid = _MIPI_PID_HEX_CONVERTER.Parse(pid_values[0])
  if pid is None:
    builder.LogBuilderError(f'MIPI camera pid {pid_values[0]!r} parse failed')
    return None
  value = vid_values[0] + _MIPI_PID_HEX_CONVERTER.Format(pid)
  return (
      runtime_probe_matchers.StringEqualMatcher(runtime_probe_key, value),
      # TODO(wyuang): implement MIPI camera suggester
      common.NopSuggester(),
  )


class MIPICameraWithMIPIPrefix(builder.IProbeInfoConverter):
  IDENTIFIER = 'MIPICameraWithMIPIPrefix'

  def Build(self, probe_info: v3_rule.AVLProbeInfo):
    return common.JoinFieldConverters((
        _GetMIPIFieldConverter(probe_info, 'module_vid', 'module_pid',
                               'mipi_module_id'),
        _GetMIPIFieldConverter(probe_info, 'sensor_vid', 'sensor_pid',
                               'mipi_sensor_id'),
    ))


class MIPICameraNoMIPIPrefix(builder.IProbeInfoConverter):
  IDENTIFIER = 'MIPICameraNoMIPIPrefix'
  # crrev/c/4041981. Until REX.
  LAST_SUPPORT_VERSIONS = builder.BranchesOSVersions([builder.OSVersion(15708)])

  def Build(self, probe_info: v3_rule.AVLProbeInfo):
    return common.JoinFieldConverters((
        _GetMIPIFieldConverter(probe_info, 'module_vid', 'module_pid',
                               'module_id'),
        _GetMIPIFieldConverter(probe_info, 'sensor_vid', 'sensor_pid',
                               'sensor_id'),
    ))


def GetConverterSets() -> Iterable[builder.ConverterSet]:
  return (
      builder.ConverterSet('camera.usb_camera', [
          USBCameraWithUSBPrefix(),
          USBCameraNoUSBPrefix(),
          USBCameraWithUSBPrefixUnqualified(),
          USBCameraNoUSBPrefixUnqualified(),
      ]),
      builder.ConverterSet('camera.mipi_camera', [
          MIPICameraWithMIPIPrefix(),
          MIPICameraNoMIPIPrefix(),
      ]),
  )
