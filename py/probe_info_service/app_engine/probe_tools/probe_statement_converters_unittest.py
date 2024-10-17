#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import typing
from typing import Sequence
import unittest

from google.protobuf import text_format

from cros.factory.probe.runtime_probe import generic_probe_statement
from cros.factory.probe.runtime_probe import probe_config_types
from cros.factory.probe_info_service.app_engine import probe_info_analytics
from cros.factory.probe_info_service.app_engine.probe_tools import analyzers
from cros.factory.probe_info_service.app_engine.probe_tools import probe_statement_converters as ps_converters


def _CreateStrProbeParam(name: str,
                         value: str) -> probe_info_analytics.ProbeParameter:
  return probe_info_analytics.ProbeParameter(name=name, string_value=value)


def _CreateIntProbeParam(name: str,
                         value: int) -> probe_info_analytics.ProbeParameter:
  return probe_info_analytics.ProbeParameter(name=name, int_value=value)


def _GetConverter(name: str) -> analyzers.IBidirectionalProbeInfoConverter:
  for converter in ps_converters.GetAllConverters():
    if name == converter.GetName():
      return converter

  raise KeyError(f'Converter {name} not found.')


RUNTIME_PROBE_SUPPORTED_CATEGORIES = frozenset([
    ps.probe_category for ps in
    generic_probe_statement.GetAllRuntimeProbeSupportedGenericProbeStatements()
])
# Categories that are supported by Probe Info Service, but are not yet
# available in Runtime Probe
SKIP_CATEGORIES = frozenset(['cpu'])


class ConverterTestCase(unittest.TestCase):

  def assertCanGenerateGenericProbeStatements(
      self,
      probe_statements: Sequence[probe_config_types.ComponentProbeStatement]):
    for ps in probe_statements:
      self.assertIn(ps.category_name,
                    SKIP_CATEGORIES | RUNTIME_PROBE_SUPPORTED_CATEGORIES)


class AudioCodecConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('audio_codec.audio_codec')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "audio_codec.audio_codec"
        description: "Probe audio codec info."
        parameter_definitions {
          name: "name"
          description: "The probed kernel name of audio codec comp."
          value_type: STRING
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertEqual(actual, expect)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('name', 'abcd1234'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'audio_codec', 'comp_name', {
                'eval': {
                    'audio_codec': {}
                },
                'expect': {
                    'name': [True, 'str', '!eq abcd1234']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('name', 'ABCD1234'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'audio_codec', 'comp_name', {
                'eval': {
                    'audio_codec': {}
                },
                'expect': {
                    'name': [True, 'str', '!eq ABCD1234']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'audio_codec': [{
            'name': 'abcd1234'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter('audio_codec',
                                       _CreateStrProbeParam('name', 'abcd1234'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('name', 'abcd1234'),
        _CreateStrProbeParam('name', 'EFGH5678'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('name', 'abcd1234'),
        _CreateStrProbeParam('name', 'EFGH5678'),
    ]
    self.assertCountEqual(actual, expected_probe_params)


class BatteryConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('battery.generic_battery')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "battery.generic_battery"
        description: "Read battery information from sysfs."
        parameter_definitions {
          name: "model_name"
          description: "Model name exposed from the EC or the ACPI interface."
          value_type: STRING
        }
        parameter_definitions {
          name: "manufacturer"
          description: "Manufacturer name exposed from the ACPI interface."
          value_type: STRING
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertEqual(actual, expect)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('manufacturer', 'abcd1234'),
        _CreateStrProbeParam('model_name', 'efgh5678'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'battery', 'comp_name', {
                'eval': {
                    'generic_battery': {}
                },
                'expect': {
                    'manufacturer': [True, 'str', '!eq abcd1234'],
                    'model_name': [True, 'str', '!re efgh5678']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('manufacturer', 'ABCD1234'),
        _CreateStrProbeParam('model_name', 'EFGH5678'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'battery', 'comp_name', {
                'eval': {
                    'generic_battery': {}
                },
                'expect': {
                    'manufacturer': [True, 'str', '!eq ABCD1234'],
                    'model_name': [True, 'str', '!re EFGH5678']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeParam_WithRegexParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('manufacturer', 'abcd[0-9]'),
        _CreateStrProbeParam('model_name', 'efgh[0-9]'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'battery', 'comp_name', {
                'eval': {
                    'generic_battery': {}
                },
                'expect': {
                    'manufacturer': [True, 'str', '!eq abcd[0-9]'],
                    'model_name': [True, 'str', '!re efgh[0-9]']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'battery': [{
            'manufacturer': 'abcd',
            'model_name': '1234'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'battery', _CreateStrProbeParam('manufacturer', 'abcd')),
        analyzers.ParsedProbeParameter(
            'battery', _CreateStrProbeParam('model_name', '1234'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('manufacturer', 'abc123'),
        _CreateStrProbeParam('model_name', 'def456'),
        _CreateStrProbeParam('manufacturer', 'ABC123'),
        _CreateStrProbeParam('model_name', 'DEF456'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('manufacturer', 'abc123'),
        _CreateStrProbeParam('model_name', 'def456'),
        _CreateStrProbeParam('manufacturer', 'ABC123'),
        _CreateStrProbeParam('model_name', 'DEF456'),
    ]

    self.assertCountEqual(actual, expected_probe_params)

  def testGetNormalizedProbeParams_WithRegexParams_CanGetParamsCorrectly(self):
    probe_params = [
        _CreateStrProbeParam('manufacturer', 'abc[0-9]'),
        _CreateStrProbeParam('model_name', 'def[0-9]'),
        _CreateStrProbeParam('manufacturer', 'ABC[0-9]'),
        _CreateStrProbeParam('model_name', 'DEF[0-9]'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('manufacturer', 'abc[0-9]'),
        _CreateStrProbeParam('model_name', 'def[0-9]'),
        _CreateStrProbeParam('manufacturer', 'ABC[0-9]'),
        _CreateStrProbeParam('model_name', 'DEF[0-9]'),
    ]

    self.assertCountEqual(actual, expected_probe_params)


class MipiCameraConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('camera.mipi_camera')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "camera.mipi_camera"
        description: "A method that probes camera devices on MIPI bus."
        parameter_definitions {
          name: "module_vid"
          description: "The camera module vendor ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "module_pid"
          description: "The camera module product ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "sensor_vid"
          description: "The camera sensor vendor ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "sensor_pid"
          description: "The camera sensor product ID."
          value_type: STRING
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('module_vid', 'ab'),
        _CreateStrProbeParam('module_pid', '0x000a'),
        _CreateStrProbeParam('sensor_vid', 'cd'),
        _CreateStrProbeParam('sensor_pid', '0x000b'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'camera', 'comp_name', {
                'eval': {
                    'mipi_camera': {}
                },
                'expect': {
                    'mipi_module_id': [True, 'str', '!eq ab000a'],
                    'mipi_sensor_id': [True, 'str', '!eq cd000b'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('module_vid', 'AB'),
        _CreateStrProbeParam('module_pid', '0x000A'),
        _CreateStrProbeParam('sensor_vid', 'CD'),
        _CreateStrProbeParam('sensor_pid', '0x000B'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'camera', 'comp_name', {
                'eval': {
                    'mipi_camera': {}
                },
                'expect': {
                    'mipi_module_id': [True, 'str', '!eq AB000a'],
                    'mipi_sensor_id': [True, 'str', '!eq CD000b'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'camera': [{
            'mipi_module_id': 'AB0001',
            'mipi_sensor_id': 'CD0002'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter('camera',
                                       _CreateStrProbeParam('module_vid',
                                                            'AB')),
        analyzers.ParsedProbeParameter(
            'camera', _CreateStrProbeParam('module_pid', '0x0001')),
        analyzers.ParsedProbeParameter('camera',
                                       _CreateStrProbeParam('sensor_vid',
                                                            'CD')),
        analyzers.ParsedProbeParameter(
            'camera', _CreateStrProbeParam('sensor_pid', '0x0002'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('module_vid', 'AB'),
        _CreateStrProbeParam('module_pid', '0xaa11'),
        _CreateStrProbeParam('module_vid', 'ab'),
        _CreateStrProbeParam('module_pid', '0xBB22'),
        _CreateStrProbeParam('sensor_vid', 'CD'),
        _CreateStrProbeParam('sensor_pid', '0xcc33'),
        _CreateStrProbeParam('sensor_vid', 'cd'),
        _CreateStrProbeParam('sensor_pid', '0xDD44'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('module_vid', 'AB'),
        _CreateStrProbeParam('module_pid', '0xaa11'),
        _CreateStrProbeParam('module_vid', 'ab'),
        _CreateStrProbeParam('module_pid', '0xbb22'),
        _CreateStrProbeParam('sensor_vid', 'CD'),
        _CreateStrProbeParam('sensor_pid', '0xcc33'),
        _CreateStrProbeParam('sensor_vid', 'cd'),
        _CreateStrProbeParam('sensor_pid', '0xdd44'),
    ]
    self.assertCountEqual(actual, expected_probe_params)


class UsbCameraConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('camera.usb_camera')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "camera.usb_camera"
        description: "A method that probes camera devices on USB bus."
        parameter_definitions {
          name: "usb_vendor_id"
          description: "USB Vendor ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "usb_product_id"
          description: "USB Product ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "usb_bcd_device"
          description: "USB BCD Device Info."
          value_type: STRING
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('usb_vendor_id', '000a'),
        _CreateStrProbeParam('usb_product_id', '000b'),
        _CreateStrProbeParam('usb_bcd_device', '000c'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'camera', 'comp_name', {
                'eval': {
                    'usb_camera': {}
                },
                'expect': {
                    'usb_vendor_id': [True, 'hex', '!eq 0x000A'],
                    'usb_product_id': [True, 'hex', '!eq 0x000B'],
                    'usb_bcd_device': [True, 'hex', '!eq 0x000C']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('usb_vendor_id', '000A'),
        _CreateStrProbeParam('usb_product_id', '000B'),
        _CreateStrProbeParam('usb_bcd_device', '000C'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'camera', 'comp_name', {
                'eval': {
                    'usb_camera': {}
                },
                'expect': {
                    'usb_vendor_id': [True, 'hex', '!eq 0x000A'],
                    'usb_product_id': [True, 'hex', '!eq 0x000B'],
                    'usb_bcd_device': [True, 'hex', '!eq 0x000C']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'camera': [{
            'usb_vendor_id': '0001',
            'usb_product_id': '0002',
            'usb_bcd_device': '0003'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'camera', _CreateStrProbeParam('usb_vendor_id', '0001')),
        analyzers.ParsedProbeParameter(
            'camera', _CreateStrProbeParam('usb_product_id', '0002')),
        analyzers.ParsedProbeParameter(
            'camera', _CreateStrProbeParam('usb_bcd_device', '0003'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('usb_vendor_id', '00aa'),
        _CreateStrProbeParam('usb_vendor_id', '11BB'),
        _CreateStrProbeParam('usb_product_id', '22cc'),
        _CreateStrProbeParam('usb_product_id', '33DD'),
        _CreateStrProbeParam('usb_bcd_device', '44ee'),
        _CreateStrProbeParam('usb_bcd_device', '55FF'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('usb_vendor_id', '00AA'),
        _CreateStrProbeParam('usb_vendor_id', '11BB'),
        _CreateStrProbeParam('usb_product_id', '22CC'),
        _CreateStrProbeParam('usb_product_id', '33DD'),
        _CreateStrProbeParam('usb_bcd_device', '44EE'),
        _CreateStrProbeParam('usb_bcd_device', '55FF'),
    ]
    self.assertCountEqual(actual, expected_probe_params)


class DisplayPanelConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('display_panel.edid')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "display_panel.edid"
        description: "A method that probes devices via edid."
        parameter_definitions {
          name: "product_id"
          description: "The product ID, 16 bits"
          value_type: STRING
        }
        parameter_definitions {
          name: "vendor"
          description: "The vendor code, 3 letters"
          value_type: STRING
        }
        parameter_definitions {
          name: "width"
          description: "The width of display panel."
          value_type: INT
        }
        parameter_definitions {
          name: "height"
          description: "The height of display panel."
          value_type: INT
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('product_id', '000a'),
        _CreateStrProbeParam('vendor', 'ABC'),  # vendor must be upper case.
        _CreateIntProbeParam('width', 100),
        _CreateIntProbeParam('height', 200),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'display_panel', 'comp_name', {
                'eval': {
                    'edid': {}
                },
                'expect': {
                    'product_id': [True, 'hex', '!eq 0x000A'],
                    'vendor': [True, 'str', '!eq ABC']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('product_id', '000A'),
        _CreateStrProbeParam('vendor', 'ABC'),
        _CreateIntProbeParam('width', 100),
        _CreateIntProbeParam('height', 200),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'display_panel', 'comp_name', {
                'eval': {
                    'edid': {}
                },
                'expect': {
                    'product_id': [True, 'hex', '!eq 0x000A'],
                    'vendor': [True, 'str', '!eq ABC']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'display_panel': [{
            'product_id': '000a',
            'vendor': 'ABC'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'display_panel', _CreateStrProbeParam('product_id', '000A')),
        analyzers.ParsedProbeParameter('display_panel',
                                       _CreateStrProbeParam('vendor', 'ABC'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('product_id', '000a'),
        _CreateStrProbeParam('product_id', '000B'),
        _CreateStrProbeParam('vendor', 'ABC'),
        _CreateIntProbeParam('width', 100),
        _CreateIntProbeParam('height', 200),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('product_id', '000A'),
        _CreateStrProbeParam('product_id', '000B'),
        _CreateStrProbeParam('vendor', 'ABC'),
        _CreateIntProbeParam('width', 100),
        _CreateIntProbeParam('height', 200),
    ]
    self.assertCountEqual(actual, expected_probe_params)


class MemoryConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('dram.memory')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "dram.memory"
        description: "Probe memory from DMI."
        parameter_definitions {
          name: "part"
          description: "Part number."
          value_type: STRING
        }
        parameter_definitions {
          name: "extra_part"
          description: "Extra part number."
          value_type: STRING
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [_CreateStrProbeParam('part', 'abcd1234')]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'dram', 'comp_name', {
                'eval': {
                    'memory': {}
                },
                'expect': {
                    'part': [True, 'str', '!eq abcd1234']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [_CreateStrProbeParam('part', 'ABCD1234')]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'dram', 'comp_name', {
                'eval': {
                    'memory': {}
                },
                'expect': {
                    'part': [True, 'str', '!eq ABCD1234']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeParam_MergeExtraPartNumbers(self):
    probe_params = [
        _CreateStrProbeParam('part', 'abcd1234'),
        _CreateStrProbeParam('extra_part', 'extra-abcd1234'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'dram', 'comp_name', {
                'eval': {
                    'memory': {}
                },
                'expect': [{
                    'part': [True, 'str', '!eq abcd1234'],
                },{
                    'part': [True, 'str', '!eq extra-abcd1234'],
                }]
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'dram': [{
            'part': 'ABCD1234'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter('dram',
                                       _CreateStrProbeParam('part',
                                                            'ABCD1234')),
        analyzers.ParsedProbeParameter(
            'dram', _CreateStrProbeParam('extra_part', 'ABCD1234'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('part', 'ABC123'),
        _CreateStrProbeParam('part', 'def456')
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('part', 'ABC123'),
        _CreateStrProbeParam('part', 'def456')
    ]
    self.assertCountEqual(actual, expected_probe_params)

  def testGetNormalizedProbeParams_MergeExtraPartNumbers(self):
    probe_params = [
        _CreateStrProbeParam('part', 'ABC123'),
        _CreateStrProbeParam('part', 'def456'),
        _CreateStrProbeParam('extra_part', 'extra-ABC123'),
        _CreateStrProbeParam('extra_part', 'extra-def456'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('part', 'ABC123'),
        _CreateStrProbeParam('part', 'def456'),
        _CreateStrProbeParam('extra_part', 'extra-ABC123'),
        _CreateStrProbeParam('extra_part', 'extra-def456'),
    ]
    self.assertCountEqual(actual, expected_probe_params)

  def testMatchProbeResult_Pass_MatchPartNumber(self):
    probe_params = [
        _CreateStrProbeParam('part', 'ABC123'),
        _CreateStrProbeParam('part', 'def456'),
        _CreateStrProbeParam('extra_part', 'extra-ABC123'),
        _CreateStrProbeParam('extra_part', 'extra-def456'),
    ]
    probe_result = {
        'dram': [{
            'part': 'def456'
        }],
    }
    parsed_probe_result = self._converter.ParseProbeResult(probe_result)

    actual = self._converter.MatchProbeResult(probe_params, parsed_probe_result)

    expected_match_result = analyzers.ProbeResultMatchResult({})
    self.assertEqual(actual, expected_match_result)

  def testMatchProbeResult_Pass_MatchExtraPartNumber(self):
    probe_params = [
        _CreateStrProbeParam('part', 'ABC123'),
        _CreateStrProbeParam('part', 'def456'),
        _CreateStrProbeParam('extra_part', 'extra-ABC123'),
        _CreateStrProbeParam('extra_part', 'extra-def456'),
    ]
    probe_result = {
        'dram': [{
            'part': 'extra-ABC123'
        }],
    }
    parsed_probe_result = self._converter.ParseProbeResult(probe_result)

    actual = self._converter.MatchProbeResult(probe_params, parsed_probe_result)

    expected_match_result = analyzers.ProbeResultMatchResult({})
    self.assertEqual(actual, expected_match_result)

  def testMatchProbeResult_Fail_ResultShouldContainExtraPartNumbers(self):
    probe_params = [
        _CreateStrProbeParam('part', 'ABC123'),
        _CreateStrProbeParam('part', 'def456'),
        _CreateStrProbeParam('extra_part', 'extra-ABC123'),
        _CreateStrProbeParam('extra_part', 'extra-def456'),
    ]
    probe_result = {
        'dram': [{
            'part': 'XYZ789-1'
        }],
    }
    parsed_probe_result = self._converter.ParseProbeResult(probe_result)

    actual = self._converter.MatchProbeResult(probe_params, parsed_probe_result)

    expected_match_result = analyzers.ProbeResultMatchResult(
        {'part': 'dram', 'extra_part': 'dram'})
    self.assertEqual(actual, expected_match_result)


class MmcStorageConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('storage.mmc_storage')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "storage.mmc_storage"
        description: "Probe function for eMMC storage."
        parameter_definitions {
          name: "mmc_manfid"
          description: "Manufacturer ID (MID) in CID register."
          value_type: STRING
        }
        parameter_definitions {
          name: "mmc_name"
          description: "Product name (PNM) in CID register."
          value_type: STRING
        }
        parameter_definitions {
          name: "mmc_prv"
          description: "Product revision (PRV) in CID register."
          value_type: STRING
        }
        parameter_definitions {
          name: "size_in_gb"
          description: "The storage size in GB."
          value_type: INT
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_name', '0x61626364'),
        _CreateStrProbeParam('mmc_prv', '0x2b'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name', {
                'eval': {
                    'mmc_storage': {}
                },
                'expect': {
                    'mmc_manfid': [True, 'hex', '!eq 0x1A'],
                    'mmc_name': [True, 'str', '!eq abcd'],
                    'mmc_prv': [True, 'hex', '!eq 0x2B']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1A'),
        _CreateStrProbeParam('mmc_name', '0x61626364'),
        _CreateStrProbeParam('mmc_prv', '0x2B'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name', {
                'eval': {
                    'mmc_storage': {}
                },
                'expect': {
                    'mmc_manfid': [True, 'hex', '!eq 0x1A'],
                    'mmc_name': [True, 'str', '!eq abcd'],
                    'mmc_prv': [True, 'hex', '!eq 0x2B']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'storage': [{
            'mmc_manfid': '0x12',
            'mmc_name': 'abcd',
            'mmc_prv': '0x34'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('mmc_manfid', '0x12')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('mmc_name', '0x61626364')),
        analyzers.ParsedProbeParameter('storage',
                                       _CreateStrProbeParam('mmc_prv', '0x34'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_manfid', '0x2B'),
        _CreateStrProbeParam('mmc_name', '0x61626364'),
        _CreateStrProbeParam('mmc_prv', '0x3c'),
        _CreateStrProbeParam('mmc_prv', '0x4D'),
        _CreateIntProbeParam('size_in_gb', 64)
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_manfid', '0x2b'),
        _CreateStrProbeParam('mmc_name', '0x61626364'),
        _CreateStrProbeParam('mmc_prv', '0x3c'),
        _CreateStrProbeParam('mmc_prv', '0x4d'),
        _CreateIntProbeParam('size_in_gb', 64)
    ]
    self.assertCountEqual(actual, expected_probe_params)


class NvmeStorageConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('storage.nvme_storage')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "storage.nvme_storage"
        description: "Probe function for NVMe storage."
        parameter_definitions {
          name: "pci_vendor"
          description: "PCI Vendor ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "pci_device"
          description: "PCI Device ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "pci_class"
          description: "PCI Device Class Indicator."
          value_type: STRING
        }
        parameter_definitions {
          name: "nvme_model"
          description: "NVMe model name."
          value_type: STRING
        }
        parameter_definitions {
          name: "size_in_gb"
          description: "The storage size in GB."
          value_type: INT
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('pci_vendor', '0x000a'),
        _CreateStrProbeParam('pci_device', '0x000b'),
        _CreateStrProbeParam('pci_class', '0x123abc'),
        _CreateStrProbeParam('nvme_model', 'abcde'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name', {
                'eval': {
                    'nvme_storage': {}
                },
                'expect': {
                    'pci_vendor': [True, 'hex', '!eq 0x000A'],
                    'pci_device': [True, 'hex', '!eq 0x000B'],
                    'pci_class': [True, 'hex', '!eq 0x123ABC'],
                    'nvme_model': [True, 'str', '!eq abcde']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('pci_vendor', '0x000A'),
        _CreateStrProbeParam('pci_device', '0x000B'),
        _CreateStrProbeParam('pci_class', '0x123ABC'),
        _CreateStrProbeParam('nvme_model', 'ABCDE'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name', {
                'eval': {
                    'nvme_storage': {}
                },
                'expect': {
                    'pci_vendor': [True, 'hex', '!eq 0x000A'],
                    'pci_device': [True, 'hex', '!eq 0x000B'],
                    'pci_class': [True, 'hex', '!eq 0x123ABC'],
                    'nvme_model': [True, 'str', '!eq ABCDE']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'storage': [{
            'pci_vendor': '0x0001',
            'pci_device': '0x0002',
            'pci_class': '0x123456',
            'nvme_model': 'ABCDE'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('pci_vendor', '0x0001')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('pci_device', '0x0002')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('pci_class', '0x123456')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('nvme_model', 'ABCDE'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('pci_vendor', '0x000a'),
        _CreateStrProbeParam('pci_vendor', '0x000B'),
        _CreateStrProbeParam('pci_device', '0x000c'),
        _CreateStrProbeParam('pci_device', '0x000D'),
        _CreateStrProbeParam('pci_class', '0x123abc'),
        _CreateStrProbeParam('pci_class', '0x456DEF'),
        _CreateStrProbeParam('nvme_model', 'abc'),
        _CreateStrProbeParam('nvme_model', 'DEF'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('pci_vendor', '0x000a'),
        _CreateStrProbeParam('pci_vendor', '0x000b'),
        _CreateStrProbeParam('pci_device', '0x000c'),
        _CreateStrProbeParam('pci_device', '0x000d'),
        _CreateStrProbeParam('pci_class', '0x123abc'),
        _CreateStrProbeParam('pci_class', '0x456def'),
        _CreateStrProbeParam('nvme_model', 'abc'),
        _CreateStrProbeParam('nvme_model', 'DEF'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]
    self.assertCountEqual(actual, expected_probe_params)


class UfsStorageConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('storage.ufs_storage')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "storage.ufs_storage"
        description: "Probe function for UFS storage."
        parameter_definitions {
          name: "ufs_vendor"
          description: "Vendor name."
          value_type: STRING
        }
        parameter_definitions {
          name: "ufs_model"
          description: "Model name."
          value_type: STRING
        }
        parameter_definitions {
          name: "size_in_gb"
          description: "The storage size in GB."
          value_type: INT
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('ufs_vendor', 'abcd'),
        _CreateStrProbeParam('ufs_model', 'wxyz'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name', {
                'eval': {
                    'ufs_storage': {}
                },
                'expect': {
                    'ufs_vendor': [True, 'str', '!eq abcd'],
                    'ufs_model': [True, 'str', '!eq wxyz']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('ufs_vendor', 'ABCD'),
        _CreateStrProbeParam('ufs_model', 'WXYZ'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name', {
                'eval': {
                    'ufs_storage': {}
                },
                'expect': {
                    'ufs_vendor': [True, 'str', '!eq ABCD'],
                    'ufs_model': [True, 'str', '!eq WXYZ']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'storage': [{
            'ufs_vendor': 'abcd',
            'ufs_model': 'wxyz'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('ufs_vendor', 'abcd')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('ufs_model', 'wxyz'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('ufs_vendor', 'abc'),
        _CreateStrProbeParam('ufs_vendor', 'DEF'),
        _CreateStrProbeParam('ufs_model', 'ghi'),
        _CreateStrProbeParam('ufs_model', 'JKL'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('ufs_vendor', 'abc'),
        _CreateStrProbeParam('ufs_vendor', 'DEF'),
        _CreateStrProbeParam('ufs_model', 'ghi'),
        _CreateStrProbeParam('ufs_model', 'JKL'),
        _CreateIntProbeParam('size_in_gb', 64),
    ]
    self.assertCountEqual(actual, expected_probe_params)


class CpuConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('cpu.generic_cpu')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "cpu.generic_cpu"
        description: "A currently non-existent runtime probe function for CPU."
        parameter_definitions {
          name: "identifier"
          description: "Model name on x86, chip-id on ARM."
          value_type: STRING
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [_CreateStrProbeParam('identifier', 'abcd1234')]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'cpu', 'comp_name', {
                'eval': {
                    'generic_cpu': {}
                },
                'expect': {
                    'identifier': [True, 'str', '!eq abcd1234']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [_CreateStrProbeParam('identifier', 'ABCD1234')]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'cpu', 'comp_name', {
                'eval': {
                    'generic_cpu': {}
                },
                'expect': {
                    'identifier': [True, 'str', '!eq ABCD1234']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'cpu': [{
            'identifier': 'ABCD1234'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'cpu', _CreateStrProbeParam('identifier', 'ABCD1234'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('identifier', 'abc123'),
        _CreateStrProbeParam('identifier', 'DEF456')
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('identifier', 'abc123'),
        _CreateStrProbeParam('identifier', 'DEF456')
    ]
    self.assertCountEqual(actual, expected_probe_params)


class TouchscreenModuleConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = ps_converters.BuildTouchscreenModuleConverter()

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "touchscreen_module.generic_input_device_and_edid"
        description:
          "Probe statement converter for touchscreen modules with eDP displays."
        parameter_definitions {
          name: "module_vendor_id"
          description: "Vendor ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "module_product_id"
          description: "Product ID."
          value_type: STRING
        }
        parameter_definitions {
          name: "panel_edid_vendor_code"
          description: "The vendor code, 3 letters"
          value_type: STRING
        }
        parameter_definitions {
          name: "panel_edid_product_id"
          description: "The product ID, 16 bits"
          value_type: STRING
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithMissingParamAllowed_ThenValidationPassed(self):
    probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'AB12'),
        _CreateStrProbeParam('module_product_id', 'CD34'),
        _CreateStrProbeParam('panel_edid_vendor_code', 'ABC'),
        # `panel_edid_product_id` is missing.
    ]

    actual = self._converter.ParseProbeParams(probe_params,
                                              allow_missing_params=True)

    self.assertEqual(actual.probe_info_parsed_result.result_type,
                     probe_info_analytics.ProbeInfoParsedResult.PASSED)

  def testParseProbeParam_WithMissingParamNotAllowed_ThenValidationFailed(self):
    probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'AB12'),
        _CreateStrProbeParam('module_product_id', 'CD34'),
        _CreateStrProbeParam('panel_edid_vendor_code', 'ABC'),
        # `panel_edid_product_id` is missing.
    ]

    actual = self._converter.ParseProbeParams(probe_params,
                                              allow_missing_params=False)

    expected_parsed_result = probe_info_analytics.ProbeInfoParsedResult(
        result_type=(
            probe_info_analytics.ProbeInfoParsedResult.INCOMPATIBLE_ERROR),
        general_error_msg='Missing probe parameters: panel_edid_product_id.')
    self.assertEqual(actual.probe_info_parsed_result, expected_parsed_result)

  def testParseProbeParam_WithSomeParamValueInvalid_ThenValidationFailed(self):
    probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'not a hex string'),
        _CreateStrProbeParam('module_product_id', 'CD34'),
        _CreateStrProbeParam('panel_edid_vendor_code', 'value is too long'),
        _CreateStrProbeParam('panel_edid_product_id', '1234'),
    ]

    actual = self._converter.ParseProbeParams(probe_params,
                                              allow_missing_params=True)

    expected_parsed_result = probe_info_analytics.ProbeInfoParsedResult(
        result_type=(
            probe_info_analytics.ProbeInfoParsedResult.PROBE_PARAMETER_ERROR))
    expected_parsed_result.probe_parameter_errors.add(
        index=0, hint=('format error, should be hex number between 0000 and '
                       'FFFF with leading zero perserved.'))
    expected_parsed_result.probe_parameter_errors.add(
        index=2, hint='Must be a 3-letter all caps string.')
    self.assertEqual(actual.probe_info_parsed_result, expected_parsed_result)

  def testParseProbeParam_WithExtraParam_ThenValidationFailed(self):
    probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'AB12'),
        _CreateStrProbeParam('module_product_id', 'CD34'),
        _CreateStrProbeParam('panel_edid_vendor_code', 'ABC'),
        _CreateStrProbeParam('panel_edid_product_id', '1234'),
        _CreateStrProbeParam('the_unknown_param', 'the_unknown_value'),
    ]

    actual = self._converter.ParseProbeParams(probe_params,
                                              allow_missing_params=True)

    expected_parsed_result = probe_info_analytics.ProbeInfoParsedResult(
        result_type=(
            probe_info_analytics.ProbeInfoParsedResult.INCOMPATIBLE_ERROR),
        general_error_msg='Unknown probe parameters: the_unknown_param.')
    self.assertEqual(actual.probe_info_parsed_result, expected_parsed_result)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'ab12'),
        _CreateStrProbeParam('module_product_id', 'cd34'),
        # vendor must be upper case.
        _CreateStrProbeParam('panel_edid_vendor_code', 'ABC'),
        _CreateStrProbeParam('panel_edid_product_id', 'ef56'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'touchscreen', 'comp_name-touchscreen_controller', {
                'eval': {
                    'input_device': {
                        'device_type': 'touchscreen'
                    }
                },
                'expect': {
                    'vendor': [True, 'hex', '!eq 0xAB12'],
                    'product': [True, 'hex', '!eq 0xCD34']
                }
            }),
        probe_config_types.ComponentProbeStatement(
            'display_panel', 'comp_name-edid_panel', {
                'eval': {
                    'edid': {}
                },
                'expect': {
                    'vendor': [True, 'str', '!eq ABC'],
                    'product_id': [True, 'hex', '!eq 0xEF56']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'AB12'),
        _CreateStrProbeParam('module_product_id', 'CD34'),
        _CreateStrProbeParam('panel_edid_vendor_code', 'ABC'),
        _CreateStrProbeParam('panel_edid_product_id', 'EF56'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'touchscreen', 'comp_name-touchscreen_controller', {
                'eval': {
                    'input_device': {
                        'device_type': 'touchscreen'
                    }
                },
                'expect': {
                    'vendor': [True, 'hex', '!eq 0xAB12'],
                    'product': [True, 'hex', '!eq 0xCD34']
                }
            }),
        probe_config_types.ComponentProbeStatement(
            'display_panel', 'comp_name-edid_panel', {
                'eval': {
                    'edid': {}
                },
                'expect': {
                    'vendor': [True, 'str', '!eq ABC'],
                    'product_id': [True, 'hex', '!eq 0xEF56']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'touchscreen': [{
            'vendor': 'AB12',
            'product': 'CD34'
        }],
        'display_panel': [{
            'vendor': 'ABC',
            'product_id': '1234'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'touchscreen', _CreateStrProbeParam('module_vendor_id', 'AB12')),
        analyzers.ParsedProbeParameter(
            'touchscreen', _CreateStrProbeParam('module_product_id', 'CD34')),
        analyzers.ParsedProbeParameter(
            'display_panel',
            _CreateStrProbeParam('panel_edid_vendor_code', 'ABC')),
        analyzers.ParsedProbeParameter(
            'display_panel',
            _CreateStrProbeParam('panel_edid_product_id', '1234'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'aa11'),
        _CreateStrProbeParam('module_vendor_id', 'BB22'),
        _CreateStrProbeParam('module_product_id', 'cc33'),
        _CreateStrProbeParam('module_product_id', 'DD44'),
        _CreateStrProbeParam('panel_edid_vendor_code', 'ABC'),
        _CreateStrProbeParam('panel_edid_product_id', 'ee55'),
        _CreateStrProbeParam('panel_edid_product_id', 'FF66')
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('module_vendor_id', 'AA11'),
        _CreateStrProbeParam('module_vendor_id', 'BB22'),
        _CreateStrProbeParam('module_product_id', 'CC33'),
        _CreateStrProbeParam('module_product_id', 'DD44'),
        _CreateStrProbeParam('panel_edid_vendor_code', 'ABC'),
        _CreateStrProbeParam('panel_edid_product_id', 'EE55'),
        _CreateStrProbeParam('panel_edid_product_id', 'FF66')
    ]
    self.assertCountEqual(actual, expected_probe_params)


class MMCWithBridgeProbeStatementConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = ps_converters.MMCWithBridgeProbeStatementConverter()

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    converter_description = (
        'The probe statement converter for eMMC + eMMC-PCIe bridge assemblies.')
    nvme_model_param_description = (
        'NVMe model name. (if the bridge component contains a NVMe controller)')
    expect = text_format.Parse(
        f'''
        name: "emmc_pcie_assembly.generic"
        description: "{converter_description}"
        parameter_definitions {{
          name: "mmc_manfid"
          description: "Manufacturer ID (MID) in CID register."
          value_type: STRING
        }}
        parameter_definitions {{
          name: "mmc_name"
          description: "Product name (PNM) in CID register."
          value_type: STRING
        }}
        parameter_definitions {{
          name: "bridge_pcie_vendor"
          description: "PCIe vendor ID"
          value_type: STRING
        }}
        parameter_definitions {{
          name: "bridge_pcie_device"
          description: "PCIe device ID"
          value_type: STRING
        }}
        parameter_definitions {{
          name: "bridge_pcie_class"
          description: "PCIe class code"
          value_type: STRING
        }}
        parameter_definitions {{
          name: "nvme_model"
          description: "{nvme_model_param_description}"
          value_type: STRING
        }}''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateMMCAndMMCHostPS(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_name', '0x656565656565'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xab12'),
        _CreateStrProbeParam('bridge_pcie_device', '0xcd34'),
        _CreateStrProbeParam('bridge_pcie_class', '0xef5678'),
        _CreateStrProbeParam('nvme_model', ''),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')
    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name-storage', {
                'eval': {
                    'mmc_storage': {}
                },
                'expect': {
                    'mmc_manfid': [True, 'hex', '!eq 0x1A'],
                    'mmc_name': [True, 'str', '!eq eeeeee']
                }
            }),
        probe_config_types.ComponentProbeStatement(
            'mmc_host', 'comp_name-bridge', {
                'eval': {
                    'mmc_host': {
                        'is_emmc_attached': True,
                    }
                },
                'expect': {
                    'pci_vendor_id': [True, 'hex', '!eq 0xAB12'],
                    'pci_device_id': [True, 'hex', '!eq 0xCD34'],
                    'pci_class': [True, 'hex', '!eq 0xEF5678'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateMMCAndMMCHostPS(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1A'),
        _CreateStrProbeParam('mmc_name', '0x656565656565'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xAB12'),
        _CreateStrProbeParam('bridge_pcie_device', '0xCD34'),
        _CreateStrProbeParam('bridge_pcie_class', '0xEF5678'),
        _CreateStrProbeParam('nvme_model', ''),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')
    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name-storage', {
                'eval': {
                    'mmc_storage': {}
                },
                'expect': {
                    'mmc_manfid': [True, 'hex', '!eq 0x1A'],
                    'mmc_name': [True, 'str', '!eq eeeeee']
                }
            }),
        probe_config_types.ComponentProbeStatement(
            'mmc_host', 'comp_name-bridge', {
                'eval': {
                    'mmc_host': {
                        'is_emmc_attached': True,
                    }
                },
                'expect': {
                    'pci_vendor_id': [True, 'hex', '!eq 0xAB12'],
                    'pci_device_id': [True, 'hex', '!eq 0xCD34'],
                    'pci_class': [True, 'hex', '!eq 0xEF5678'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithNANVMeModel_CanGenerateMMCAndMMCHostPS(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_name', '0x656565656565'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xab12'),
        _CreateStrProbeParam('bridge_pcie_device', '0xcd34'),
        _CreateStrProbeParam('bridge_pcie_class', '0xef5678'),
        _CreateStrProbeParam('nvme_model', 'N/A'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')
    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name-storage', {
                'eval': {
                    'mmc_storage': {}
                },
                'expect': {
                    'mmc_manfid': [True, 'hex', '!eq 0x1A'],
                    'mmc_name': [True, 'str', '!eq eeeeee']
                }
            }),
        probe_config_types.ComponentProbeStatement(
            'mmc_host', 'comp_name-bridge', {
                'eval': {
                    'mmc_host': {
                        'is_emmc_attached': True,
                    }
                },
                'expect': {
                    'pci_vendor_id': [True, 'hex', '!eq 0xAB12'],
                    'pci_device_id': [True, 'hex', '!eq 0xCD34'],
                    'pci_class': [True, 'hex', '!eq 0xEF5678'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateNVMePS(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_name', '0x656565656565'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xab12'),
        _CreateStrProbeParam('bridge_pcie_device', '0xcd34'),
        _CreateStrProbeParam('bridge_pcie_class', '0xef5678'),
        _CreateStrProbeParam('nvme_model', 'the_model_with_eeeeee'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name-assembly', {
                'eval': {
                    'nvme_storage': {}
                },
                'expect': {
                    'nvme_model': [True, 'str', '!eq the_model_with_eeeeee'],
                    'pci_vendor': [True, 'hex', '!eq 0xAB12'],
                    'pci_device': [True, 'hex', '!eq 0xCD34'],
                    'pci_class': [True, 'hex', '!eq 0xEF5678'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateNVMePS(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1A'),
        _CreateStrProbeParam('mmc_name', '0x656565656565'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xAB12'),
        _CreateStrProbeParam('bridge_pcie_device', '0xCD34'),
        _CreateStrProbeParam('bridge_pcie_class', '0xEF5678'),
        _CreateStrProbeParam('nvme_model', 'the_model_with_eeeeee'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'storage', 'comp_name-assembly', {
                'eval': {
                    'nvme_storage': {}
                },
                'expect': {
                    'nvme_model': [True, 'str', '!eq the_model_with_eeeeee'],
                    'pci_vendor': [True, 'hex', '!eq 0xAB12'],
                    'pci_device': [True, 'hex', '!eq 0xCD34'],
                    'pci_class': [True, 'hex', '!eq 0xEF5678'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateMMCAndMMCHostProbeParameter(self):
    probe_result = {
        'storage': [{
            'mmc_manfid': '0x00001a',
            'mmc_name': 'eeeeee'
        }],
        'mmc_host': [{
            'pci_vendor_id': '0xab12',
            'pci_device_id': '0xcd34',
            'pci_class': '0x010809'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('mmc_manfid', '0x1a')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('mmc_name', '0x656565656565')),
        analyzers.ParsedProbeParameter(
            'mmc_host', _CreateStrProbeParam('bridge_pcie_vendor', '0xab12')),
        analyzers.ParsedProbeParameter(
            'mmc_host', _CreateStrProbeParam('bridge_pcie_device', '0xcd34')),
        analyzers.ParsedProbeParameter(
            'mmc_host', _CreateStrProbeParam('bridge_pcie_class', '0x010809'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testParseProbeResult_CanGenerateNVMeProbeParameter(self):
    probe_result = {
        'storage': [{
            'nvme_model': 'the_model_with_eeeeee',
            'pci_vendor': '0xab12',
            'pci_device': '0xcd34',
            'pci_class': '0x010809'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('bridge_pcie_vendor', '0xab12')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('bridge_pcie_device', '0xcd34')),
        analyzers.ParsedProbeParameter(
            'storage', _CreateStrProbeParam('bridge_pcie_class', '0x010809')),
        analyzers.ParsedProbeParameter(
            'storage',
            _CreateStrProbeParam('nvme_model', 'the_model_with_eeeeee')),
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_manfid', '0x2B'),
        _CreateStrProbeParam('mmc_name', '0x656565656565'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xaa11'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xBB22'),
        _CreateStrProbeParam('bridge_pcie_device', '0xcc33'),
        _CreateStrProbeParam('bridge_pcie_device', '0xDD44'),
        _CreateStrProbeParam('bridge_pcie_class', '0xee5555'),
        _CreateStrProbeParam('bridge_pcie_class', '0xFF6666'),
        _CreateStrProbeParam('nvme_model', 'the_model_with_eeeeee'),
        _CreateStrProbeParam('nvme_model', 'THE_MODEL_WITH_FFFFFF'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('mmc_manfid', '0x1a'),
        _CreateStrProbeParam('mmc_manfid', '0x2b'),
        _CreateStrProbeParam('mmc_name', '0x656565656565'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xaa11'),
        _CreateStrProbeParam('bridge_pcie_vendor', '0xbb22'),
        _CreateStrProbeParam('bridge_pcie_device', '0xcc33'),
        _CreateStrProbeParam('bridge_pcie_device', '0xdd44'),
        _CreateStrProbeParam('bridge_pcie_class', '0xee5555'),
        _CreateStrProbeParam('bridge_pcie_class', '0xff6666'),
        _CreateStrProbeParam('nvme_model', 'the_model_with_eeeeee'),
        _CreateStrProbeParam('nvme_model', 'THE_MODEL_WITH_FFFFFF'),
    ]

    self.assertCountEqual(actual, expected_probe_params)


class PCIeeMMCStorageBridgeProbeStatementConverterTest(unittest.TestCase):

  def setUp(self):
    self._converter = _GetConverter('emmc_pcie_storage_bridge.mmc_host')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "emmc_pcie_storage_bridge.mmc_host"
        description: "The probe function for MMC host components."
        parameter_definitions {
          name: "pci_vendor_id"
          description: "PCIe vendor ID"
          value_type: STRING
        }
        parameter_definitions {
          name: "pci_device_id"
          description: "PCIe device ID"
          value_type: STRING
        }
        parameter_definitions {
          name: "pci_class"
          description: "PCIe class code"
          value_type: STRING
        }
    ''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertCountEqual(actual.parameter_definitions,
                          expect.parameter_definitions)

  def testParseProbeParam_WithLowerCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('pci_vendor_id', '0xab12'),
        _CreateStrProbeParam('pci_device_id', '0xcd34'),
        _CreateStrProbeParam('pci_class', '0x010809'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'mmc_host', 'comp_name', {
                'eval': {
                    'mmc_host': {
                        'is_emmc_attached': True
                    }
                },
                'expect': {
                    'pci_vendor_id': [True, 'hex', '!eq 0xAB12'],
                    'pci_device_id': [True, 'hex', '!eq 0xCD34'],
                    'pci_class': [True, 'hex', '!eq 0x010809'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithUpperCaseParams_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('pci_vendor_id', '0xAB12'),
        _CreateStrProbeParam('pci_device_id', '0xCD34'),
        _CreateStrProbeParam('pci_class', '0x010809'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'mmc_host', 'comp_name', {
                'eval': {
                    'mmc_host': {
                        'is_emmc_attached': True
                    }
                },
                'expect': {
                    'pci_vendor_id': [True, 'hex', '!eq 0xAB12'],
                    'pci_device_id': [True, 'hex', '!eq 0xCD34'],
                    'pci_class': [True, 'hex', '!eq 0x010809'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'mmc_host': [{
            'pci_vendor_id': '0xab12',
            'pci_device_id': '0xcd34',
            'pci_class': '0x010809'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'mmc_host', _CreateStrProbeParam('pci_vendor_id', '0xab12')),
        analyzers.ParsedProbeParameter(
            'mmc_host', _CreateStrProbeParam('pci_device_id', '0xcd34')),
        analyzers.ParsedProbeParameter(
            'mmc_host', _CreateStrProbeParam('pci_class', '0x010809'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateStrProbeParam('pci_vendor_id', '0xaa11'),
        _CreateStrProbeParam('pci_vendor_id', '0xBB22'),
        _CreateStrProbeParam('pci_device_id', '0xcc33'),
        _CreateStrProbeParam('pci_device_id', '0xDD44'),
        _CreateStrProbeParam('pci_class', '0x010809')
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)
    expected_probe_params = [
        _CreateStrProbeParam('pci_vendor_id', '0xaa11'),
        _CreateStrProbeParam('pci_vendor_id', '0xbb22'),
        _CreateStrProbeParam('pci_device_id', '0xcc33'),
        _CreateStrProbeParam('pci_device_id', '0xdd44'),
        _CreateStrProbeParam('pci_class', '0x010809')
    ]

    self.assertCountEqual(actual, expected_probe_params)


class WirelessConverterTest(ConverterTestCase):

  def setUp(self):
    self._pci_converter = _GetConverter('wireless.pci_wireless_network')
    self._sdio_converter = _GetConverter('wireless.sdio_wireless_network')

  def testGenerateDefinition_PCI(self):
    actual = self._pci_converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "wireless.pci_wireless_network"
        description:
          "A method that tries various of way to detect the network component."
        parameter_definitions {
          name: "wifi_probe_attributes"
          description: "Joined probe attributes."
          value_type: STRING
        }
    ''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertEqual(actual, expect)

  def testGenerateDefinition_SDIO(self):
    actual = self._sdio_converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "wireless.sdio_wireless_network"
        description:
          "A method that tries various of way to detect the network component."
        parameter_definitions {
          name: "wifi_probe_attributes"
          description: "Joined probe attributes."
          value_type: STRING
        }
    ''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertEqual(actual, expect)

  def testParseProbeParam_AllAttrsProvided(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x1234, 0x5678, 0x90ab'),
    ]

    actual = self._pci_converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'wireless', 'comp_name', {
                'eval': {
                    'network': {
                        'device_type': 'wifi'
                    }
                },
                'expect': {
                    'pci_vendor_id': [True, 'hex', '!eq 0x1234'],
                    'pci_device_id': [True, 'hex', '!eq 0x5678'],
                    'pci_subsystem': [True, 'hex', '!eq 0x90AB'],
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithoutSubsystem_PCI(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x1234, 0x5678'),
    ]

    actual = self._pci_converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'wireless', 'comp_name', {
                'eval': {
                    'network': {
                        'device_type': 'wifi'
                    }
                },
                'expect': {
                    'pci_vendor_id': [True, 'hex', '!eq 0x1234'],
                    'pci_device_id': [True, 'hex', '!eq 0x5678'],
                },
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeParam_WithoutSubsystem_SDIO(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x1234, 0x5678'),
    ]

    actual = self._sdio_converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'wireless', 'comp_name', {
                'eval': {
                    'network': {
                        'device_type': 'wifi'
                    }
                },
                'expect': {
                    'sdio_vendor_id': [True, 'hex', '!eq 0x1234'],
                    'sdio_device_id': [True, 'hex', '!eq 0x5678'],
                },
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter_PCI(self):
    probe_result = {
        'wireless': [{
            'pci_vendor_id': '0xab12',
            'pci_device_id': '0xcd34',
            'pci_subsystem': '0xef56',
        }]
    }

    actual = self._pci_converter.ParseProbeResult(probe_result)

    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'wireless',
            _CreateStrProbeParam('wifi_probe_attributes',
                                 '0xab12, 0xcd34, 0xef56')),
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testParseProbeResult_CanGenerateProbeParameter_SDIO(self):
    probe_result = {
        'wireless': [{
            'sdio_vendor_id': '0xab12',
            'sdio_device_id': '0xcd34',
        }]
    }

    actual = self._sdio_converter.ParseProbeResult(probe_result)

    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'wireless',
            _CreateStrProbeParam('wifi_probe_attributes', '0xab12, 0xcd34')),
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_PCI(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]

    actual = self._pci_converter.GetNormalizedProbeParams(probe_params)

    expected_probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]
    self.assertCountEqual(actual, expected_probe_params)

  def testGetNormalizedProbeParams_SDIO(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]

    actual = self._sdio_converter.GetNormalizedProbeParams(probe_params)

    expected_probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]
    self.assertCountEqual(actual, expected_probe_params)

  def testMatchProbeResult_PCI_Pass(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]
    probe_result = {
        'wireless': [{
            'pci_vendor_id': '0x11aa',
            'pci_device_id': '0x22bb',
            'pci_subsystem': '0x33cc',
        }],
    }
    parsed_probe_result = self._pci_converter.ParseProbeResult(probe_result)

    actual = self._pci_converter.MatchProbeResult(probe_params,
                                                  parsed_probe_result)

    expected_match_result = analyzers.ProbeResultMatchResult({})
    self.assertEqual(actual, expected_match_result)

  def testMatchProbeResult_PCI_Fail(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]
    probe_result = {
        'wireless': [{
            'pci_vendor_id': '0x11aa',
            'pci_device_id': '0x22bb',
            'pci_subsystem': '0x33cd',
        }],
    }
    parsed_probe_result = self._pci_converter.ParseProbeResult(probe_result)

    actual = self._pci_converter.MatchProbeResult(probe_params,
                                                  parsed_probe_result)

    expected_match_result = analyzers.ProbeResultMatchResult(
        {'wifi_probe_attributes': 'wireless'})
    self.assertEqual(actual, expected_match_result)

  def testMatchProbeResult_SDIO_Pass(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]
    probe_result = {
        'wireless': [{
            'sdio_vendor_id': '0x44dd',
            'sdio_device_id': '0x55ee',
        }],
    }
    parsed_probe_result = self._sdio_converter.ParseProbeResult(probe_result)

    actual = self._sdio_converter.MatchProbeResult(probe_params,
                                                   parsed_probe_result)

    expected_match_result = analyzers.ProbeResultMatchResult({})
    self.assertEqual(actual, expected_match_result)

  def testMatchProbeResult_SDIO_Fail(self):
    probe_params = [
        _CreateStrProbeParam('wifi_probe_attributes', '0x11aa, 0x22bb, 0x33cc'),
        _CreateStrProbeParam('wifi_probe_attributes', '0x44dd, 0x55ee'),
    ]
    probe_result = {
        'wireless': [{
            'sdio_vendor_id': '0x44dd',
            'sdio_device_id': '0x66ff',
        }],
    }
    parsed_probe_result = self._sdio_converter.ParseProbeResult(probe_result)

    actual = self._sdio_converter.MatchProbeResult(probe_params,
                                                   parsed_probe_result)

    expected_match_result = analyzers.ProbeResultMatchResult(
        {'wifi_probe_attributes': 'wireless'})
    self.assertEqual(actual, expected_match_result)


class ECComponentStandaloneComponentConverterTest(ConverterTestCase):

  _COMPONENT_TYPES = ('accel', 'als', 'charger')

  def _GetConverter(
      self, component_type: str) -> analyzers.IBidirectionalProbeInfoConverter:
    converter = _GetConverter(f'ec_component.ec_component_{component_type}')
    return converter

  def testGenerateDefinition(self):
    for component_type in self._COMPONENT_TYPES:
      with self.subTest(component_type=component_type):
        converter = self._GetConverter(component_type)

        actual = converter.GenerateDefinition()

        expect = text_format.Parse(
            f'''
            name: "ec_component.ec_component_{component_type}"
            description: "Probe EC components by manifest."
            parameter_definitions {{
              name: "{component_type}_component_name"
              description: "Name identifier of the component in the manifest."
              value_type: STRING
            }}''', probe_info_analytics.ProbeFunctionDefinition())
        self.assertCountEqual(actual.parameter_definitions,
                              expect.parameter_definitions)

  def testParseProbeParam_CanGenerateProbeStatement(self):
    for component_type in self._COMPONENT_TYPES:
      with self.subTest(component_type=component_type):
        probe_params = [
            _CreateStrProbeParam(f'{component_type}_component_name',
                                 'the_name_in_manifest'),
        ]

        converter = self._GetConverter(component_type)
        actual = converter.ParseProbeParams(
            probe_params, allow_missing_params=False,
            comp_name_for_probe_statement='comp_name')

        expected_probe_statements = [
            probe_config_types.ComponentProbeStatement(
                'ec_component', 'comp_name', {
                    'eval': {
                        'ec_component': {'type': component_type},
                    },
                    'expect': {
                        'component_name': [
                            True,
                            'str',
                            '!eq the_name_in_manifest'
                        ],
                    }
                },
            )
        ]
        self.assertCountEqual(
            typing.cast(Sequence[probe_config_types.ComponentProbeStatement],
                        actual.output),
            expected_probe_statements)
        self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanParseProbeResult(self):
    for component_type in self._COMPONENT_TYPES:
      with self.subTest(component_type=component_type):
        probe_result = {
            'ec_component': [
                {
                    'component_type': component_type,
                    'component_name': 'ABC'
                },
                {
                    'component_type': 'other_type',
                    'component_name': 'DEF'
                },
            ]
        }

        converter = self._GetConverter(component_type)
        actual = converter.ParseProbeResult(probe_result)

        expected_probe_parameters = [
            analyzers.ParsedProbeParameter(
                'ec_component',
                _CreateStrProbeParam(
                    f'{component_type}_component_name', 'ABC')),
        ]
        self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    for component_type in self._COMPONENT_TYPES:
      param_name = f'{component_type}_component_name'
      with self.subTest(component_type=component_type):
        probe_params = [_CreateStrProbeParam(param_name, 'ABC')]

        converter = self._GetConverter(component_type)
        actual = converter.GetNormalizedProbeParams(probe_params)

        expected_probe_params = [_CreateStrProbeParam(param_name, 'ABC')]
        self.assertCountEqual(actual, expected_probe_params)


class ECComponentUSBCConverterTest(ConverterTestCase):
  def setUp(self):
    super().setUp()
    self._converter = _GetConverter('usb_c.ec_components')

  def testParseProbeParam_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateStrProbeParam('bc12_component_name', 'bc12_name'),
        _CreateStrProbeParam('tcpc_component_name', 'tcpc_name'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'ec_component', 'comp_name-bc12', {
                'eval': {
                    'ec_component': {'type': 'bc12'},
                },
                'expect': {
                    'component_name': [True, 'str', '!eq bc12_name'],
                }
            },
        ),
        probe_config_types.ComponentProbeStatement(
            'ec_component', 'comp_name-tcpc', {
                'eval': {
                    'ec_component': {'type': 'tcpc'},
                },
                'expect': {
                    'component_name': [True, 'str', '!eq tcpc_name'],
                }
            },
        ),
    ]
    self.assertCountEqual(
        typing.cast(Sequence[probe_config_types.ComponentProbeStatement],
                    actual.output), expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanParseProbeResult(self):
    probe_result = {
        'ec_component': [
            {
                'component_type': 'ppc',
                'component_name': 'ppc_name'
            },
            {
                'component_type': 'bc12',
                'component_name': 'bc12_name'
            },
        ]
    }

    actual = self._converter.ParseProbeResult(probe_result)

    expected_probe_parameters = [
        analyzers.ParsedProbeParameter(
            'ec_component',
            _CreateStrProbeParam('ppc_component_name', 'ppc_name')),
        analyzers.ParsedProbeParameter(
            'ec_component',
            _CreateStrProbeParam('bc12_component_name', 'bc12_name')),
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testParseProbeResult_CanMatchParsedProbeResultsWithUnrelatedComponents(
      self):
    probe_params = [
        _CreateStrProbeParam('bc12_component_name', 'bc12_name'),
        _CreateStrProbeParam('tcpc_component_name', 'tcpc_name'),
    ]
    probe_result = {
        'ec_component': [
            {
                'component_type': 'charger',
                'component_name': 'charger_probed_name',
            },
            {
                'component_type': 'bc12',
                'component_name': 'bc12_probed_name',
            },
            {
                'component_type': 'ppc',
                'component_name': 'ppc_probed_name',
            },
        ]
    }
    parsed_probe_result = self._converter.ParseProbeResult(probe_result)

    actual = self._converter.MatchProbeResult(probe_params, parsed_probe_result)

    expected = analyzers.ProbeResultMatchResult(
        {'bc12_component_name': 'ec_component', 'tcpc_component_name': None})
    self.assertEqual(actual, expected)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [_CreateStrProbeParam('tcpc_component_name', 'ABC')]

    actual = self._converter.GetNormalizedProbeParams(probe_params)

    expected_probe_params = [_CreateStrProbeParam('tcpc_component_name', 'ABC')]
    self.assertCountEqual(actual, expected_probe_params)


class TouchComponentConverterTest(ConverterTestCase):

  _COMPONENT_TYPES = ('touchscreen', 'touchpad', 'stylus')

  def _GetConverter(
      self, component_type: str) -> analyzers.IBidirectionalProbeInfoConverter:
    converter = _GetConverter(f'{component_type}.input_device')
    return converter

  def testGenerateDefinition(self):
    for component_type in self._COMPONENT_TYPES:
      with self.subTest(component_type=component_type):
        converter = self._GetConverter(component_type)

        actual = converter.GenerateDefinition()

        expect = text_format.Parse(
            f'''
            name: "{component_type}.input_device"
            description: "Probe input devices from procfs."
            parameter_definitions {{
              name: "product"
              description: "Product ID."
              value_type: STRING
            }}
            parameter_definitions {{
              name: "vendor"
              description: "Vendor ID."
              value_type: STRING
            }}
            ''', probe_info_analytics.ProbeFunctionDefinition())
        self.assertCountEqual(actual.parameter_definitions,
                              expect.parameter_definitions)

  def testParseProbeParam_CanGenerateProbeStatement(self):
    for component_type in self._COMPONENT_TYPES:
      with self.subTest(component_type=component_type):
        probe_params = [
            _CreateStrProbeParam('vendor', '01AB'),
            _CreateStrProbeParam('product', '23CD'),
        ]

        converter = self._GetConverter(component_type)
        actual = converter.ParseProbeParams(
            probe_params, allow_missing_params=False,
            comp_name_for_probe_statement='comp_name')

        expected_probe_statements = [
            probe_config_types.ComponentProbeStatement(
                component_type, 'comp_name', {
                    'eval': {
                        'input_device': {'device_type': component_type},
                    },
                    'expect': {
                        'vendor': [
                            True,
                            'hex',
                            '!eq 0x01AB'
                        ],
                        'product': [
                            True,
                            'hex',
                            '!eq 0x23CD'
                        ],
                    }
                },
            )
        ]
        self.assertCountEqual(
            typing.cast(Sequence[probe_config_types.ComponentProbeStatement],
                        actual.output),
            expected_probe_statements)
        self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanParseProbeResult(self):
    for component_type in self._COMPONENT_TYPES:
      with self.subTest(component_type=component_type):
        probe_result = {
            component_type: [
                {
                    'vendor': '01ab',
                    'product': '0x2345cdef',
                },
            ]
        }

        converter = self._GetConverter(component_type)
        actual = converter.ParseProbeResult(probe_result)

        expected_probe_parameters = [
            analyzers.ParsedProbeParameter(
                component_type, _CreateStrProbeParam('vendor', '01AB')),
            analyzers.ParsedProbeParameter(
                component_type, _CreateStrProbeParam('product', '2345CDEF')),
        ]
        self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    for component_type in self._COMPONENT_TYPES:
      with self.subTest(component_type=component_type):
        probe_params = [
            _CreateStrProbeParam('vendor', '01aB'),
            _CreateStrProbeParam('product', '23cD'),
        ]

        converter = self._GetConverter(component_type)
        actual = converter.GetNormalizedProbeParams(probe_params)

        expected_probe_params = [
            _CreateStrProbeParam('vendor', '01AB'),
            _CreateStrProbeParam('product', '23CD'),
        ]
        self.assertCountEqual(actual, expected_probe_params)


class TPMConverterTest(ConverterTestCase):

  def setUp(self):
    self._converter = _GetConverter('tpm.tpm')

  def testGenerateDefinition(self):
    actual = self._converter.GenerateDefinition()

    expect = text_format.Parse(
        '''
        name: "tpm.tpm"
        description: "Probe TPM info."
        parameter_definitions {
          name: "manufacturer"
          description: "The manufacturer of TPM."
          value_type: STRING
        }
        parameter_definitions {
          name: "vendor_specific"
          description: "The vendor specific string of TPM."
          value_type: STRING
        }
        parameter_definitions {
          name: "spec_level"
          description: "The spec level of TPM."
          value_type: INT
        }''', probe_info_analytics.ProbeFunctionDefinition())
    self.assertEqual(actual, expect)

  def testParseProbeParam_CanGenerateProbeStatement(self):
    probe_params = [
        _CreateIntProbeParam('spec_level', 162),
        _CreateStrProbeParam('manufacturer', 'CROS'),
        _CreateStrProbeParam('vendor_specific', 'xCG fTPM'),
    ]

    actual = self._converter.ParseProbeParams(
        probe_params, allow_missing_params=False,
        comp_name_for_probe_statement='comp_name')

    expected_probe_statements = [
        probe_config_types.ComponentProbeStatement(
            'tpm', 'comp_name', {
                'eval': {
                    'tpm': {}
                },
                'expect': {
                    'spec_level': [True, 'int', '!eq 162'],
                    'vendor_specific': [True, 'str', '!eq xCG fTPM'],
                    'manufacturer': [True, 'str', '!eq 0x43524f53']
                }
            })
    ]
    assert actual.output is not None
    self.assertCountEqual(actual.output, expected_probe_statements)
    self.assertCanGenerateGenericProbeStatements(expected_probe_statements)

  def testParseProbeResult_CanGenerateProbeParameter(self):
    probe_result = {
        'tpm': [{
            'manufacturer': '0x43524f53',
            'spec_level': '162',
            'vendor_specific': 'xCG fTPM'
        }]
    }

    actual = self._converter.ParseProbeResult(probe_result)
    expected_probe_parameters = [
        analyzers.ParsedProbeParameter('tpm',
                                       _CreateIntProbeParam('spec_level', 162)),
        analyzers.ParsedProbeParameter(
            'tpm', _CreateStrProbeParam('manufacturer', 'CROS')),
        analyzers.ParsedProbeParameter(
            'tpm', _CreateStrProbeParam('vendor_specific', 'xCG fTPM'))
    ]
    self.assertCountEqual(actual, expected_probe_parameters)

  def testGetNormalizedProbeParams_CanGetParamsWithCorrectFormat(self):
    probe_params = [
        _CreateIntProbeParam('spec_level', 162),
        _CreateStrProbeParam('manufacturer', 'CROS'),
        _CreateStrProbeParam('vendor_specific', 'xCG fTPM'),
    ]

    actual = self._converter.GetNormalizedProbeParams(probe_params)

    expected_probe_params = [
        _CreateIntProbeParam('spec_level', 162),
        _CreateStrProbeParam('manufacturer', 'CROS'),
        _CreateStrProbeParam('vendor_specific', 'xCG fTPM'),
    ]

    self.assertCountEqual(actual, expected_probe_params)


if __name__ == '__main__':
  unittest.main()
