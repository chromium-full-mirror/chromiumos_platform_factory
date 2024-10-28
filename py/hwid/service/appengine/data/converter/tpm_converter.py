# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds TPM field name mappings from AVL to HWID."""

from typing import Sequence

from cros.factory.hwid.service.appengine.data.converter import converter


_ConvertedValueSpec = converter.ConvertedValueSpec


class TPMAVLAttrs(converter.AVLAttrs):
  SPEC_LEVEL = 'spec_level'
  VENDOR_SPECIFIC = 'vendor_specific'
  MANUFACTURER = 'manufacturer'
  GSC_DEVICE = 'gsc_device'


_TPM_CONVERTERS: Sequence[converter.FieldNameConverter] = [
    converter.FieldNameConverter.FromFieldMap(
        'full_length_match', {
            TPMAVLAttrs.SPEC_LEVEL:
                _ConvertedValueSpec('spec_level'),
            TPMAVLAttrs.VENDOR_SPECIFIC:
                _ConvertedValueSpec('vendor_specific'),
            TPMAVLAttrs.MANUFACTURER:
                _ConvertedValueSpec(
                    'manufacturer',
                    converter.MakeHexDecodedStrValueFactory(
                        source_has_prefix=True)),
            TPMAVLAttrs.GSC_DEVICE:
                _ConvertedValueSpec('gsc_device'),
        }),
]


def GetConverterCollection():
  collection = converter.ConverterCollection('tpm')
  for conv in _TPM_CONVERTERS:
    collection.AddConverter(conv)
  return collection
