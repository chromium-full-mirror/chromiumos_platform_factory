# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Methods to generate the encoding spec from the HWID database."""

from __future__ import annotations

from typing import Collection, Dict, Mapping, Optional, Sequence, Tuple

import hardware_verifier_pb2  # pylint: disable=import-error
import runtime_probe_pb2  # pylint: disable=import-error

from cros.factory.hwid.v3 import database
from cros.factory.hwid.v3 import name_pattern_adapter


_ProbeRequestSupportCategory = runtime_probe_pb2.ProbeRequest.SupportCategory


class _AVLComplianceAcceptor(name_pattern_adapter.NameInfoAcceptor[bool]):
  """An acceptor to provide the AVL compliance."""

  def AcceptRegularComp(self, cid: int, qid: Optional[int]) -> bool:
    """See base class."""
    del cid, qid
    return True

  def AcceptSubcomp(self, cid: int) -> bool:
    """See base class."""
    del cid
    return True

  def AcceptUntracked(self) -> bool:
    """See base class."""
    return False

  def AcceptLegacy(self, raw_comp_name: str) -> bool:
    """See base class."""
    del raw_comp_name
    return False


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
      vpg_waived_categories: Collection[_ProbeRequestSupportCategory],
      vp_related_comps: Collection[Tuple[str, str]],
      primary_identifiers: Mapping[Tuple[str, str], str],
      skip_fields: Collection[str],
      name_patterns: Mapping[str, name_pattern_adapter.NamePattern],
  ):
    self._db = db
    self._vpg_waived_categories = vpg_waived_categories
    self._vp_related_comps = vp_related_comps
    self._primary_identifiers = primary_identifiers
    self._skip_fields = skip_fields
    self._name_patterns = name_patterns
    self._avl_compliance_acceptor = _AVLComplianceAcceptor()

  @classmethod
  def Create(
      cls, db: database.Database, vpg_waived_categories: Sequence[str],
      vp_related_comps: Collection[Tuple[str, str]],
      primary_identifiers: Mapping[Tuple[str, str],
                                   str]) -> EncodingSpecGenerator:
    """Creates an encoding spec generator for a specific HWID DB.

    Args:
      db: The HWID DB used to build the encoding spec generator.
      vpg_waived_categories: The component categories to be waived in the
          verification payload generator. In general, this should come from the
          verification payload generator config.
      vp_related_comps: (component category, component name) of all components
          that can be used to generate valid probe statements.
    """
    np_adapter = name_pattern_adapter.NamePatternAdapter()
    name_patterns = {
        comp_cls: np_adapter.GetNamePattern(comp_cls)
        for comp_cls in db.GetComponentClasses()
    }

    skip_fields = set()
    if db.GetCameraComponentClass() == 'camera':
      skip_fields.add('video_field')
    else:
      skip_fields.add('camera_field')

    return cls(
        db,
        set(
            getattr(_ProbeRequestSupportCategory, category)
            for category in vpg_waived_categories), vp_related_comps,
        primary_identifiers, skip_fields, name_patterns)

  def _GetFieldCategoryIfNotSkipped(
      self, field_name: str) -> _ProbeRequestSupportCategory | None:
    """Gets the category if the field should not be skipped in encoding spec.

    We should skip the encoded field if any of the following is true:
    1. The field is unexpectedly added to the HWID DB.
    2. The category of the field is not Runtime-Probe-supported.
    3. The category of the field is waived in the verification payload
        generator.

    Args:
      field_name: The encoded field name. Should be "{CATEGORY}_field".

    Returns:
      The category if it should not be skipped, otherwise None.
    """
    category = self._FIELD_CATEGORY_MAP.get(field_name)
    if (category is None or field_name in self._skip_fields or
        category in self._vpg_waived_categories):
      return None
    return category

  def _ShouldSkipComponent(self, comp_cls: str, comp_name: str) -> bool:
    """Checks if a component should be skipped in encoding specs.

    We should skip the component if any of the following is true:
    1. The component name does not follow AVL name pattern (i.e. not AVL
        compliant). It should at least contain a CID.
    2. The component can't be used to generate valid probe statements.

    Args:
      comp_cls: The class (category) of the component.
      comp_name: The name of the component.
    """
    comp_name_info = self._name_patterns[comp_cls].Matches(comp_name)
    avl_compliant = comp_name_info.Provide(self._avl_compliance_acceptor)
    return not avl_compliant or (comp_cls,
                                 comp_name) not in self._vp_related_comps

  def _GenerateEncodingPattern(
      self, pattern_id: int,
      encoding_spec_categories: Collection[_ProbeRequestSupportCategory]
  ) -> hardware_verifier_pb2.EncodingPattern:
    """Generates the EncodingPattern message for a specific pattern in DB.

    Args:
      pattern_id: The ID of the pattern used to generate the message.
      encoding_spec_categories: The valid categories in the encoding spec.
    """
    bit_ranges = []
    category_first_zero_bit: Dict[_ProbeRequestSupportCategory, int] = {}
    pattern_datum = self._db.GetPattern(pattern_idx=pattern_id)
    start_idx = 0
    for field in pattern_datum.fields:
      category = self._GetFieldCategoryIfNotSkipped(field.name)
      if category is not None and category in encoding_spec_categories:
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
      self, encoded_fields: Sequence[hardware_verifier_pb2.EncodedFields]
  ) -> Sequence[hardware_verifier_pb2.EncodingPattern]:
    """Generates all EncodingPattern messages for the DB."""
    encoding_spec_categories = {
        encoded_field.category
        for encoded_field in encoded_fields
    }
    return [
        self._GenerateEncodingPattern(pattern_id, encoding_spec_categories)
        for pattern_id in range(self._db.GetPatternCount())
    ]

  def _GenerateEncodedComponents(
      self, encoded_field_name: str
  ) -> Sequence[hardware_verifier_pb2.EncodedComponents]:
    """Generates the EncodedComponents message for a specific encoded field.

    Given an encoded field, generates all the encoded components of that field
    along with their indexes.

    Args:
      encoded_field_name: The name of the encoded field used to generate the
          message.
    """
    encoded_components = []
    has_valid_comp = False
    for index, components in self._db.GetEncodedField(
        encoded_field_name).items():
      comp_cls, comp_names_encoded = next(iter(components.items()))
      comp_infos = self._db.GetComponents(comp_cls)
      component_names = []
      for comp_name in comp_names_encoded:
        info = comp_infos[comp_name].information
        comp_name = self._primary_identifiers.get((comp_cls, comp_name),
                                                  comp_name)
        comp_name = info and info.get('comp_group') or comp_name

        if self._ShouldSkipComponent(comp_cls, comp_name):
          continue

        component_names.append(comp_name)

      if component_names:
        has_valid_comp = True

      encoded_components.append(
          hardware_verifier_pb2.EncodedComponents(
              index=index, component_names=component_names))

    if not has_valid_comp:
      return []

    return encoded_components

  def GenerateEncodedFieldsAndWaivedCategories(
      self
  ) -> tuple[Sequence[hardware_verifier_pb2.EncodedFields],
             Collection[_ProbeRequestSupportCategory]]:
    """Generates EncodedFields messages for all categories in the DB."""
    encoded_fields = []
    waived_categories = set(self._vpg_waived_categories)
    for field in self._db.encoded_fields:
      category = self._GetFieldCategoryIfNotSkipped(field)
      if category is None:
        continue

      encoded_components = self._GenerateEncodedComponents(field)
      if not encoded_components:
        waived_categories.add(category)
        continue

      encoded_fields.append(
          hardware_verifier_pb2.EncodedFields(
              category=category, encoded_components=encoded_components))

    return encoded_fields, waived_categories

  def GenerateEncodingSpec(self) -> hardware_verifier_pb2.EncodingSpec:
    encoded_fields, waived_categories = (
        self.GenerateEncodedFieldsAndWaivedCategories())
    encoding_patterns = self.GenerateEncodingPatterns(encoded_fields)
    return hardware_verifier_pb2.EncodingSpec(
        encoding_patterns=encoding_patterns, encoded_fields=encoded_fields,
        waived_categories=waived_categories)
