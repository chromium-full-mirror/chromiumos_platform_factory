# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
from typing import Mapping, Sequence, Tuple, Union
import unittest

from cros.factory.hwid.service.appengine.data.converter import converter_utils
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3.avl import builder as avl_builder
from cros.factory.hwid.v3.avl.converter import common as avl_common
from cros.factory.hwid.v3 import builder as v3_builder
from cros.factory.hwid.v3 import contents_analyzer
from cros.factory.hwid.v3 import database
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers
from cros.factory.probe_info_service.app_engine import stubby_pb2  # pylint: disable=no-name-in-module
from cros.factory.utils import type_utils


_PVAlignmentStatus = contents_analyzer.ProbeValueAlignmentStatus


def _ProbeInfoFromMapping(
    mapping: Mapping[str, Union[str, int, Sequence[Union[str, int]]]]):
  probe_parameters = []
  for name, value_or_values in mapping.items():
    values = type_utils.MakeList(value_or_values)
    for value in values:
      probe_parameters.append(
          stubby_pb2.ProbeParameter(
              name=name, string_value=value if isinstance(value, str) else None,
              int_value=value if isinstance(value, int) else None))
  return stubby_pb2.ProbeInfo(probe_parameters=probe_parameters)


def _HWIDDBExternalResourceFromProbeInfos(
    probe_info_mapping: Mapping[Tuple[int, int], stubby_pb2.ProbeInfo]
) -> hwid_api_messages_pb2.HwidDbExternalResource:
  return hwid_api_messages_pb2.HwidDbExternalResource(component_probe_infos=[
      stubby_pb2.ComponentProbeInfo(
          component_identity=stubby_pb2.ComponentIdentity(
              readable_label=f'label_{cid}_{i}',
              component_id=cid,
              qual_id=qid,
          ), probe_info=probe_info)
      for i, ((cid, qid), probe_info) in enumerate(probe_info_mapping.items())
  ])


class TestConverter(avl_builder.IProbeInfoConverter):
  IDENTIFIER = 'converter1'
  RUNTIME_PROBE_KEY_MAPPING = {
      'avl_attr_name1': 'converted_key1',
      'avl_attr_name2': 'converted_key2'
  }

  def Build(
      self, probe_info: v3_rule.AVLProbeInfo
  ) -> avl_builder.IProbeInfoConverterBuildResult:
    return avl_common.JoinFieldConverters((
        avl_common.GetFieldConverter(probe_info, 'avl_attr_name1',
                                     runtime_probe_matchers.StringEqualMatcher,
                                     self.RUNTIME_PROBE_KEY_MAPPING),
        avl_common.GetFieldConverter(probe_info, 'avl_attr_name2',
                                     runtime_probe_matchers.StringEqualMatcher,
                                     self.RUNTIME_PROBE_KEY_MAPPING),
    ))


class ConverterManagerTest(unittest.TestCase):

  def setUp(self):
    builder = avl_builder.Builder()
    builder.AddConverterSets(avl_builder.ConverterSet('', [TestConverter()]))
    self.converter_manager = converter_utils.ConverterManager(
        builder, ['comp_cls'])

  def testLinkAVL_TryAllComponents(self):
    # Arrange.
    cid = 123
    comp_name1 = f'comp_cls_{cid}#1'
    comp_name2 = f'comp_cls_{cid}#2'

    with v3_builder.DatabaseBuilder.FromEmpty('CHROMEBOOK', 'PROTO') as builder:
      builder.AddComponent('comp_cls', comp_name1, {
          'converted_key1': 'value1',
          'converted_key2': 'value2',
      }, 'supported')
      builder.AddComponent('comp_cls', comp_name2, {
          'converted_key1': 'value1',
          'converted_key2': 'value-not-2',
      }, 'unsupported')
    db_with_components_only = builder.Build().DumpDataWithoutChecksum()
    avl_resource = _HWIDDBExternalResourceFromProbeInfos({
        (cid, 0):
            _ProbeInfoFromMapping({
                'avl_attr_name1': 'value1',
                'avl_attr_name2': 'value2',
            })
    })

    # Act.
    avl_converter = self.converter_manager.GetAVLConverter(
        avl_resource, 'CHROMEBOOK', None)
    avl_linked_db_content = avl_converter.LinkAVL(db_with_components_only)

    # Assert.
    avl_linked_db = database.Database.LoadData(avl_linked_db_content)
    self.assertEqual(
        v3_rule.AVLProbeValue(
            identifier='converter1',
            probe_value_matched=True,
            probe_info=v3_rule.AVLProbeInfo(
                '',
                collections.OrderedDict([
                    ('avl_attr_name1', ['value1']),
                    ('avl_attr_name2', ['value2']),
                ])),
            probe_info_matched=True,
            probe_info_override=None,
            probe_info_override_matched=False,
            values=collections.OrderedDict([
                ('converted_key1', 'value1'),
                ('converted_key2', 'value2'),
            ]),
        ),
        avl_linked_db.GetComponents('comp_cls')[comp_name1].values)
    self.assertEqual(
        v3_rule.AVLProbeValue(
            identifier='converter1',
            probe_value_matched=False,
            probe_info=v3_rule.AVLProbeInfo(
                '',
                collections.OrderedDict([
                    ('avl_attr_name1', ['value1']),
                    ('avl_attr_name2', ['value2']),
                ])),
            probe_info_matched=False,
            probe_info_override=None,
            probe_info_override_matched=False,
            values=collections.OrderedDict([
                ('converted_key1', 'value1'),
                ('converted_key2', 'value-not-2'),
            ]),
        ),
        avl_linked_db.GetComponents('comp_cls')[comp_name2].values)

  def testLinkAVL_LookupProbeInfoByCIDQID(self):
    # Arrange.
    with v3_builder.DatabaseBuilder.FromEmpty('CHROMEBOOK', 'PROTO') as builder:
      builder.AddComponent('comp_cls', 'comp_cls_123_1', {
          'converted_key1': 'value1',
          'converted_key2': 'value2',
      }, 'supported')
      builder.AddComponent('comp_cls', 'comp_cls_123_2', {
          'converted_key1': 'value1',
          'converted_key2': 'another-value2',
      }, 'unsupported')
    db_with_components_only = builder.Build().DumpDataWithoutChecksum()
    avl_resource = _HWIDDBExternalResourceFromProbeInfos({
        (123, 1):
            _ProbeInfoFromMapping({
                'avl_attr_name1': 'value1',
                'avl_attr_name2': 'value2',
            }),
        (123, 2):
            _ProbeInfoFromMapping({
                'avl_attr_name1': 'value1',
                'avl_attr_name2': 'another-value2',
            }),
    })

    # Act.
    avl_converter = self.converter_manager.GetAVLConverter(
        avl_resource, 'CHROMEBOOK', None)
    avl_linked_db_content = avl_converter.LinkAVL(db_with_components_only)

    # Assert.
    avl_linked_db = database.Database.LoadData(avl_linked_db_content)
    self.assertEqual(
        v3_rule.AVLProbeValue(
            identifier='converter1',
            probe_value_matched=True,
            probe_info=v3_rule.AVLProbeInfo(
                '',
                collections.OrderedDict([
                    ('avl_attr_name1', ['value1']),
                    ('avl_attr_name2', ['value2']),
                ])),
            probe_info_matched=True,
            probe_info_override=None,
            probe_info_override_matched=False,
            values=collections.OrderedDict([
                ('converted_key1', 'value1'),
                ('converted_key2', 'value2'),
            ]),
        ),
        avl_linked_db.GetComponents('comp_cls')['comp_cls_123_1'].values)
    self.assertEqual(
        v3_rule.AVLProbeValue(
            identifier='converter1',
            probe_value_matched=True,
            probe_info=v3_rule.AVLProbeInfo(
                '',
                collections.OrderedDict([
                    ('avl_attr_name1', ['value1']),
                    ('avl_attr_name2', ['another-value2']),
                ])),
            probe_info_matched=True,
            probe_info_override=None,
            probe_info_override_matched=False,
            values=collections.OrderedDict([
                ('converted_key1', 'value1'),
                ('converted_key2', 'another-value2'),
            ]),
        ),
        avl_linked_db.GetComponents('comp_cls')['comp_cls_123_2'].values)

  def testLinkAVL_ProbeInfoOverridePreserved(self):
    # Arrange.
    with v3_builder.DatabaseBuilder.FromEmpty('CHROMEBOOK', 'PROTO') as builder:
      value = v3_rule.AVLProbeValue(
          identifier='converter1',
          probe_value_matched=True,
          probe_info=None,
          probe_info_matched=False,
          probe_info_override=v3_rule.AVLProbeInfo(
              'identifier',
              collections.OrderedDict([
                  ('avl_attr_name1', ['override_value1']),
                  ('avl_attr_name2', ['value2']),
              ])),
          probe_info_override_matched=True,
          values=collections.OrderedDict([
              ('converted_key1', 'value1'),
              ('converted_key2', 'value2'),
          ]),
      )
      builder.AddComponent('comp_cls', 'comp_cls_123_1', value, 'supported')
    db_with_components_only = builder.Build().DumpDataWithoutChecksum(
        internal=True)
    avl_resource = _HWIDDBExternalResourceFromProbeInfos({
        (123, 1):
            _ProbeInfoFromMapping({
                'avl_attr_name1': 'value1',
                'avl_attr_name2': 'value2',
            }),
    })

    # Act.
    avl_converter = self.converter_manager.GetAVLConverter(
        avl_resource, 'CHROMEBOOK', None)
    avl_linked_db_content = avl_converter.LinkAVL(db_with_components_only)

    # Assert.
    avl_linked_db = database.Database.LoadData(avl_linked_db_content)
    self.assertEqual(
        v3_rule.AVLProbeValue(
            identifier='converter1',
            probe_value_matched=True,
            probe_info=v3_rule.AVLProbeInfo(
                '',
                collections.OrderedDict([
                    ('avl_attr_name1', ['value1']),
                    ('avl_attr_name2', ['value2']),
                ])),
            probe_info_matched=True,
            probe_info_override=v3_rule.AVLProbeInfo(
                'identifier',
                collections.OrderedDict([
                    ('avl_attr_name1', ['override_value1']),
                    ('avl_attr_name2', ['value2']),
                ])),
            probe_info_override_matched=False,
            values=collections.OrderedDict([
                ('converted_key1', 'value1'),
                ('converted_key2', 'value2'),
            ]),
        ),
        avl_linked_db.GetComponents('comp_cls')['comp_cls_123_1'].values)

  def testGetAVLSuggestion(self):
    # Arrange.
    avl_resource = _HWIDDBExternalResourceFromProbeInfos({
        (1, 0):
            _ProbeInfoFromMapping({
                'avl_attr_name1': 'value1',
                'avl_attr_name2': 'value2',
            }),
        (2, 0):
            _ProbeInfoFromMapping({
                'avl_attr_name1': 'value3',
                'avl_attr_name2': 'value4',
            })
    })

    # Act.
    avl_converter = self.converter_manager.GetAVLConverter(
        avl_resource, 'CHROMEBOOK', None)
    suggestion = avl_converter.GetAVLSuggestion('comp_cls', 'comp_cls_1', {
        'converted_key1': 'value3',
        'converted_key2': 'value4',
    })

    # Assert.
    self.assertEqual(
        suggestion,
        hwid_api_messages_pb2.ChangeUnit.AVLSuggestion(
            probe_info_suggestions=[
                stubby_pb2.ProbeParameterSuggestion(
                    hint="Expected AVL attribute 'avl_attr_name1'='value1', "
                    "but got 'value3'.", key='avl_attr_name1', value='value3'),
                stubby_pb2.ProbeParameterSuggestion(
                    hint="Expected AVL attribute 'avl_attr_name2'='value2', "
                    "but got 'value4'.", key='avl_attr_name2', value='value4'),
            ], avl_key_suggestions=[hwid_api_messages_pb2.AvlInfo(cid=2)]))

  def testGetAVLSuggestion_NoSuggestion(self):
    # Arrange.
    avl_resource = _HWIDDBExternalResourceFromProbeInfos({
        (1, 0):
            _ProbeInfoFromMapping({
                'avl_attr_name1': 'value1',
                'avl_attr_name2': 'value2',
            }),
    })

    # Act.
    avl_converter = self.converter_manager.GetAVLConverter(
        avl_resource, 'CHROMEBOOK', None)
    suggestion = avl_converter.GetAVLSuggestion('comp_cls', 'not_comp_cls', {
        'converted_key1': 'value3',
        'converted_key2': 'value4',
    })

    # Assert.
    self.assertIsNone(suggestion)


if __name__ == '__main__':
  unittest.main()
