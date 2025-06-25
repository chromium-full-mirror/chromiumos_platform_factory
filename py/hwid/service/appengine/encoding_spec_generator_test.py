#!/usr/bin/env python3
# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
from typing import Collection, Mapping, Sequence, Set, Tuple
import unittest
from unittest import mock

import hardware_verifier_pb2  # pylint: disable=import-error

from cros.factory.hwid.service.appengine import encoding_spec_generator as encoding_spec_generator_module
from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import database


TESTDATA_DIR = os.path.join(
    os.path.dirname(__file__), 'testdata', 'encoding_spec_generator')
_EncodedComponents = hardware_verifier_pb2.EncodedComponents
_EncodedFields = hardware_verifier_pb2.EncodedFields
_EncodingPattern = hardware_verifier_pb2.EncodingPattern
_BitRange = hardware_verifier_pb2.BitRange
_FirstZeroBit = hardware_verifier_pb2.FirstZeroBit
_EncodingSpec = hardware_verifier_pb2.EncodingSpec


class EncodingSpecGeneratorTest(unittest.TestCase):

  def _GenerateVPRelatedComps(self,
                              db: database.Database) -> Set[Tuple[str, str]]:
    vp_related_comps = set()
    for comp_cls in db.GetComponentClasses():
      components = db.GetComponents(comp_cls)
      for comp_name in components:
        vp_related_comps.add((comp_cls, comp_name))

    return vp_related_comps

  def _UpdateCompStatus(self, db: database.Database, comp_cls: str,
                        status: common.ComponentStatus):
    components = db.GetComponents(comp_cls)
    for comp_name, comp_info in components.items():
      db.raw_components.UpdateComponent(
          comp_cls, comp_name, comp_name, comp_info.values, status,
          comp_info.information, comp_info.bundle_uuids)

  def _UpdateCompGroup(self, db: database.Database, comp_cls: str,
                       comp_name: str, comp_group: str):
    comp_info = db.GetComponents(comp_cls)[comp_name]
    db.raw_components.UpdateComponent(comp_cls, comp_name, comp_name,
                                      comp_info.values, comp_info.status, {
                                          'comp_group': comp_group
                                      }, comp_info.bundle_uuids)

  def testGenerateEncodingPatterns_WithSupportedCamera_ShouldSkipVideo(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_a_db.yaml'), verify_checksum=False)
    waived_comp_categories: Sequence[str] = []
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoding_patterns = encoding_spec_generator.GenerateEncodingPatterns()

    self.assertCountEqual(encoding_patterns, [
        _EncodingPattern(
            image_ids=[0, 1], bit_ranges=[
                _BitRange(category='battery', start=4, end=5),
                _BitRange(category='camera', start=8, end=9),
                _BitRange(category='cellular', start=12, end=14),
                _BitRange(category='touchscreen', start=17, end=18),
            ], first_zero_bits=[
                _FirstZeroBit(category='touchscreen', zero_bit_position=3),
                _FirstZeroBit(category='cellular', zero_bit_position=10),
            ]),
        _EncodingPattern(
            image_ids=[2, 3], bit_ranges=[
                _BitRange(category='battery', start=0, end=1),
                _BitRange(category='camera', start=2, end=3),
                _BitRange(category='touchscreen', start=5, end=6),
            ], first_zero_bits=[
                _FirstZeroBit(category='camera', zero_bit_position=2),
            ]),
    ])

  def testGenerateEncodingPatterns_WithSupportedVideo_ShouldSkipCamera(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_a_db.yaml'), verify_checksum=False)
    self._UpdateCompStatus(db, 'camera', common.ComponentStatus.unsupported)
    self._UpdateCompStatus(db, 'video', common.ComponentStatus.supported)
    waived_comp_categories: Sequence[str] = []
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoding_patterns = encoding_spec_generator.GenerateEncodingPatterns()

    self.assertCountEqual(encoding_patterns, [
        _EncodingPattern(
            image_ids=[0, 1], bit_ranges=[
                _BitRange(category='battery', start=4, end=5),
                _BitRange(category='cellular', start=12, end=14),
                _BitRange(category='touchscreen', start=17, end=18),
            ], first_zero_bits=[
                _FirstZeroBit(category='touchscreen', zero_bit_position=3),
                _FirstZeroBit(category='cellular', zero_bit_position=10),
            ]),
        _EncodingPattern(
            image_ids=[2, 3], bit_ranges=[
                _BitRange(category='battery', start=0, end=1),
                _BitRange(category='camera', start=4, end=4),
                _BitRange(category='touchscreen', start=5, end=6),
            ], first_zero_bits=[
                _FirstZeroBit(category='camera', zero_bit_position=2),
            ]),
    ])

  def testGenerateEncodingPatterns_ShouldSkipWaivedCategories(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_a_db.yaml'), verify_checksum=False)
    waived_comp_categories: Sequence[str] = ['touchscreen']
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoding_patterns = encoding_spec_generator.GenerateEncodingPatterns()

    self.assertCountEqual(encoding_patterns, [
        _EncodingPattern(
            image_ids=[0, 1], bit_ranges=[
                _BitRange(category='battery', start=4, end=5),
                _BitRange(category='camera', start=8, end=9),
                _BitRange(category='cellular', start=12, end=14),
            ], first_zero_bits=[
                _FirstZeroBit(category='cellular', zero_bit_position=10),
            ]),
        _EncodingPattern(
            image_ids=[2, 3], bit_ranges=[
                _BitRange(category='battery', start=0, end=1),
                _BitRange(category='camera', start=2, end=3),
            ], first_zero_bits=[
                _FirstZeroBit(category='camera', zero_bit_position=2),
            ]),
    ])

  def testGenerateEncodedFields_ShouldCheckCompNameAVLCompliance(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_b_db.yaml'), verify_checksum=False)
    waived_comp_categories: Sequence[str] = []
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoded_fields = encoding_spec_generator.GenerateEncodedFields()

    self.assertCountEqual(encoded_fields, [
        _EncodedFields(
            category='camera', encoded_components=[
                _EncodedComponents(
                    index=0,
                    component_names=['camera_4', 'camera_5_5', 'camera_6_6#3']),
                _EncodedComponents(index=1, component_names=['camera_4']),
                _EncodedComponents(index=2, component_names=[]),
            ]),
        _EncodedFields(
            category='touchpad', encoded_components=[
                _EncodedComponents(index=0, component_names=[]),
            ]),
        _EncodedFields(
            category='storage', encoded_components=[
                _EncodedComponents(index=0, component_names=['storage_6_6']),
                _EncodedComponents(index=1,
                                   component_names=['storage_subcomp_7']),
                _EncodedComponents(index=2,
                                   component_names=['storage_subcomp_7#3']),
            ]),
    ])

  def testGenerateEncodedFields_WithSupportedVideo_ShouldSkipCamera(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_b_db.yaml'), verify_checksum=False)
    self._UpdateCompStatus(db, 'camera', common.ComponentStatus.unsupported)
    self._UpdateCompStatus(db, 'video', common.ComponentStatus.supported)
    waived_comp_categories: Sequence[str] = []
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoded_fields = encoding_spec_generator.GenerateEncodedFields()

    self.assertCountEqual(encoded_fields, [
        _EncodedFields(
            category='camera', encoded_components=[
                _EncodedComponents(index=0, component_names=['video_9_9']),
            ]),
        _EncodedFields(
            category='touchpad', encoded_components=[
                _EncodedComponents(index=0, component_names=[]),
            ]),
        _EncodedFields(
            category='storage', encoded_components=[
                _EncodedComponents(index=0, component_names=['storage_6_6']),
                _EncodedComponents(index=1,
                                   component_names=['storage_subcomp_7']),
                _EncodedComponents(index=2,
                                   component_names=['storage_subcomp_7#3']),
            ]),
    ])

  def testGenerateEncodedFields_ShouldSkipWaivedCategories(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_b_db.yaml'), verify_checksum=False)
    waived_comp_categories: Sequence[str] = ['camera']
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoded_fields = encoding_spec_generator.GenerateEncodedFields()

    self.assertCountEqual(encoded_fields, [
        _EncodedFields(
            category='touchpad', encoded_components=[
                _EncodedComponents(index=0, component_names=[]),
            ]),
        _EncodedFields(
            category='storage', encoded_components=[
                _EncodedComponents(index=0, component_names=['storage_6_6']),
                _EncodedComponents(index=1,
                                   component_names=['storage_subcomp_7']),
                _EncodedComponents(index=2,
                                   component_names=['storage_subcomp_7#3']),
            ]),
    ])

  def testGenerateEncodedFields_ShouldCheckVPRelatedComps(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_b_db.yaml'), verify_checksum=False)
    waived_comp_categories: Sequence[str] = []
    vp_related_comps = self._GenerateVPRelatedComps(db)
    vp_related_comps.remove(('camera', 'camera_4'))
    vp_related_comps.remove(('storage', 'storage_subcomp_7'))
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoded_fields = encoding_spec_generator.GenerateEncodedFields()

    self.assertCountEqual(encoded_fields, [
        _EncodedFields(
            category='camera', encoded_components=[
                _EncodedComponents(
                    index=0, component_names=['camera_5_5', 'camera_6_6#3']),
                _EncodedComponents(index=1, component_names=[]),
                _EncodedComponents(index=2, component_names=[]),
            ]),
        _EncodedFields(
            category='touchpad', encoded_components=[
                _EncodedComponents(index=0, component_names=[]),
            ]),
        _EncodedFields(
            category='storage', encoded_components=[
                _EncodedComponents(index=0, component_names=['storage_6_6']),
                _EncodedComponents(index=1, component_names=[]),
                _EncodedComponents(index=2,
                                   component_names=['storage_subcomp_7#3']),
            ]),
    ])

  def testGenerateEncodedFields_WithCompGroup_ShouldUseCompGroup(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_b_db.yaml'), verify_checksum=False)
    self._UpdateCompGroup(db, 'camera', 'camera_4', 'camera_untracked#4')
    self._UpdateCompGroup(db, 'camera', 'XYZ', 'camera_5_5')
    self._UpdateCompGroup(db, 'storage', 'storage_6_6', 'storage_subcomp_7#3')
    waived_comp_categories: Sequence[str] = []
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoded_fields = encoding_spec_generator.GenerateEncodedFields()

    self.assertCountEqual(encoded_fields, [
        _EncodedFields(
            category='camera', encoded_components=[
                _EncodedComponents(
                    index=0, component_names=['camera_5_5', 'camera_6_6#3']),
                _EncodedComponents(index=1, component_names=[]),
                _EncodedComponents(index=2, component_names=['camera_5_5']),
            ]),
        _EncodedFields(
            category='touchpad', encoded_components=[
                _EncodedComponents(index=0, component_names=[]),
            ]),
        _EncodedFields(
            category='storage', encoded_components=[
                _EncodedComponents(index=0,
                                   component_names=['storage_subcomp_7#3']),
                _EncodedComponents(index=1,
                                   component_names=['storage_subcomp_7']),
                _EncodedComponents(index=2,
                                   component_names=['storage_subcomp_7#3']),
            ]),
    ])

  def testGenerateEncodedFields_WithCompGroup_ShouldUsePrimaryIdentifiers(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_b_db.yaml'), verify_checksum=False)
    waived_comp_categories: Sequence[str] = []
    vp_related_comps = self._GenerateVPRelatedComps(db)
    primary_identifiers: Mapping[Tuple[str, str], str] = {
        ('camera', 'camera_4'): 'camera_5_5',
        ('storage', 'storage_subcomp_7#3'): 'storage_6_6',
    }
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories, vp_related_comps, primary_identifiers))

    encoded_fields = encoding_spec_generator.GenerateEncodedFields()

    self.assertCountEqual(encoded_fields, [
        _EncodedFields(
            category='camera', encoded_components=[
                _EncodedComponents(
                    index=0, component_names=[
                        'camera_5_5', 'camera_5_5', 'camera_6_6#3'
                    ]),
                _EncodedComponents(index=1, component_names=['camera_5_5']),
                _EncodedComponents(index=2, component_names=[]),
            ]),
        _EncodedFields(
            category='touchpad', encoded_components=[
                _EncodedComponents(index=0, component_names=[]),
            ]),
        _EncodedFields(
            category='storage', encoded_components=[
                _EncodedComponents(index=0, component_names=['storage_6_6']),
                _EncodedComponents(index=1,
                                   component_names=['storage_subcomp_7']),
                _EncodedComponents(index=2, component_names=['storage_6_6']),
            ]),
    ])

  @mock.patch.object(encoding_spec_generator_module.EncodingSpecGenerator,
                     'GenerateEncodingPatterns')
  @mock.patch.object(encoding_spec_generator_module.EncodingSpecGenerator,
                     'GenerateEncodedFields')
  def testGenerateEncodedFields(self, mock_generate_encoded_fields,
                                mock_generate_encoding_patterns):
    mock_db = mock.create_autospec(database.Database, instance=True)
    waived_comp_categories: Sequence[str] = ['battery']
    vp_related_comps: Collection[Tuple[str, str]] = set()
    primary_identifiers: Mapping[Tuple[str, str], str] = {}
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            mock_db, waived_comp_categories, vp_related_comps,
            primary_identifiers))
    encoded_fields = [
        _EncodedFields(
            category='camera', encoded_components=[
                _EncodedComponents(index=0, component_names=[]),
            ]),
    ]
    encoding_patterns = [
        _EncodingPattern(
            image_ids=[0], bit_ranges=[
                _BitRange(category='camera', start=0, end=0),
            ], first_zero_bits=[
                _FirstZeroBit(category='camera', zero_bit_position=0),
            ]),
    ]
    mock_generate_encoded_fields.return_value = encoded_fields
    mock_generate_encoding_patterns.return_value = encoding_patterns

    encoding_spec = encoding_spec_generator.GenerateEncodingSpec()

    self.assertEqual(
        encoding_spec,
        _EncodingSpec(encoding_patterns=encoding_patterns,
                      encoded_fields=encoded_fields,
                      waived_categories=waived_comp_categories))


if __name__ == '__main__':
  unittest.main()
