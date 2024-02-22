# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

from typing import Sequence, Union

from cros.factory.hwid.service.appengine.data.converter import converter
from cros.factory.hwid.service.appengine.data.converter import converter_types


_ConvertedValueSpec = converter.ConvertedValueSpec


class DRAMAVLAttrs(converter.AVLAttrs):
  PART = 'part'


class _SpacelessFormatter(converter_types.IStrFormatter):

  def __call__(self, value: Union[str,
                                  converter_types.FormattedStrType]) -> str:
    return value.replace(' ', '')


_DRAM_CONVERTERS: Sequence[converter.FieldNameConverter] = [
    converter.FieldNameConverter.FromFieldMap(
        'full_length_match', {
            DRAMAVLAttrs.PART:
                _ConvertedValueSpec(
                    'part',
                    converter_types.FormattedStrType.CreateInstanceFactory(
                        formatter_self=_SpacelessFormatter(),
                        formatter_other=_SpacelessFormatter(),
                    ),
                ),
        }),
]


def GetConverterCollection():
  collection = converter.ConverterCollection('dram')
  for conv in _DRAM_CONVERTERS:
    collection.AddConverter(conv)
  return collection
