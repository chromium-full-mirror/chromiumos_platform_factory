#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import threading
from typing import Dict, Mapping, Union
import unittest
from unittest import mock

from cros.factory.device import device_utils
from cros.factory.test import device_data
from cros.factory.test import server_proxy
from cros.factory.test import test_ui
from cros.factory.test.i18n import _
from cros.factory.test.pytests import shopfloor_service
from cros.factory.test.rules import privacy
from cros.factory.test.utils.url_spec import URLSpec
from cros.factory.utils import debug_utils
from cros.factory.utils import log_utils
from cros.factory.utils import process_utils
from cros.factory.utils import shelve_utils
from cros.factory.utils import type_utils
from cros.factory.utils import webservice_utils


class FakeArgs:

  def __init__(self, **kwargs):
    self.method: str = 'GetVersion'  # type: ignore #TODO(b/338318729) Fixit!
    self.args: list = None  # type: ignore #TODO(b/338318729) Fixit!
    self.kargs: Mapping = None  # type: ignore #TODO(b/338318729) Fixit!
    self.raw_invocation: bool = False  # type: ignore #TODO(b/338318729) Fixit!
    self.server_url: Union[str, Dict[str, str]] = None  # type: ignore #TODO(b/338318729) Fixit!

    for k, v in kwargs.items():
      setattr(self, k, v)


class ShopfloorServiceUnitTest(unittest.TestCase):

  def setUp(self):
    self.test = shopfloor_service.ShopfloorService()
    self.ui = mock.create_autospec(test_ui.StandardUI)
    type_utils.LazyProperty.Override(self.test, 'ui', self.ui)

    def _GetFakeDeviceData(key='', default=None):
      return {
          key: key + '.data'
      } if key else default

    patcher = mock.patch.object(device_data, 'GetDeviceData',
                                side_effect=_GetFakeDeviceData, autospec=True)
    self.mock_get_device_data = patcher.start()
    patcher = mock.patch.object(device_data, 'DeleteDeviceData', autospec=True)
    self.mock_delete_device_data = patcher.start()
    patcher = mock.patch.object(device_data, 'UpdateDeviceData', autospec=True)
    self.mock_update_device_data = patcher.start()
    patcher = mock.patch.object(shelve_utils, 'DictShelfView', autospec=True)
    self.mock_dict_shelf = patcher.start().return_value
    patcher = mock.patch.object(device_utils, 'CreateDUTInterface',
                                autospec=True)
    self.mock_dut = patcher.start().return_value
    patcher = mock.patch.object(test_ui, 'EventLoop', autospec=True)
    self.test.event_loop = patcher.start().return_value
    patcher = mock.patch.object(URLSpec, 'FindServerURL',
                                side_effect=lambda url, unused_dut: url,
                                autospec=True)
    self.mock_find_server_url = patcher.start()
    patcher = mock.patch.object(webservice_utils, 'CreateWebServiceProxy',
                                autospec=True)
    self.mock_create_web_service_proxy = patcher.start()
    patcher = mock.patch.object(server_proxy, 'GetServerProxy', autospec=True)
    self.mock_get_server_proxy = patcher.start()
    patcher = mock.patch.object(log_utils, 'NoisyLogger', autospec=True)
    self.mock_logger = patcher.start().return_value
    patcher = mock.patch.object(process_utils, 'WaitEvent', autospec=True)
    self.mock_wait_event = patcher.start()
    self.addCleanup(mock.patch.stopall)

    self.test.args = FakeArgs()  # type: ignore #TODO(b/338318729) Fixit!

  @mock.patch.object(device_data, 'FlattenData',
                     side_effect=lambda dict, domain: dict or domain,
                     autospec=True)
  def test_GetFactoryDeviceData(self, mock_flatten):
    self.mock_dut.CallOutput.return_value = 'dut.hwid.data'

    self.test.setUp()
    data = self.test.GetFactoryDeviceData()

    self.mock_get_device_data.assert_has_calls([
        mock.call('serials', {}),
        mock.call('factory', {}),
        mock.call('hwid', 'dut.hwid.data')
    ])
    self.mock_dut.CallOutput.assert_called_once_with('crossystem hwid')
    mock_flatten.assert_has_calls([
        mock.call({'serials': 'serials.data'}, 'serials'),
        mock.call({'factory': 'factory.data'}, 'factory'),
    ])
    self.assertEqual(
        data, {
            'serials': 'serials.data',
            'factory': 'factory.data',
            'hwid': {
                'hwid': 'hwid.data'
            }
        })

  def test_UpdateAutoResults(self):
    args = ['arg1', 'arg2']
    result_dict = {}  # type: ignore #TODO(b/338318729) Fixit!

    self.test.setUp()
    for method in self.test.METHODS:
      self.test.UpdateAutoResults(method, result_dict, args)

    self.assertEqual(
        result_dict, {
            'factory.start_arg2': True,
            'factory.end_arg2': True,
            'factory.event_arg2': True,
            'factory.activate_reg_code': True
        })

  def test_UpdateDeviceData_AllKeysHasValue(self):
    data = {
        'serials': 'serials.data',
        'vpd': 'vpd.data',
        'component': 'component.data',
        'factory': 'factory.data',
        'hwid': 'hwid.data',
        'feature_management': 'feature_management.data'
    }

    self.test.setUp()
    self.test.UpdateDeviceData(data)

    self.mock_delete_device_data.assert_called_once_with([])
    self.mock_update_device_data.assert_called_once_with(data)

  def test_UpdateDeviceData_IllegalKeysExist(self):
    self.test.setUp()
    with self.assertRaisesRegex(ValueError,
                                r"Invalid response keys: \['illegal'\]"):
      self.test.UpdateDeviceData({'illegal': 'illegal.data'})

    self.mock_delete_device_data.assert_not_called()
    self.mock_update_device_data.assert_not_called()

  def test_UpdateDeviceData_DeleteKeysWithNoneValue(self):
    data = {
        'serials': 'serials.data',
        'vpd': 'vpd.data',
        'component': 'component.data',
        'factory': None,
        'hwid': None,
        'feature_management': None
    }

    self.test.setUp()
    self.test.UpdateDeviceData(data)

    self.mock_delete_device_data.assert_called_once_with(
        ['factory', 'hwid', 'feature_management'])
    self.mock_update_device_data.assert_called_once_with({
        'serials': 'serials.data',
        'vpd': 'vpd.data',
        'component': 'component.data',
    })

  @mock.patch.object(privacy, 'FilterDict',
                     return_value={'filtered.key': 'filtered.val'},
                     autospec=True)
  def test_FilterDict_ContainKeys(self, mock_filter_dict):
    self.mock_dict_shelf.GetKeys.return_value = ['filtered.key']

    filtered_dict = self.test.FilterDict({
        'serials': 'serials.data',
        'vpd': 'vpd.data',
    })

    self.mock_dict_shelf.SetValue.assert_has_calls(
        [mock.call('serials', 'serials.data'),
         mock.call('vpd', 'vpd.data')])
    mock_filter_dict.assert_called_once_with(self.mock_dict_shelf.GetValue(''))
    self.assertEqual(filtered_dict, {'filtered.key': 'filtered.val'})

  def test_FilterDict_NoKeys(self):
    self.mock_dict_shelf.GetKeys.return_value = []

    filtered_dict = self.test.FilterDict({})

    self.mock_dict_shelf.SetValue.assert_not_called()
    self.assertEqual(filtered_dict, {})

  def test_ShowMessage_NoRetryButton(self):
    self.test.ShowMessage('caption', 'css', 'message')
    self.ui.SetState.assert_called_once_with([
        '<span class="css">', 'caption',
        '</span><p><textarea rows=25 cols=90 readonly>', 'message',
        '</textarea><p>', ''
    ])

  def test_ShowMessage_AddRetryButton(self):
    self.test.ShowMessage('caption', 'css', 'message', retry=True)
    self.ui.SetState.assert_called_once_with([
        '<span class="css">', 'caption',
        '</span><p><textarea rows=25 cols=90 readonly>', 'message',
        '</textarea><p>',
        ['<button data-test-event="retry">',
         _('Retry'), '</button>']
    ])

  @mock.patch.object(threading, 'Event', autospec=True)
  @mock.patch.object(shopfloor_service.ShopfloorService, 'ShowMessage',
                     autospec=True)
  def test_HandleError(self, mock_show_message, mock_event):
    threading_event = mock_event.return_value

    self.test.setUp()
    self.test.HandleError('message', 'invocation_message')

    mock_show_message.assert_called_once_with(
        self.test, _('Shopfloor exception:'), 'test-status-failed large',
        'message\ninvocation_message\nmessage', True)
    self.mock_wait_event.assert_called_once_with(threading_event)
    threading_event.clear.assert_called_once()

  def test_runTest_AddRetryEvent(self):
    self.test.setUp()
    self.test.runTest()

    assert self.test.event_loop.AddEventHandler.call_count == 1  # type: ignore #TODO(b/338318729) Fixit!
    args, unused_kwargs = self.test.event_loop.AddEventHandler.call_args  # type: ignore #TODO(b/338318729) Fixit!
    assert args[0] == 'retry'

  def test_runTest_GetServerByUrl(self):
    fake_url = 'fake_url'
    self.test.args = FakeArgs(server_url=fake_url)  # type: ignore #TODO(b/338318729) Fixit!
    self.mock_find_server_url.return_value = fake_url

    self.test.setUp()
    self.test.runTest()

    self.mock_find_server_url.assert_called_once_with(fake_url, self.mock_dut)
    self.mock_create_web_service_proxy.assert_called_once_with(fake_url)

  def test_runTest_GetServerByServerProxy(self):
    self.mock_find_server_url.return_value = None

    self.test.setUp()
    self.test.runTest()

    self.mock_get_server_proxy.assert_called_once()

  def test_runTest_UseRawInvocationForInternalServer(self):
    self.test.args = FakeArgs(raw_invocation=True)  # type: ignore #TODO(b/338318729) Fixit!
    self.mock_find_server_url.return_value = None

    self.test.setUp()
    with self.assertRaisesRegex(
        ValueError, r'Argument `raw_invocation` allowed only for external '
        r'server \(need `server_url`\)\.'):
      self.test.runTest()

  @mock.patch.object(shopfloor_service, 'ServiceSpec',
                     return_value=mock.MagicMock(), autospec=True)
  def test_runTest_CreateServiceSpecWithRawInvocation(self, mock_service_spec):
    self.test.args = FakeArgs(server_url='fake_url', raw_invocation=True)  # type: ignore #TODO(b/338318729) Fixit!

    self.test.setUp()
    self.test.runTest()

    mock_service_spec.assert_called_once_with(has_data=False)

  def test_runTest_UseKargsWithoutRawInvocation(self):
    self.test.args = FakeArgs(kargs={'fake_karg_key': 'fake_karg_val'},  # type: ignore #TODO(b/338318729) Fixit!
                              raw_invocation=False)

    self.test.setUp()
    with self.assertRaisesRegex(ValueError,
                                r'`kargs` only allowed for `raw_invocation`\.'):
      self.test.runTest()

  def test_runTest_GetSpecByUnknownMethod(self):
    self.test.args = FakeArgs(method='fake_method', raw_invocation=False)  # type: ignore #TODO(b/338318729) Fixit!

    self.test.setUp()
    with self.assertRaisesRegex(
        ValueError, r'Unknown method for shopfloor service: fake_method'):
      self.test.runTest()

  @mock.patch.object(shopfloor_service, 'ServiceSpec', autospec=True)
  def test_runTest_GetDeviceDataBySpecDataArgs(self, mock_service_spec):
    self.test.args = FakeArgs(server_url='fake_url', raw_invocation=True)  # type: ignore #TODO(b/338318729) Fixit!
    mock_spec = mock.MagicMock()
    mock_spec.data_args = ['key1', 'key2', 'key3']
    mock_service_spec.return_value = mock_spec

    self.test.setUp()
    self.test.runTest()

    self.mock_get_device_data.assert_has_calls(
        [mock.call('key1'),
         mock.call('key2'),
         mock.call('key3')])

  @mock.patch.object(shopfloor_service.ShopfloorService, 'GetFactoryDeviceData',
                     autospec=True)
  @mock.patch.object(shopfloor_service, 'ServiceSpec', autospec=True)
  def test_runTest_GetFactoryDeviceDataWhenSpecHasData(self, mock_service_spec,
                                                       mock_get_factory_data):
    self.test.args = FakeArgs(server_url='fake_url', raw_invocation=True)  # type: ignore #TODO(b/338318729) Fixit!
    mock_spec = mock.MagicMock()
    mock_spec.has_data = True
    mock_service_spec.return_value = mock_spec

    self.test.setUp()
    self.test.runTest()

    mock_get_factory_data.assert_called_once()

  @mock.patch.object(logging, 'info', autospec=True)
  @mock.patch.object(shopfloor_service, 'ServiceSpec', autospec=True)
  def test_runTest_LogTestArgs(self, mock_service_spec, mock_logging_info):
    self.test.args = FakeArgs(method='GetVersion', server_url='fake_url',  # type: ignore #TODO(b/338318729) Fixit!
                              raw_invocation=True, args=['fake_arg'],
                              kargs={'fake_karg.key': 'fake_karg.val'})
    mock_spec = mock.MagicMock()
    mock_spec.has_privacy_args = False
    mock_spec.data_args = ['fake_spec_arg']
    mock_spec.has_data = True
    mock_service_spec.return_value = mock_spec

    self.test.setUp()
    self.test.runTest()

    mock_logging_info.assert_any_call(
        'shopfloor_service: invoking %s%s', 'GetVersion',
        ("({'serials.serials': 'serials.data', "
         "'factory.factory': 'factory.data', 'hwid': {'hwid': 'hwid.data'}}, "
         "{'fake_spec_arg': 'fake_spec_arg.data'}, 'fake_arg')"
         "{'fake_karg.key': 'fake_karg.val'}"))

  @mock.patch.object(logging, 'info', autospec=True)
  @mock.patch.object(shopfloor_service, 'ServiceSpec', autospec=True)
  def test_runTest_ReplaceLogWhenSpecHasPrivacyArgs(self, mock_service_spec,
                                                    mock_logging_info):
    self.test.args = FakeArgs(method='GetVersion', server_url='fake_url',  # type: ignore #TODO(b/338318729) Fixit!
                              raw_invocation=True)
    mock_spec = mock.MagicMock()
    mock_spec.has_privacy_args = True
    mock_service_spec.return_value = mock_spec

    self.test.setUp()
    self.test.runTest()

    mock_logging_info.assert_any_call('shopfloor_service: invoking %s%s',
                                      'GetVersion', '(...)')

  @mock.patch.object(shopfloor_service.ShopfloorService, 'ShowMessage',
                     autospec=True)
  @mock.patch.object(logging, 'info', autospec=True)
  @mock.patch.object(shopfloor_service.ShopfloorService, 'FilterDict',
                     return_value={'filtered.key': 'filtered.val'},
                     autospec=True)
  @mock.patch.object(shopfloor_service.ShopfloorService, 'UpdateAutoResults',
                     autospec=True)
  @mock.patch.object(shopfloor_service.ShopfloorService, 'UpdateDeviceData',
                     autospec=True)
  def test_runTest_GetResultAndUpdateData(
      self, mock_update_device_data, mock_update_auto_results, mock_filter_dict,
      mock_logging_info, mock_show_message):
    method = 'GetVersion'
    fake_args = [1, 2, 3]
    self.test.args = FakeArgs(method=method, args=fake_args)  # type: ignore #TODO(b/338318729) Fixit!
    fake_result = {
        'fake.key': 'fake.val'
    }
    mock_server = self.mock_get_server_proxy.return_value
    mock_server.GetVersion.return_value = fake_result

    self.test.setUp()
    self.test.runTest()

    mock_server.GetVersion.assert_called_once_with(*fake_args)
    mock_show_message.assert_called_once_with(self.test,
                                              _('Invoking shopfloor service'),
                                              'test-status-active large',
                                              "{'GetVersion': [1, 2, 3]}")
    mock_filter_dict.assert_called_once_with(fake_result)
    mock_logging_info.assert_any_call('shopfloor_service: %s%s => %r',
                                      'GetVersion', '(1, 2, 3)',
                                      {'filtered.key': 'filtered.val'})
    mock_update_auto_results.assert_called_once_with(self.test, method,
                                                     fake_result, fake_args)
    mock_update_device_data.assert_called_once_with(self.test, fake_result)

  @mock.patch.object(shopfloor_service.ShopfloorService, 'UpdateDeviceData',
                     autospec=True)
  @mock.patch.object(shopfloor_service.ShopfloorService, 'HandleError',
                     autospec=True)
  @mock.patch.object(debug_utils, 'FormatExceptionOnly',
                     return_value='fake_format_fault', autospec=True)
  def test_runTest_GetResultAndUpdateData_RaiseException(
      self, unused_mock_format_exception, mock_handle_error,
      unused_mock_update_device_data):
    self.test.args = FakeArgs(method='GetVersion')  # type: ignore #TODO(b/338318729) Fixit!
    fake_result = [
        server_proxy.Fault(faultCode=0, faultString='fake_fault'), Exception, {
            'fake.key': 'fake.val'
        }
    ]
    mock_server = self.mock_get_server_proxy.return_value
    mock_server.GetVersion.side_effect = fake_result

    self.test.setUp()
    self.test.runTest()

    self.mock_logger.Log.assert_has_calls([
        mock.call('fake_fault', 'Server fault occurred: %s'),
        mock.call('fake_format_fault',
                  'Exception invoking shopfloor service: %s')
    ])
    mock_handle_error.assert_has_calls([
        mock.call(self.test, 'fake_fault', "{'GetVersion': []}"),
        mock.call(self.test, 'fake_format_fault', "{'GetVersion': []}")
    ])


if __name__ == '__main__':
  unittest.main()
