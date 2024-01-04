# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Holds field name mappings from AVL to HWID."""

from typing import Callable, Optional, Sequence

from cros.factory.hwid.service.appengine.data.converter import converter
from cros.factory.hwid.service.appengine.data.converter import converter_types
from cros.factory.probe_info_service.app_engine.probe_tools import utils as probe_info_utils


# Shorter identifiers.
_ConvertedValueSpec = converter.ConvertedValueSpec


class _BatteryAVLAttrs(converter.AVLAttrs):
  MANUFACTURER = 'manufacturer'
  MODEL_NAME = 'model_name'


def MakeStrPrefixMatchFactory(
    length: int) -> Callable[..., converter_types.FormattedStrType]:
  return converter_types.FormattedStrType.CreateInstanceFactory(
      formatter_self=lambda x: x[:length].ljust(length),
      formatter_other=lambda x: x.ljust(length))


class _PrefixRestrictedRegexStrFormatter(converter_types.IStrFormatter):

  def __init__(self, length: int):
    super().__init__()
    self._length = length

  def __call__(self, value: converter_types.FormattedRegexStrType) -> str:
    pattern_arr = probe_info_utils.ToRestrictedPatternArray(value)
    space_count = self._length - len(pattern_arr)

    return ''.join(pattern_arr[:self._length]) + ' ' * space_count


def MakeStrRestrictedRegexMatchFactory(
    length: Optional[int] = None
) -> Callable[..., converter_types.FormattedRegexStrType]:
  if length is None:
    return converter_types.FormattedRegexStrType.CreateInstanceFactory()

  return converter_types.FormattedRegexStrType.CreateInstanceFactory(
      formatter_self=_PrefixRestrictedRegexStrFormatter(length),
      formatter_other=lambda x: x.ljust(length))


_BATTERY_CONVERTERS: Sequence[converter.FieldNameConverter] = (
    converter.FieldNameConverter.FromFieldMap(
        'full_length_match', {
            _BatteryAVLAttrs.MANUFACTURER:
                _ConvertedValueSpec('manufacturer'),
            _BatteryAVLAttrs.MODEL_NAME:
                _ConvertedValueSpec('model_name',
                                    MakeStrRestrictedRegexMatchFactory()),
        }),
    converter.FieldNameConverter.FromFieldMap(
        'prefix_match_length_11', {
            _BatteryAVLAttrs.MANUFACTURER:
                _ConvertedValueSpec('manufacturer',
                                    MakeStrPrefixMatchFactory(11)),
            _BatteryAVLAttrs.MODEL_NAME:
                _ConvertedValueSpec('model_name',
                                    MakeStrRestrictedRegexMatchFactory(11)),
        }),
    converter.FieldNameConverter.FromFieldMap(
        'prefix_match_length_7', {
            _BatteryAVLAttrs.MANUFACTURER:
                _ConvertedValueSpec('manufacturer',
                                    MakeStrPrefixMatchFactory(7)),
            _BatteryAVLAttrs.MODEL_NAME:
                _ConvertedValueSpec('model_name',
                                    MakeStrRestrictedRegexMatchFactory(7)),
        }),
)


def GetConverterCollection():
  collection = converter.ConverterCollection('battery')
  for conv in _BATTERY_CONVERTERS:
    collection.AddConverter(conv)
  return collection
