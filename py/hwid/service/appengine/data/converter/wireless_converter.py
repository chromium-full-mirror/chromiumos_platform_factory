# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

import enum
from typing import Sequence

from cros.factory.hwid.service.appengine.data.converter import converter
from cros.factory.hwid.service.appengine.data.converter import converter_types

# Shorter identifiers.
_ConvertedValueSpec = converter.ConvertedValueSpec


class _WirelessAVLAttrs(converter.AVLAttrs):
  JOINED_PROBE_ATTRIBUTE = 'wifi_probe_attributes'


class _WirelessAttrIndex(enum.IntEnum):
  VENDOR = 0
  DEVICE = 1
  SUBSYSTEM_DEVICE = 2


class _ExtractWirelessAttributeFactory:
  _ATTR_SEPARATOR = ', '

  def __init__(self, idx: _WirelessAttrIndex, with_subsystem: bool):
    self._idx = idx
    self._with_subsystem = with_subsystem

  def __call__(self, val: str) -> converter_types.StrValueType:
    sp = val.split(self._ATTR_SEPARATOR)
    if len(sp) <= self._idx:
      raise ValueError(f'{val!r} does not contain {self._idx.name!r} attr')
    if (len(sp) > _WirelessAttrIndex.SUBSYSTEM_DEVICE) != self._with_subsystem:
      raise ValueError(f'Joined attribute must '
                       f'{"" if self._with_subsystem else "not "}'
                       f'contain {_WirelessAttrIndex.SUBSYSTEM_DEVICE.name!r} '
                       f'attribute, got {val!r}.')
    return converter_types.StrValueType(sp[self._idx])


_WIRELESS_CONVERTERS: Sequence[converter.FieldNameConverter] = (
    converter.FieldNameConverter.FromFieldMap(
        'match_with_subsystem', {
            _WirelessAVLAttrs.JOINED_PROBE_ATTRIBUTE: [
                _ConvertedValueSpec(
                    'vendor',
                    _ExtractWirelessAttributeFactory(_WirelessAttrIndex.VENDOR,
                                                     with_subsystem=True)),
                _ConvertedValueSpec(
                    'device',
                    _ExtractWirelessAttributeFactory(_WirelessAttrIndex.DEVICE,
                                                     with_subsystem=True)),
                _ConvertedValueSpec(
                    'subsystem_device',
                    _ExtractWirelessAttributeFactory(
                        _WirelessAttrIndex.SUBSYSTEM_DEVICE,
                        with_subsystem=True)),
            ],
        }),
    converter.FieldNameConverter.FromFieldMap(
        'match_without_subsystem', {
            _WirelessAVLAttrs.JOINED_PROBE_ATTRIBUTE: [
                _ConvertedValueSpec(
                    'vendor',
                    _ExtractWirelessAttributeFactory(_WirelessAttrIndex.VENDOR,
                                                     with_subsystem=False)),
                _ConvertedValueSpec(
                    'device',
                    _ExtractWirelessAttributeFactory(_WirelessAttrIndex.DEVICE,
                                                     with_subsystem=False)),
            ],
        }),
)


def GetConverterCollection():
  collection = converter.ConverterCollection('wireless')
  for conv in _WIRELESS_CONVERTERS:
    collection.AddConverter(conv)
  return collection
