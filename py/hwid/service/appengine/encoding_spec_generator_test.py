#!/usr/bin/env python3
# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
from typing import Sequence, Set, Tuple
import unittest

import hardware_verifier_pb2  # pylint: disable=import-error

from cros.factory.hwid.service.appengine import encoding_spec_generator as encoding_spec_generator_module
from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import database


TESTDATA_DIR = os.path.join(
    os.path.dirname(__file__), 'testdata', 'encoding_spec_generator')
_EncodingPattern = hardware_verifier_pb2.EncodingPattern
_BitRange = hardware_verifier_pb2.BitRange
_FirstZeroBit = hardware_verifier_pb2.FirstZeroBit


class EncodingSpecGeneratorTest(unittest.TestCase):

  def _UpdateCompStatus(self, db: database.Database, comp_cls: str,
                        status: common.ComponentStatus):
    components = db.GetComponents(comp_cls)
    for comp_name, comp_info in components.items():
      db.raw_components.UpdateComponent(
          comp_cls, comp_name, comp_name, comp_info.values, status,
          comp_info.information, comp_info.bundle_uuids)

  def testGenerateEncodingPatterns_WithSupportedCamera_ShouldSkipVideo(self):
    db = database.Database.LoadFile(
        os.path.join(TESTDATA_DIR, 'model_a_db.yaml'), verify_checksum=False)
    waived_comp_categories: Sequence[str] = []
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories))

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
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories))

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
    encoding_spec_generator = (
        encoding_spec_generator_module.EncodingSpecGenerator.Create(
            db, waived_comp_categories))

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


if __name__ == '__main__':
  unittest.main()
