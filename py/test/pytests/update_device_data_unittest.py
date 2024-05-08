#!/usr/bin/env python3
# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
# pylint: disable=protected-access

import unittest
from unittest import mock

from cros.factory.test import device_data
from cros.factory.test.i18n import _
from cros.factory.test.l10n import regions
from cros.factory.test.pytests import update_device_data
from cros.factory.test import test_ui
from cros.factory.test import ui_templates
from cros.factory.utils import sync_utils
from cros.factory.utils import type_utils


_KNOWN_KEY_LABELS = update_device_data._KNOWN_KEY_LABELS
_COMMONLY_USED_REGIONS = update_device_data._COMMONLY_USED_REGIONS


class FakeArgs:

  def __init__(self, **kwargs):
    self.manual_input = True
    self.config_name = None
    self.fields = None
    for k, v in kwargs.items():
      setattr(self, k, v)


class FakeEntry:

  def __init__(self, *args):
    self.key = f'{args[0]}_key'
    self.value = f'{args[0]}_value'
    self.label = f'{args[0]}_label'

  def __eq__(self, other):
    return isinstance(other, type(self)) and vars(self) == vars(other)


class GetDisplayNameWithKeyUnitTest(unittest.TestCase):

  def testNameGiven(self):
    name = 'super power name'
    cases = [{
        'name': 'test random input',
        'key': 'irrelevant.key',
    }, {
        'name': 'keys in the known set should still be override',
        'key': device_data.KEY_SERIAL_NUMBER,
    }]

    for c in cases:
      self.assertEqual(
          update_device_data.GetDisplayNameWithKey(c['key'], name), name,
          msg=f'test failed at {c["name"]}')

  def testKnownKey(self):
    for known_key, expected in _KNOWN_KEY_LABELS.items():
      self.assertEqual(
          update_device_data.GetDisplayNameWithKey(known_key), expected)

  def testNoNameGivenAndNotKnownKey(self):
    irrelevant_key = 'irrelevant.key'
    self.assertEqual(
        update_device_data.GetDisplayNameWithKey(irrelevant_key),
        irrelevant_key)


class CreateRegionOptionsUnitTest(unittest.TestCase):

  def _ValidateOptionMatchesDisplayText(self, options):
    for idx, option in enumerate(options):
      description = regions.REGIONS[option[0]].description
      self.assertEqual(option[1], f'{idx + 1} - {option[0]}: {description}')

  def testAllRegion(self):
    options = update_device_data.CreateRegionOptions()

    self._ValidateOptionMatchesDisplayText(options)
    # Test commonly used regions should be in first sections.

    option_regions = [option[0] for option in options]
    self.assertEqual(
        set(option_regions[:len(_COMMONLY_USED_REGIONS)]),
        set(_COMMONLY_USED_REGIONS))

  def testWithSomeAllowedRegions(self):
    available_regions = ['us', 'tw']
    options = update_device_data.CreateRegionOptions(available_regions)

    self._ValidateOptionMatchesDisplayText(options)

    self.assertEqual([option[0] for option in options], available_regions)

  def testInvalidAllowedRegions(self):
    with self.assertRaisesRegex(
        ValueError, r"value of options for 'vpd\.ro\.region'"
        r" must be a subset of known regions"):
      available_regions = ['alien']
      update_device_data.CreateRegionOptions(available_regions)


class CreateSelectionOptionsUnitTest(unittest.TestCase):

  def testValidValueCheckWithNonListItem(self):
    value_check = ['str_input', 3, False]

    output = update_device_data.CreateSelectOptions(value_check)

    expected = [('str_input', '1 - str_input'), (3, '2 - 3'),
                (False, '3 - False')]
    self.assertEqual(output, expected)

  def testValidValueCheckItemWithListItem(self):
    value_check = [['option'], ['option_value', 'option_text'],
                   ['option_value', 'option_text', 'dummy']]

    output = update_device_data.CreateSelectOptions(value_check)

    expected = [
        ('option', '1 - option'),
        ('option_value', '2 - option_text'),
        ('option_value', '3 - option_text'),
    ]
    self.assertEqual(output, expected)

  def testUnsupportedValueCheckItemType(self):
    value_check = [('tuple not supported', )]
    with self.assertRaisesRegex(
        ValueError, r"Unsupported value_check \[\('tuple not supported',\)\]"):
      update_device_data.CreateSelectOptions(value_check)

  def testEmptyValueCheckItem(self):
    with self.assertRaisesRegex(
        ValueError, r'Each element of `value_check` must not be an empty list'):
      update_device_data.CreateSelectOptions([[]])


class TextDataEntryUnitTest(unittest.TestCase):

  def testInit_InvalidRegexPattern(self):
    with self.assertRaises(Exception):
      update_device_data.TextDataEntry('unused_key', None, 'unused_label', '[')

  def testSetValueFromString(self):
    entry = update_device_data.TextDataEntry('unused_key', 'value',
                                             'unused_label', "[a-zA-Z0-9]+")
    self.assertEqual(entry.value, 'value')

    entry.SetValueFromString('new_value')

    self.assertEqual(entry.value, 'new_value')

  def testSetValueFromString_NotMatchingPattern(self):
    unmatched_value = 'I do not say hello'
    entry = update_device_data.TextDataEntry('key', 'init_value',
                                             'unused_label', '^Hello, .*$')

    with self.assertRaisesRegex(
        ValueError, r"Cannot use value 'I do not say hello' for key 'key': "
        r"not matching pattern '\^Hello, \.\*\$'"):
      entry.SetValueFromString(unmatched_value)

    self.assertEqual(entry.value, 'init_value')

  def testGetValue(self):
    update_value = 'Hello, world'
    entry = update_device_data.TextDataEntry('unused_key', None, 'unused_label',
                                             '^Hello, .*$')
    self.assertEqual(entry.GetValue(), entry.value)
    self.assertEqual(entry.GetValue(), None)

    entry.SetValueFromString(update_value)

    self.assertEqual(entry.GetValue(), entry.value)
    self.assertEqual(entry.GetValue(), update_value)


class SelectionDataEntryUnitTest(unittest.TestCase):

  test_options = [(1, 'text A'), (2, 'text B')]

  def testSetValueFromString(self):
    entry = update_device_data.SelectionDataEntry(
        'unused_key', None, 'unused_label', self.test_options)
    entry.SetValueFromString('1')
    self.assertEqual(entry.value, 1)

  def testSetValueFromString_NotInOption(self):
    entry = update_device_data.SelectionDataEntry(
        'key', 'init_value', 'unused_label', self.test_options)
    update_value = 'update_value'

    with self.assertRaisesRegex(
        ValueError, r"Cannot use value 'update_value' for key 'key': "
        r"not in options"):
      entry.SetValueFromString(update_value)

    self.assertEqual(entry.value, 'init_value')

  def testGetValue(self):
    update_value = self.test_options[1][0]
    entry = update_device_data.SelectionDataEntry(
        'unused_key', 1, 'unused_label', self.test_options)
    self.assertEqual(entry.GetValue(), entry.value)
    self.assertEqual(entry.GetValue(), 1)

    entry.SetValueFromString(str(update_value))

    self.assertEqual(entry.GetValue(), entry.value)
    self.assertEqual(entry.GetValue(), update_value)

  def testGetOptions(self):
    entry = update_device_data.SelectionDataEntry(
        'unused_key', 1, 'unused_label', self.test_options)
    self.assertEqual(entry.GetOptions(), self.test_options)

  def testGetIndex(self):
    idx = 0
    value = self.test_options[idx][0]
    entry = update_device_data.SelectionDataEntry(
        'unused_key', value, 'unused_label', self.test_options)
    self.assertEqual(entry.GetSelectedIndex(), 0)

    idx = 1
    value = self.test_options[idx][0]
    entry.SetValueFromString(str(value))
    self.assertEqual(entry.GetSelectedIndex(), 1)

  def testGetIndex_ValueNotSet(self):
    with self.assertRaises(ValueError):
      entry = update_device_data.SelectionDataEntry(
          'unused_key', None, 'unused_label', self.test_options)
      entry.GetSelectedIndex()


class CreateDataEntryUnitTest(unittest.TestCase):

  def setUp(self):
    self.mock_check_patcher = mock.patch.object(
        device_data, 'CheckValidDeviceDataKey', autospec=True)
    self.mock_check_patcher.start()
    self.addCleanup(mock.patch.stopall)

  def testInvalidDeviceKey(self):
    self.mock_check_patcher.stop()
    with self.assertRaises(KeyError):
      update_device_data.CreateDataEntry('impossible.key', 'unused_value', None,
                                         None)

  @mock.patch.object(device_data, 'GetDeviceData', autospec=True)
  def testGetValueFromDeviceData(self, mock_get_device_data):
    mock_get_device_data.return_value = 'value_from_device_data'

    entry = update_device_data.CreateDataEntry('test.key', None, None, None)

    mock_get_device_data.assert_called_with('test.key')
    self.assertEqual(entry.GetValue(), 'value_from_device_data')

  def testBoolValue(self):
    entry = update_device_data.CreateDataEntry('test.key', True, None, None)

    self.assertIsInstance(entry, update_device_data.SelectionDataEntry)
    self.assertEqual(entry.GetOptions(), [(True, '1 - True'),
                                          (False, '2 - False')])

  def testRegionKey(self):
    entry = update_device_data.CreateDataEntry(device_data.KEY_VPD_REGION, 'tw',
                                               None, None)
    self.assertIsInstance(entry, update_device_data.SelectionDataEntry)

  def testValueCheckWithOptions(self):
    value_check = ['option A', 'option B']

    entry = update_device_data.CreateDataEntry('test.key', 'unused_value', None,
                                               value_check)

    self.assertIsInstance(entry, update_device_data.SelectionDataEntry)
    self.assertEqual(entry.GetOptions(), [('option A', '1 - option A'),
                                          ('option B', '2 - option B')])

  def testValueCheckWithRegexPattern(self):
    entry = update_device_data.CreateDataEntry('test.key', 'unused_value', None,
                                               '.*')
    self.assertIsInstance(entry, update_device_data.TextDataEntry)

  def testValueCheckWithNone(self):
    entry = update_device_data.CreateDataEntry('test.key', 'unused_value', None,
                                               None)
    self.assertIsInstance(entry, update_device_data.TextDataEntry)

  def testInvalidValueCheck(self):
    key = 'test.key'
    value_check = (1, 2)

    with self.assertRaisesRegex(
        TypeError, r"value_check \(1, 2\) for 'test.key'"
        r" must be either regex, sequence, or None\."):
      update_device_data.CreateDataEntry(key, 'unused_value', None, value_check)


class UpdateDeviceDataUnitTest(unittest.TestCase):

  def setUp(self):
    self.test = update_device_data.UpdateDeviceData()
    # yapf: disable
    self.test.args = FakeArgs()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.ui = mock.create_autospec(test_ui.StandardUI)
    type_utils.LazyProperty.Override(self.test, 'ui', self.ui)
    # yapf: disable
    self.created_fake_entries = []  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

    # yapf: enable

    def mock_create_entry(*args, **kwargs):
      self.created_fake_entries.append(FakeEntry(*args, **kwargs))
      return self.created_fake_entries[-1]

    patcher = mock.patch.object(test_ui, 'EventLoop', autospec=True)
    self.test.event_loop = patcher.start().return_value
    patcher = mock.patch.object(update_device_data, 'CreateDataEntry',
                                side_effect=mock_create_entry, autospec=True)
    self.mock_create_data_entry = patcher.start()
    self.addCleanup(mock.patch.stopall)

  def test_setUp_NoValidData(self):
    with self.assertRaisesRegex(
        ValueError, r'Either config_name or fields must be specified\.'):
      # yapf: disable
      self.test.args = FakeArgs(config_name=None, fields=None)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.test.setUp()

  @mock.patch.object(device_data, 'LoadConfig', autospec=True)
  def test_setUp_LoadFieldsFromConfig(self, mock_load):
    config = {
        'key1': 'value1',
        'key2': 'value2'
    }
    mock_load.return_value = config
    # yapf: disable
    self.test.args = FakeArgs(config_name='config_file')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.test.setUp()

    mock_load.assert_called_once_with('config_file')
    self.mock_create_data_entry.assert_has_calls(
        [mock.call(k, v, None, None) for k, v in config.items()])
    self.assertEqual(self.created_fake_entries,
                     [FakeEntry(k, v, None, None) for k, v in config.items()])
    self.ui.ToggleTemplateClass.assert_called_once_with('font-large', True)

  def test_setUp_LoadFieldsFromFields(self):
    fields = ['key1', 'key2']
    # yapf: disable
    self.test.args = FakeArgs(fields=fields)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.test.setUp()

    self.mock_create_data_entry.assert_has_calls([mock.call(k) for k in fields])
    self.assertEqual(self.created_fake_entries, [FakeEntry(k) for k in fields])

  @mock.patch.object(update_device_data.UpdateDeviceData, 'ManualInput',
                     autospec=True)
  def test_runTest_Manual(self, mock_input):
    # yapf: disable
    self.test.args = FakeArgs(fields=['key1', 'key2'])  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.test.setUp()
    self.test.runTest()

    mock_input.assert_has_calls(
        [mock.call(self.test, entry) for entry in self.test.entries])

  @mock.patch.object(device_data, 'UpdateDeviceData', autospec=True)
  def test_runTest_Auto(self, mock_update):
    # yapf: disable
    self.test.args = FakeArgs(fields=['key1', 'key2'], manual_input=False)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.test.setUp()
    self.test.runTest()

    mock_update.assert_called_once_with(
        {entry.key: entry.value
         for entry in self.test.entries})

  @mock.patch.object(update_device_data.UpdateDeviceData, '_RenderSelectBox',
                     autospec=True)
  @mock.patch.object(sync_utils, 'QueueGet', autospec=True)
  def testManualInput_SelectionDataEntry(self, mock_queue_get, mock_select):
    mock_queue_get.return_value = None
    options = [('value1', 'text1'), ('value2', 'text2')]
    entry = update_device_data.SelectionDataEntry('key', 'value1',
                                                  'unused_label', options)

    self.test.ManualInput(entry)

    event_subtype = 'devicedata-' + entry.key
    mock_select.assert_called_once_with(self.test, entry)
    self.ui.BindKeyJS.assert_called_once_with(
        test_ui.ENTER_KEY,
        f'window.sendSelectValue({entry.key!r}, {event_subtype!r})')
    self.ui.UnbindAllKeys.assert_called_once()

  @mock.patch.object(update_device_data.UpdateDeviceData, '_RenderInputBox',
                     autospec=True)
  @mock.patch.object(sync_utils, 'QueueGet', autospec=True)
  def testManualInput_RenderInputBox(self, mock_queue_get, mock_input):
    mock_queue_get.return_value = None
    entry = update_device_data.TextDataEntry('key', 'unused_value',
                                             'unused_label', '[a-zA-Z0-9]+')

    self.test.ManualInput(entry)

    event_subtype = 'devicedata-' + entry.key
    mock_input.assert_called_once_with(self.test, entry)
    self.ui.BindKeyJS.assert_called_once_with(
        test_ui.ENTER_KEY,
        f'window.sendInputValue({entry.key!r}, {event_subtype!r})')

  @mock.patch.object(update_device_data.UpdateDeviceData, '_RenderSelectBox',
                     autospec=True)
  @mock.patch.object(update_device_data.UpdateDeviceData, '_SetErrorMsg',
                     autospec=True)
  @mock.patch.object(sync_utils, 'QueueGet', autospec=True)
  def testManualInput_FinishInputByPressESC(self, mock_queue_get,
                                            mock_error_msg, unused_mock_select):
    mock_error_msg.side_effect = Exception('Value not set.')
    esc_pressed_event = None
    mock_queue_get.return_value = esc_pressed_event

    # Value is set.
    entry = update_device_data.TextDataEntry('unused_key', 'value',
                                             'unused_label', '[a-zA-Z0-9]+')

    self.test.ManualInput(entry)

    mock_error_msg.assert_not_called()
    # yapf: disable
    self.test.ui.UnbindAllKeys.assert_called_once()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.event_loop.ClearHandlers.assert_called_once()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # Value not set.
    with self.assertRaisesRegex(Exception, r'Value not set\.'):
      entry = update_device_data.TextDataEntry('unused_key', None, 'label',
                                               '[a-zA-Z0-9]+')
      self.test.ManualInput(entry)
      mock_error_msg.assert_called_once_with(
          _('No valid data on machine for {label}.', label=entry.label))

  @mock.patch.object(update_device_data.UpdateDeviceData, '_RenderSelectBox',
                     autospec=True)
  @mock.patch.object(sync_utils, 'QueueGet', autospec=True)
  @mock.patch.object(device_data, 'UpdateDeviceData', autospec=True)
  def testManualInput_SetValue(self, mock_update, mock_queue_get,
                               unused_mock_select):
    set_value = 'setValue'
    mock_queue_get.return_value = mock.Mock(data=set_value)
    entry = update_device_data.TextDataEntry('key', None, 'label',
                                             '[a-zA-Z0-9]+')

    self.test.ManualInput(entry)

    mock_update.assert_called_once_with({entry.key: set_value})

  @mock.patch.object(update_device_data.UpdateDeviceData, '_RenderSelectBox',
                     autospec=True)
  @mock.patch.object(update_device_data.UpdateDeviceData, '_SetErrorMsg',
                     autospec=True)
  @mock.patch.object(sync_utils, 'QueueGet', autospec=True)
  @mock.patch.object(device_data, 'UpdateDeviceData', autospec=True)
  def testManualInput_SetInvalidValue(self, mock_update, mock_queue_get,
                                      mock_error_msg, unused_mock_select):
    invalid_value = '_'
    set_value = 'setValue'
    mock_queue_get.side_effect = [
        mock.Mock(data=invalid_value),
        mock.Mock(data=set_value)
    ]
    entry = update_device_data.TextDataEntry('key', None, 'label',
                                             '[a-zA-Z0-9]+')

    self.test.ManualInput(entry)

    mock_error_msg.assert_called_once_with(
        self.test, _('Invalid value for {label}.', label=entry.label))
    mock_update.assert_called_once_with({entry.key: set_value})

  def test_SetErrorMsg(self):
    msg = 'error_msg'
    self.test._SetErrorMsg(msg)
    self.ui.SetHTML.assert_called_once_with(
        ['<span class="test-error">', msg, '</span>'], id='errormsg')

  @mock.patch.object(ui_templates, 'SelectBox', autospec=True)
  def test_RenderSelectBox(self, mock_select):
    mock_box = mock_select.return_value
    mock_box.GenerateHTML.return_value = 'html'
    options = [('value1', 'text1'), ('value2', 'text2')]
    entry = update_device_data.SelectionDataEntry('key', 'value1', 'label',
                                                  options)

    self.test._RenderSelectBox(entry)

    mock_select.assert_called_once_with(entry.key,
                                        update_device_data._SELECTION_PER_PAGE)
    mock_box.AppendOption.assert_has_calls(
        [mock.call(value, text) for value, text in options])
    mock_box.SetSelectedIndex.assert_called_once_with(entry.GetSelectedIndex())
    self.ui.SetState.assert_called_once_with([
        _('Select {label}:', label=entry.label), 'html',
        _('Select with ENTER')
    ])
    self.ui.SetFocus.assert_called_once_with(entry.key)

  def test_RenderInputBox(self):
    entry = update_device_data.TextDataEntry('key', 'value', 'label',
                                             '[a-zA-Z0-9]+')

    self.test._RenderInputBox(entry)

    self.ui.SetState.assert_called_once_with([
        _('Enter {label}: ', label=entry.label),
        f"<input type=\"text\" id=\"{entry.key}\" "
        f"value=\"{entry.value or ''}\""
        f" style=\"width: 20em;\"><div id=\"errormsg\" "
        f"class=\"test-error\"></div>",
        _('(ESC to keep current value)')
    ])
    self.ui.SetSelected.assert_called_once_with(entry.key)
    self.ui.SetFocus.assert_called_once_with(entry.key)


if __name__ == '__main__':
  unittest.main()
