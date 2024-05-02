#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
# type: ignore

import datetime
import logging
import unittest
from unittest import mock

from cros.factory.test.pytests import sync_factory_server
from cros.factory.test import test_ui
from cros.factory.utils import type_utils


class FakeArgs:

  def __init__(self, **kwargs):
    self.first_retry_secs = 1
    self.retry_secs = 10
    self.timeout_secs = 10
    self.update_toolkit = False
    self.update_without_prompt = False
    self.sync_time = False
    self.sync_event_logs = False
    self.flush_testlog = False
    self.upload_reg_codes = False
    self.upload_sn = False
    self.upload_report = False
    self.report_stage = None
    self.report_serial_number_name = None
    self.server_url = None
    self.upload_zero_touch_ids = False
    self.upload_csv_entries = False
    for k, v in kwargs.items():
      setattr(self, k, v)


class FakeEvent:

  def __init__(self, data=''):
    self.data = data


def i18n(text):
  return {
      'en-US': text
  }


class SyncFactoryServerUnitTest(unittest.TestCase):

  def setUp(self):
    self.test = sync_factory_server.SyncFactoryServer()
    self.test.args = FakeArgs()
    logging.disable()
    self.ui = mock.create_autospec(test_ui.StandardUI)
    type_utils.LazyProperty.Override(self.test, 'ui', self.ui)
    self.test.event_loop = mock.Mock()
    self.exe_count = 0
    patcher = mock.patch.object(sync_factory_server.state, 'GetInstance',
                                autospec=True)
    self.goofy = patcher.start().return_value
    patcher = mock.patch.object(sync_factory_server.csv_utils, 'CSVManager',
                                autospec=True)
    self.csv_manager = patcher.start().return_value
    patcher = mock.patch.object(sync_factory_server.device_utils,
                                'CreateDUTInterface', autospec=True)
    self.dut = patcher.start().return_value
    self.url = ''
    patcher = mock.patch.object(sync_factory_server.server_proxy,
                                'SetServerURL', autospec=True)
    patcher.start().side_effect = self._set_server_url_side_effect
    patcher = mock.patch.object(sync_factory_server.server_proxy,
                                'GetServerURL', autospec=True)
    patcher.start().side_effect = self._get_server_url_side_effect
    self.server = mock.Mock()
    self.addCleanup(mock.patch.stopall)
    self.test.setUp()
    self.test.server = self.server

  def _set_server_url_side_effect(self, url):
    self.url = url

  def _get_server_url_side_effect(self):
    return self.url

  def testGetTasks_minimalTasks(self):
    self.test.args = FakeArgs(
        sync_time=False, sync_event_logs=False, flush_testlog=False,
        upload_reg_codes=False, upload_report=False, upload_sn=False,
        upload_zero_touch_ids=False, upload_csv_entries=False,
        update_toolkit=False, server_url=None)

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping)], tasks)

  def testGetTasks_DictUrl(self):
    self.test.args.server_url = {
        'default': 'url'
    }

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Detect Server URL'), self.test.DetectServerURL),
                      (i18n('Ping'), self.test.Ping)], tasks)

  def testGetTasks_SyncTime(self):
    self.test.args.sync_time = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Sync time'), self.test.SyncTime)], tasks)

  def testGetTasks_SyncEventLogs(self):
    self.test.args.sync_event_logs = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Flush Event Logs'), self.test.FlushEventLogs)],
                     tasks)

  def testGetTasks_FlushTestLog(self):
    self.test.args.flush_testlog = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Flush Test Log'), self.test.FlushTestlog)], tasks)

  def testGetTasks_UploadRegCodes(self):
    self.test.args.upload_reg_codes = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Upload Reg Codes'), self.test.UploadRegCodes),
                      (i18n('Upload CSV Entries'), self.test.UploadCSVEntries)],
                     tasks)

  def testGetTasks_UploadReport(self):
    self.test.args.upload_report = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Create Report'), self.test.CreateReport),
                      (i18n('Upload report'), self.test.UploadReport)], tasks)

  def testGetTasks_UploadSn(self):
    self.test.args.upload_sn = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Upload Serial Number for auditing'),
                       self.test.UploadSerialNumberForAuditing)], tasks)

  def testGetTasks_UploadZeroTouchIds(self):
    self.test.args.upload_zero_touch_ids = True

    tasks = self.test.GetTasks()

    self.assertEqual(
        [(i18n('Ping'), self.test.Ping),
         (i18n('Upload Zero Touch Ids'), self.test.UploadZeroTouchIds),
         (i18n('Upload CSV Entries'), self.test.UploadCSVEntries)], tasks)

  def testGetTasks_UploadCsvEntries(self):
    self.test.args.upload_csv_entries = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Upload CSV Entries'), self.test.UploadCSVEntries)],
                     tasks)

  def testGetTasks_UpdateToolkit(self):
    self.test.args.update_toolkit = True

    tasks = self.test.GetTasks()

    self.assertEqual([(i18n('Ping'), self.test.Ping),
                      (i18n('Update Toolkit'), self.test.UpdateToolkit)], tasks)

  @mock.patch.object(sync_factory_server.SyncFactoryServer, 'GetTasks',
                     autospec=True)
  def testProcessTasks_Success(self, mock_tasks):

    def fakeFunction():
      self.exe_count += 1

    mock_tasks.return_value = [(i18n("fake"), fakeFunction)]
    self.exe_count = 0

    self.test.ProcessTasks()

    self.ui.DrawProgressBar.assert_called_with(1)
    self.ui.SetState.assert_has_calls([
        mock.call(i18n('Running task: fake')),
        mock.call([
            '<span style="color: green">',
            i18n('Server Task Finished: fake'), '</span>'
        ])
    ])
    self.ui.AdvanceProgress.assert_called_once()
    self.assertEqual(self.exe_count, 1)

  @mock.patch.object(sync_factory_server.test_case.TestCase, 'Sleep',
                     autospec=True)
  @mock.patch.object(sync_factory_server.sync_utils, 'EventWait', autospec=True)
  @mock.patch.object(sync_factory_server.SyncFactoryServer, 'GetTasks',
                     autospec=True)
  def testProcessTasks_Retry(self, mock_tasks, mock_wait, mock_sleep):
    del mock_sleep  # unused

    def RetryButton(sec):
      return [
          '<span id="retry">',
          i18n(f'Task <b>fake</b> failed, retry in {sec} seconds...'),
          '</span>',
          [
              '<p>',
              [
                  '<button type="button" id="button_edit_url" onclick='
                  '\'this.disabled = true; '
                  'window.test.sendTestEvent("event_do_set_url");\'>',
                  i18n('Change URL'), '</button>'
              ], '</p>'
          ], '<p><textarea rows=25 cols=90 readonly class="sync-detail">',
          'Exception: Need retry', '</textarea>'
      ]

    def RetryMessage(sec):
      return {
          'en-US': f'Task <b>fake</b> failed, retry in {sec} seconds...'
      }

    def FakeFunction():
      self.exe_count += 1
      if self.exe_count < 5:
        raise Exception('Need retry')

    self.test.args.first_retry_secs = 2
    self.test.args.retry_secs = 10
    mock_tasks.return_value = [(i18n("fake"), FakeFunction)]
    mock_wait.return_value = False
    self.exe_count = 0

    self.test.ProcessTasks()

    self.ui.DrawProgressBar.assert_called_with(1)
    self.ui.SetState.assert_has_calls([
        mock.call(i18n('Running task: fake')),
        mock.call(RetryButton(2)),
        mock.call(i18n('Running task: fake')),
        mock.call(RetryButton(4)),
        mock.call(i18n('Running task: fake')),
        mock.call(RetryButton(8)),
        mock.call(i18n('Running task: fake')),
        mock.call(RetryButton(10)),
        mock.call(i18n('Running task: fake')),
        mock.call([
            '<span style="color: green">',
            i18n('Server Task Finished: fake'), '</span>'
        ])
    ])
    mock_wait.assert_has_calls(
        [mock.call(self.test.do_setup_url, timeout=1)] * (2 + 4 + 8 + 10))
    self.ui.AdvanceProgress.assert_called_once()
    self.ui.SetHTML.assert_has_calls(
        [mock.call(RetryMessage(i), id='retry') for i in reversed(range(2))] +
        [mock.call(RetryMessage(i), id='retry') for i in reversed(range(4))] +
        [mock.call(RetryMessage(i), id='retry') for i in reversed(range(8))] +
        [mock.call(RetryMessage(i), id='retry') for i in reversed(range(10))])
    self.assertEqual(self.exe_count, 5)

  @mock.patch.object(sync_factory_server.server_proxy, 'ValidateServerConfig',
                     autospec=True)
  @mock.patch.object(sync_factory_server.URLSpec, 'FindServerURL',
                     autospec=True)
  def testRunTest(self, mock_find_url, mock_validate_config):
    self.test.args = FakeArgs(server_url='url')

    with mock.patch.multiple(
        self.test,
        autospec=True,
        ChangeServerURL=mock.DEFAULT,
        ProcessTasks=mock.DEFAULT,
    ) as mock_methods:
      self.test.runTest()

      self.ui.SetInstruction.assert_called_with(i18n('Preparing...'))
      self.test.event_loop.AddEventHandler.assert_has_calls([
          mock.call('event_set_url', self.test.OnButtonSetClicked),
          mock.call('event_cancel_set_url', self.test.OnButtonCancelClicked),
          mock.call('event_do_set_url', self.test.OnButtonEditClicked)
      ])
      mock_validate_config.assert_called_once()
      mock_find_url.assert_called_once_with('url', self.test.station)
      mock_methods['ChangeServerURL'].assert_called_once_with(
          mock_find_url.return_value)
      mock_methods['ProcessTasks'].assert_called_once()

  def testChangeServerURL(self):
    self.url = ''  # The mocked value of server_proxy.GetServerURL.
    self.test.ChangeServerURL('new_url/')

    self.ui.SetInstruction.assert_called_with(i18n('Server URL: new_url'))
    self.assertEqual(self.url, 'new_url')

  def testChangeServerURLNoURL(self):
    self.test.ChangeServerURL('')

    self.assertTrue(self.test.do_setup_url.is_set())

  def testOnButtonSetClicked(self):
    with mock.patch.object(sync_factory_server.SyncFactoryServer,
                           'ChangeServerURL', autospec=True) as mock_change_url:
      self.test.OnButtonSetClicked(FakeEvent('url'))

      self.assertTrue(self.test.event_url_set.is_set())
      self.assertFalse(self.test.do_setup_url.is_set())
      mock_change_url.assert_called_with(self.test, 'url')

  def testOnButtonCancelClicked(self):
    self.test.OnButtonCancelClicked(FakeEvent())

    self.assertTrue(self.test.event_url_set.is_set())
    self.assertFalse(self.test.do_setup_url.is_set())

  def testOnButtonEditClicked(self):
    self.test.OnButtonEditClicked(FakeEvent())

    self.assertTrue(self.test.do_setup_url.is_set())
    self.ui.SetHTML.assert_called_with(
        i18n('Please wait few seconds to edit...'), id='button_edit_url')

  @mock.patch.object(sync_factory_server.updater, 'CheckForUpdate',
                     autospec=True)
  def testUpdateToolkit(self, mock_update):
    self.test.args = FakeArgs(timeout_secs=123, update_without_prompt=False)
    mock_update.return_value = (None, True)

    with mock.patch.object(self.test, 'WaitTaskEnd',
                           autospec=True) as mock_wait:
      self.test.UpdateToolkit()

      mock_update.assert_called_with(123)
      self.ui.SetState.assert_called_with(
          i18n('A software update is available. Press SPACE to update.'))
      self.ui.WaitKeysOnce.assert_called_with(' ')
      self.ui.CallJSFunction.assert_called_with('window.test.updateFactory')
      mock_wait.assert_called_once()

  @mock.patch.object(sync_factory_server.updater, 'CheckForUpdate',
                     autospec=True)
  def testUpdateToolkitNoUpdate(self, mock_update):
    self.test.args = FakeArgs(timeout_secs=123, update_without_prompt=False)
    mock_update.return_value = (None, False)

    self.test.UpdateToolkit()

    self.ui.CallJSFunction.assert_not_called()

  def testUploadCSVEntries(self):
    self.test.server = self.server

    self.test.UploadCSVEntries()

    self.csv_manager.UploadAll.assert_called_with(self.server)

  @mock.patch.object(sync_factory_server.device_data, 'GetDeviceData',
                     autospec=True)
  @mock.patch.object(sync_factory_server.device_data, 'GetSerialNumber',
                     autospec=True)
  def testUploadZeroTouchIds(self, mock_sn, mock_get_data):
    mock_get_data.return_value = 'attested_id'
    mock_sn.return_value = 'sn'

    self.test.UploadZeroTouchIds()

    self.csv_manager.Append.assert_called_with('zero_touch_ids',
                                               ['sn', 'attested_id'])
    mock_get_data.assert_called_with('vpd.ro.attested_device_id')

  @mock.patch.object(sync_factory_server.device_data, 'GetDeviceData',
                     autospec=True)
  @mock.patch.object(sync_factory_server.device_data, 'GetSerialNumber',
                     autospec=True)
  def testUploadZeroTouchIds_NoSn(self, mock_sn, mock_get_data):
    mock_get_data.return_value = 'id'
    mock_sn.return_value = None

    self.assertRaisesRegex(Exception, 'serial_number is not set',
                           self.test.UploadZeroTouchIds)

  @mock.patch.object(sync_factory_server.device_data, 'GetDeviceData',
                     autospec=True)
  @mock.patch.object(sync_factory_server.device_data, 'GetSerialNumber',
                     autospec=True)
  def testUploadZeroTouchIds_NoAttestedId(self, mock_sn, mock_get_data):
    mock_sn.return_value = 'sn'
    mock_get_data.return_value = None

    self.assertRaisesRegex(Exception, 'attested_device_id is not set',
                           self.test.UploadZeroTouchIds)

  def testDetectServerURL(self):
    self.test.args = FakeArgs(server_url={
        'default': 'url',
        'abc': '123'
    })

    self.test.DetectServerURL()

    self.assertFalse(self.test.do_setup_url.is_set())
    self.ui.SetInstruction.assert_called_with(i18n('Server URL: url'))

  @mock.patch.object(sync_factory_server.device_data, 'GetDeviceData',
                     autospec=True)
  @mock.patch.object(sync_factory_server.device_data, 'GetSerialNumber',
                     autospec=True)
  def testUploadSerialNumberForAuditing_NoSn(self, mock_sn, mock_get_data):
    self.test.setUp()
    mock_get_data.return_value = 'id'
    mock_sn.return_value = None

    self.assertRaisesRegex(Exception, 'Failed to find serial number',
                           self.test.UploadSerialNumberForAuditing)

  @mock.patch.object(sync_factory_server.commands, 'CreateReportArchiveBlob',
                     autospec=True)
  @mock.patch.object(sync_factory_server.device_data, 'GetSerialNumber',
                     autospec=True)
  def testCreateAndUploadReport(self, mock_sn, mock_blob):
    self.test.args = FakeArgs(report_stage='station',
                              report_serial_number_name='sn')
    blob = mock.Mock()
    mock_blob.return_value = blob
    mock_sn.return_value = '123'

    self.test.CreateReport()
    self.test.UploadReport()

    self.ui.SetState.assert_has_calls([
        mock.call(i18n('Collecting report data...')),
        mock.call(i18n('Getting serial number...'))
    ])
    mock_sn.assert_called_with('sn')
    self.server.UploadReport.assert_called_with('123', blob, None, 'station')

  @mock.patch.object(sync_factory_server.commands, 'CreateReportArchiveBlob',
                     autospec=True)
  @mock.patch.object(sync_factory_server.device_data, 'GetSerialNumber',
                     autospec=True)
  def testCreateAndUploadReport_DefaultSnName(self, mock_sn, mock_blob):
    del mock_blob  # unused

    self.test.CreateReport()
    self.test.UploadReport()

    mock_sn.assert_called_with('serial_number')

  @mock.patch.object(sync_factory_server.time_utils, 'Now', autospec=True)
  @mock.patch.object(sync_factory_server.registration_codes,
                     'CheckRegistrationCode', autospec=True)
  @mock.patch.object(sync_factory_server.device_data, 'GetDeviceData',
                     autospec=True)
  def testUploadRegCodes(self, mock_get_data, mock_check_regcode, mock_now):
    mock_get_data.side_effect = ['board hwid', 'ubind', 'gbind']
    mock_now.return_value = datetime.datetime(2024, 1, 2, 3, 4, 5)

    self.test.UploadRegCodes()

    self.csv_manager.Append.assert_called_with(
        'registration_code_log',
        ['board', 'ubind', 'gbind', '2024-01-02 03:04:05', 'board hwid'])
    mock_check_regcode.assert_has_calls(
        [mock.call('ubind'), mock.call('gbind')])
    mock_get_data.assert_has_calls([
        mock.call('hwid', self.dut.CallOutput.return_value),
        mock.call('vpd.rw.ubind_attribute'),
        mock.call('vpd.rw.gbind_attribute')
    ])
    mock_now.assert_called_with(sync_factory_server.datetime.timezone.utc)

  def testFlushTestlog(self):
    self.test.setUp()
    self.goofy.FlushTestlog.side_effect = [(False, 'progress1'),
                                           (True, 'progress2')]

    self.test.FlushTestlog()

    self.goofy.FlushTestlog.assert_has_calls([mock.call(timeout=2)] * 2)
    self.ui.SetState.assert_has_calls([
        mock.call(i18n('Flush Test Log: Progress = <br>progress1')),
        mock.call(i18n('Flush Test Log: Progress = <br>progress2'))
    ])

  def testFlushEventLogs(self):
    self.test.setUp()

    self.test.FlushEventLogs()

    self.goofy.FlushEventLogs.assert_called_once()

  @mock.patch.object(sync_factory_server.time_utils,
                     'SyncTimeWithFactoryServer', autospec=True)
  def testSyncTime(self, mock_sync):
    self.test.setUp()

    self.test.SyncTime()

    mock_sync.assert_has_calls([mock.call(), mock.call().__bool__])

  @mock.patch.object(sync_factory_server.server_proxy, 'GetServerProxy',
                     autospec=True)
  def testPing(self, mock_get_server_proxy):
    self.test.server = None
    self.test.allow_edit_url = True

    self.test.Ping()

    button = [
        '<button type="button" id="button_edit_url" onclick=\'this.disabled = '
        'true; window.test.sendTestEvent("event_do_set_url");\'>',
        i18n('Change URL'), '</button>'
    ]
    self.ui.SetState.assert_has_calls([
        mock.call([i18n('Trying to reach server...'), button]),
        mock.call([i18n('Trying to check server protocol...'), button])
    ])
    mock_get_server_proxy.return_value.Ping.assert_called_once()
    self.assertEqual(self.test.server, mock_get_server_proxy.return_value)
    self.assertFalse(self.test.allow_edit_url)

  @mock.patch.object(sync_factory_server.sync_utils, 'EventWait', autospec=True)
  @mock.patch.object(sync_factory_server.server_proxy, 'GetServerProxy',
                     autospec=True)
  def testPing_SetupUrl(self, mock_get_server_proxy, mock_wait):

    def EventWaitSideEffect(e):
      del e
      self.test.do_setup_url.clear()

    self.test.server = None
    self.test.allow_edit_url = True
    self.test.do_setup_url.set()
    mock_wait.side_effect = EventWaitSideEffect

    self.test.Ping()

    button = [
        '<button type="button" id="button_edit_url" onclick=\'this.disabled = '
        'true; window.test.sendTestEvent("event_do_set_url");\'>',
        i18n('Change URL'), '</button>'
    ]
    self.ui.SetState.assert_has_calls([
        mock.call([[
            '<span class="warning_label">',
            i18n('No factor server URL configured.'),
            '</span><span class="warning_message">',
            i18n('For debugging or development, '
                 'enter engineering mode to start individual tests.'), '</span>'
        ],
                   i18n('Change server URL: '),
                   '<input type="text" id="text_input_url" value=""/>',
                   '<span>',
                   [
                       '<button type="button" id="btnSet" onclick='
                       '\'window.test.sendTestEvent("event_set_url", '
                       'document.getElementById("text_input_url").value)\'>',
                       i18n('Set'), '</button>'
                   ],
                   [
                       '<button type="button" id="btnCancel" onclick='
                       '\'window.test.sendTestEvent("event_cancel_set_url")\'>',
                       i18n('Cancel'), '</button>'
                   ], '</span>']),
        mock.call([i18n('Trying to reach server...'), button]),
        mock.call([i18n('Trying to check server protocol...'), button])
    ])
    mock_get_server_proxy.return_value.Ping.assert_called_once()
    self.assertEqual(self.test.server, mock_get_server_proxy.return_value)
    self.assertFalse(self.test.allow_edit_url)


if __name__ == '__main__':
  unittest.main()
