# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Methods to generate the encoding spec from the HWID database."""

from __future__ import annotations

from typing import Collection, Dict, Sequence

import hardware_verifier_pb2  # pylint: disable=import-error
import runtime_probe_pb2  # pylint: disable=import-error

from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import database


_ProbeRequestSupportCategory = runtime_probe_pb2.ProbeRequest.SupportCategory


class EncodingSpecGenerator:
  """Generator of the encoding spec for a specific HWID DB."""

  _FIELD_CATEGORY_MAP = {
      'battery_field': _ProbeRequestSupportCategory.battery,
      'camera_field': _ProbeRequestSupportCategory.camera,
      'cellular_field': _ProbeRequestSupportCategory.cellular,
      'display_panel_field': _ProbeRequestSupportCategory.display_panel,
      'ethernet_field': _ProbeRequestSupportCategory.ethernet,
      'storage_field': _ProbeRequestSupportCategory.storage,
      'stylus_field': _ProbeRequestSupportCategory.stylus,
      'touchpad_field': _ProbeRequestSupportCategory.touchpad,
      'touchscreen_field': _ProbeRequestSupportCategory.touchscreen,
      'video_field': _ProbeRequestSupportCategory.camera,
      'wireless_field': _ProbeRequestSupportCategory.wireless,
  }

  def __init__(
      self,
      db: database.Database,
      waived_comp_categories: Collection[_ProbeRequestSupportCategory],
      skip_fields: Collection[str],
  ):
    self._db = db
    self._waived_comp_categories = waived_comp_categories
    self._skip_fields = skip_fields

  @classmethod
  def Create(cls, db: database.Database,
             waived_comp_categories: Sequence[str]) -> EncodingSpecGenerator:
    """Creates an encoding spec generator for a specific HWID DB.

    Args:
      db: The HWID DB used to build the encoding spec generator.
      waived_comp_categories: The component categories to be waived in the
          encoding specs. In general, this should come from the verification
          payload generator config.
    """
    # Some HWID DBs contain both camera_field and video_field, but only one of
    # them is used, and the other is unexpectedly added to the DB.
    # Use component status to determine which one needs to be skipped.
    skip_fields = set()
    cameras = db.GetComponents('camera')
    if any(camera.status == common.ComponentStatus.supported
           for camera in cameras.values()):
      skip_fields.add('video_field')
    else:
      skip_fields.add('camera_field')

    return cls(
        db,
        set(
            getattr(_ProbeRequestSupportCategory, category)
            for category in waived_comp_categories), skip_fields)

  def _ShouldSkipField(self, field_name: str) -> bool:
    """Checks if an encoded field should be skipped in encoding specs.

    We should skip the encoded field if any of the following is true:
    1. The field is unexpectedly added to the HWID DB.
    2. The category of the field is not Runtime-Probe-supported.
    3. The category of the field is waived.

    Args:
      field_name: The encoded field name. Should be "{CATEGORY}_field".

    Returns:
      A bool value indicating whether the field should be skipped or not.
    """
    category = self._FIELD_CATEGORY_MAP.get(field_name)
    return (category is None or field_name in self._skip_fields or
            category in self._waived_comp_categories)

  def _GenerateEncodingPattern(
      self, pattern_id: int) -> hardware_verifier_pb2.EncodingPattern:
    """Generates the EncodingPattern message for a specific pattern in DB.

    Args:
      pattern_id: The ID of the pattern used to generate the message.
    """
    bit_ranges = []
    category_first_zero_bit: Dict[_ProbeRequestSupportCategory, int] = {}
    pattern_datum = self._db.GetPattern(pattern_idx=pattern_id)
    start_idx = 0
    for field in pattern_datum.fields:
      if not self._ShouldSkipField(field.name):
        category = self._FIELD_CATEGORY_MAP[field.name]
        if field.bit_length > 0:
          bit_ranges.append(
              hardware_verifier_pb2.BitRange(
                  category=category, start=start_idx,
                  end=start_idx + field.bit_length - 1))
        else:
          category_first_zero_bit.setdefault(category, start_idx)
      start_idx += field.bit_length

    first_zero_bits = [
        hardware_verifier_pb2.FirstZeroBit(category=category,
                                           zero_bit_position=position)
        for category, position in category_first_zero_bit.items()
    ]
    return hardware_verifier_pb2.EncodingPattern(
        image_ids=self._db.GetImageIdsByPatternId(pattern_id),
        bit_ranges=bit_ranges, first_zero_bits=first_zero_bits)

  def GenerateEncodingPatterns(
      self) -> Sequence[hardware_verifier_pb2.EncodingPattern]:
    """Generates all EncodingPattern messages for the DB."""
    return [
        self._GenerateEncodingPattern(pattern_id)
        for pattern_id in range(self._db.GetPatternCount())
    ]
