# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
# pylint: disable=useless-suppression

"""Connect to factory server to find software updates and upload logs.

Description
-----------
This test will create connections from DUT to Chrome OS factory server and
invoke remote procedure calls for syncing data and programs.

This test will sync following items:

1. If ``sync_time`` is enabled (default True), sync system time from server.
2. If ``sync_event_logs`` is enabled (default True), sync the ``event_log`` YAML
   event logs to factory server.
3. If ``flush_testlog`` is enabled (default False), flush TestLog to factory
   server (which should have Instalog node running).
4. If ``upload_report`` is enabled (default False), upload a ``Gooftool`` style
   report collecting system information and manufacturing logs to server.
5. If ``update_toolkit`` is enabled (default True), compare the factory software
   (toolkit) installed on DUT with the active version on server, and update
   if needed.
6. If ``upload_reg_codes`` is enabled (default False), upload the registration
   codes to server using ``UploadCSVEntry`` API, and have the data stored in
   ``registration_code_log.csv`` file on server. If the reg codes must be sent
   back to partner's shopfloor backend, please use shopfloor_service pytest
   and ActivateRegCode API instead.
7. If ``upload_zero_touch_ids`` is enabled (default False), upload the attested
   device ID and serial number pair using the ``UploadCSVEntry`` API.  The CSV
   can be downloaded from Dome server in the Logs -> CSV page.

Additionally, if argument ``server_url`` is specified, this test will update the
stored 'default factory server URL' so all following tests connecting to factory
server via ``server_proxy.GetServerProxy()`` will use the new URL.

``server_url`` supports few different input:

- If a string is given, that is interpreted as simple URL. For example,
  ``"http://10.3.0.11:8080/"``.
- If a mapping (dict) is given, take key as network IP/CIDR and value as URL.
  For example, ``{"10.3.0.0/24": "http://10.3.0.11:8080"}``

Test Procedure
--------------
Basically no user interaction required unless a toolkit update is found.

- Make sure network is connected.
- Start the test and it will try to reach factory server and sync time and logs.
- If `update_toolkit` is True, compare installed toolkit with server's active
  version.
- If a new version is found, a message like 'A software update is available.'
  will be displayed on screen. Operator can follow the instruction (usually
  just press space) to start downloading and installing new software.

Dependency
----------
Nothing special.
This test uses only server components in Chrome OS Factory Software.

Examples
--------
To connect to default server and sync time, event logs, and update software,
add this in test list::

  {
    "pytest_name": "sync_factory_server"
  }

To only sync time and logs, and never update software (useful for stations)::

  {
    "pytest_name": "sync_factory_server",
    "args": {
      "update_toolkit": false
    }
  }

To sync time and logs, and then upload a report::

  {
    "pytest_name": "sync_factory_server",
    "args": {
      "upload_report": true
    }
  }

To override default factory server URL for all tests, change the
``default_factory_server_url`` in test list constants::

  {
    "constants": {
      "default_factory_server_url": "http://192.168.3.11:8080"
    }
  }

It is also possible to override and create one test item using different factory
server URL, and all tests after that::

  {
    "pytest_name": "sync_factory_server",
    "args": {
      "server_url": "http://192.168.3.11:8080"
    }
  }

To implement "station specific factory server" in JSON test lists, extend
``SyncFactoryServer`` from ``generic_common.test_list.json`` as::

  { "inherit": "SyncFactoryServer",
    "args": {
      "server_url": "eval! locals.factory_server_url"
    }
  }

And then in each station (or stage), override URL in locals::

  {"SMT": {"locals": {"factory_server_url": "http://192.168.3.11:8080" }}},
  {"FAT": {"locals": {"factory_server_url": "http://10.3.0.11:8080" }}},
  {"RunIn": {"locals": {"factory_server_url": "http://10.1.2.10:7000" }}},
  {"FFT": {"locals": {"factory_server_url": "http://10.3.0.11:8080" }}},
  {"GRT": {"locals": {"factory_server_url": "http://172.30.1.2:8081" }}},

To implement "auto-detect factory server by received DHCP IP address", specify a
mapping object with key set to "IP/CIDR" and value set to server URL::

  {
    "constants": {
      "default_factory_server_url": {
        "192.168.3.0/24": "http://192.168.3.11:8080",
        "10.3.0.0/24": "http://10.3.0.11:8080",
        "10.1.0.0/16": "http://10.1.2.10:8080"
      }
    }
  }
"""

import datetime
import logging
import threading

from cros.factory.device import device_utils
from cros.factory.gooftool import commands
from cros.factory.goofy import updater
from cros.factory.test import device_data
from cros.factory.test.i18n import _
from cros.factory.test.rules import registration_codes
from cros.factory.test import server_proxy
from cros.factory.test import session
from cros.factory.test import state
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.test.utils import csv_utils
from cros.factory.test.utils import time_utils
from cros.factory.test.utils.url_spec import URLSpec
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import debug_utils
from cros.factory.utils import log_utils
from cros.factory.utils import sync_utils


ID_TEXT_INPUT_URL = 'text_input_url'
ID_BUTTON_EDIT_URL = 'button_edit_url'

EVENT_SET_URL = 'event_set_url'
EVENT_CANCEL_SET_URL = 'event_cancel_set_url'
EVENT_DO_SET_URL = 'event_do_set_url'


class Report:
  """A structure for reports uploaded to factory server."""

  def __init__(self, serial_number, blob, station):
    self.serial_number = serial_number
    self.blob = blob
    self.station = station


class SyncFactoryServer(test_case.TestCase):
  related_components = tuple()
  ARGS = [
      Arg(
          'first_retry_secs', int,
          'Time to wait after the first attempt; this will increase '
          'exponentially up to retry_secs.  This is useful because '
          'sometimes the network may not be available by the time the '
          'tests starts, but a full 10-second wait is unnecessary.', 1),
      Arg('retry_secs', int, 'Maximum time to wait between retries.', 10),
      Arg('timeout_secs', int, 'Timeout for XML/RPC operations.', 10),
      Arg('update_toolkit', bool, 'Whether to check factory update.',
          default=True),
      Arg('update_without_prompt', bool, 'Update without prompting when an '
          'update is available.', default=False),
      Arg('sync_time', bool, 'Sync system time from factory server.',
          default=True),
      Arg('sync_event_logs', bool, 'Sync event logs to factory server.',
          default=True),
      Arg(
          'flush_testlog',
          bool,
          'Flush test logs to factory server.',
          # TODO(hungte) Change flush_testlog to default True when Umpire is
          # officially deployed.
          default=False),
      Arg('upload_reg_codes', bool, 'Upload registration codes to server.',
          default=False),
      Arg('upload_sn', bool, 'Upload serial number for auditing.',
          default=False),
      Arg('upload_report', bool, 'Upload a factory report to factory server.',
          default=False),
      Arg('report_stage', str, 'Stage of report to upload.', default=None),
      Arg('report_serial_number_name', str,
          'Name of serial number to use for report file name to use.',
          default=None),
      Arg('server_url', (str, dict), 'Set and keep new factory server URL.',
          default=None),
      Arg('upload_zero_touch_ids', bool,
          'Upload attested_device_id and serial_number pair to server.',
          default=False),
      Arg('upload_csv_entries', bool,
          'Upload CSV entries recorded by `csv_utils.CSVManager`',
          default=True),
  ]

  def setUp(self):
    self.server = None
    self.do_setup_url = threading.Event()
    self.allow_edit_url = True
    self.event_url_set = threading.Event()
    self.goofy = state.GetInstance()
    self.report = None
    self.dut = device_utils.CreateDUTInterface()
    self.station = device_utils.CreateStationInterface()
    self.csv_entry_manager = csv_utils.CSVManager()

  def _GetHWID(self):
    hwid = device_data.GetDeviceData(device_data.KEY_HWID,
                                     self.dut.CallOutput('crossystem hwid'))
    if not hwid:
      raise Exception('Failed to find HWID.')
    return hwid

  @classmethod
  def CreateButton(cls, node_id, message, on_click):
    return [
        f'<button type="button" id="{node_id}" onclick={on_click!r}>', message,
        '</button>'
    ]

  def CreateChangeURLButton(self):
    return self.CreateButton(
        ID_BUTTON_EDIT_URL, _('Change URL'), f'this.disabled = true; '
        f'window.test.sendTestEvent("{EVENT_DO_SET_URL}");')

  def OnButtonSetClicked(self, event):
    self.ChangeServerURL(event.data)
    self.do_setup_url.clear()
    self.event_url_set.set()

  def OnButtonCancelClicked(self, event):
    del event  # Unused.
    self.do_setup_url.clear()
    self.event_url_set.set()

  def OnButtonEditClicked(self, event):
    del event  # Unused.
    self.do_setup_url.set()
    # yapf: disable
    self.ui.SetHTML(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        _('Please wait few seconds to edit...'), id=ID_BUTTON_EDIT_URL)

  def EditServerURL(self):
    current_url = server_proxy.GetServerURL() or ''

    if current_url:
      prompt = []
    else:
      prompt = [
          '<span class="warning_label">',
          _('No factor server URL configured.'),
          '</span><span class="warning_message">',
          # TODO(hungte) Add message when we can't connect to factory server.
          _('For debugging or development, '
            'enter engineering mode to start individual tests.'),
          '</span>'
      ]

    # yapf: disable
    self.ui.SetState([  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        prompt,
        _('Change server URL: '),
        f'<input type="text" id="{ID_TEXT_INPUT_URL}" value="{current_url}"/>',
        '<span>',
        SyncFactoryServer.CreateButton(
            'btnSet', _('Set'), f'window.test.sendTestEvent("{EVENT_SET_URL}", '
            f'document.getElementById("{ID_TEXT_INPUT_URL}").value)'),
        SyncFactoryServer.CreateButton(
            'btnCancel', _('Cancel'),
            f'window.test.sendTestEvent("{EVENT_CANCEL_SET_URL}")'), '</span>'
    ])

  def DetectServerURL(self):
    # yapf: disable
    expected_networks = list(self.args.server_url)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    label_connect = _('Please connect to network...')
    label_status = _('Expected network: {networks}', networks=expected_networks)

    while True:
      # yapf: disable
      new_url = URLSpec.FindServerURL(self.args.server_url, self.station)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      if new_url:
        break
      # Collect current networks. The output format is DEV STATUS NETWORK.
      output = self.station.CallOutput(['ip', '-f', 'inet', '-br', 'addr'])
      networks = [
          entry.split()[2] for entry in output.splitlines() if ' UP ' in entry
      ]
      # yapf: disable
      self.ui.SetState([  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          label_connect, label_status,
          _('Current networks: {networks}', networks=networks)
      ])
      self.Sleep(0.5)

    self.ChangeServerURL(new_url)
    self.do_setup_url.clear()

  def Ping(self):
    if self.do_setup_url.is_set():
      self.event_url_set.clear()
      self.EditServerURL()
      sync_utils.EventWait(self.event_url_set, enable_logging=False)

    # yapf: disable
    self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        [_('Trying to reach server...'),
         self.CreateChangeURLButton()])
    # yapf: disable
    self.server = server_proxy.GetServerProxy(timeout=self.args.timeout_secs,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
                                              expected_project='')
    # yapf: enable

    if self.do_setup_url.is_set():
      raise Exception('Edit URL clicked.')

    # yapf: disable
    self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        [_('Trying to check server protocol...'),
         self.CreateChangeURLButton()])
    self.server.Ping()
    self.allow_edit_url = False

  def ChangeServerURL(self, new_server_url):
    server_url = server_proxy.GetServerURL() or ''

    if new_server_url and new_server_url != server_url:
      server_proxy.SetServerURL(new_server_url.rstrip('/'))
      # Read again because server_proxy module may normalize it.
      new_server_url = server_proxy.GetServerURL()
      session.console.info(
          'Factory server URL has been changed from [%s] to [%s].',
          server_url, new_server_url)
      server_url = new_server_url

    # yapf: disable
    self.ui.SetInstruction(_('Server URL: {server_url}', server_url=server_url))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    if not server_url:
      self.do_setup_url.set()

  def FlushTestlog(self):
    # TODO(hungte) goofy.FlushTestlog should reload factory_server_url.
    result = False
    while not result:
      result, progress = self.goofy.FlushTestlog(timeout=2)
      # yapf: disable
      self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          _('Flush Test Log: Progress = <br>{progress}',
            progress=str(progress)))

  def CreateReport(self):
    # yapf: disable
    self.report = Report(None, None, self.args.report_stage) # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.ui.SetState(_('Collecting report data...'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    self.report.blob = commands.CreateReportArchiveBlob()
    self.ui.SetState(_('Getting serial number...'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.report.serial_number = device_data.GetSerialNumber(
        # yapf: disable
        self.args.report_serial_number_name or  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        device_data.NAME_SERIAL_NUMBER)

  def UploadReport(self):
    # yapf: disable
    self.server.UploadReport( # type: ignore #TODO(b/338318729) Fixit!
        self.report.serial_number, self.report.blob, None, self.report.station) # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def UploadRegCodes(self):
    """Uploads registration codes to factory server.

    The registration codes should be sent in format from http://goto/nkjyr.
    """
    hwid = self._GetHWID()

    board = hwid.partition(' ')[0]
    ubind = device_data.GetDeviceData(device_data.KEY_VPD_USER_REGCODE)
    gbind = device_data.GetDeviceData(device_data.KEY_VPD_GROUP_REGCODE)
    for label, value in ('user', ubind), ('group', gbind):
      if not value:
        raise Exception(
            f'Missing {label} registration codes in device data ({value!r}).')

    registration_codes.CheckRegistrationCode(ubind)
    registration_codes.CheckRegistrationCode(gbind)
    timestamp = time_utils.Now(
        datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    entry = [board, ubind, gbind, timestamp, hwid]
    self.csv_entry_manager.Append('registration_code_log', entry)

  def UploadSerialNumberForAuditing(self):
    hwid = self._GetHWID()
    serial_number = device_data.GetSerialNumber()
    if not serial_number:
      raise Exception('Failed to find serial number.')
    assert isinstance(hwid, str)
    assert isinstance(serial_number, str)

    now = time_utils.Now()
    timestamp = now.astimezone().replace(microsecond=0).isoformat()
    entry = [serial_number, hwid, timestamp]

    csv_filename = f'sn-report-{now.strftime("%Y-%m-%d")}'
    # yapf: disable
    self.server.UploadCSVEntry(csv_filename, entry)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def UploadZeroTouchIds(self):
    """Uploads identifiers for zero touch enrollment.

    The identifiers will be sent in format (serial_number, attested_device_id).
    The CSV file can be downloaded from Dome server (Logs -> CSV).
    """
    attested_device_id = device_data.GetDeviceData(
        device_data.JoinKeys(device_data.KEY_VPD_RO, 'attested_device_id'))
    serial_number = device_data.GetSerialNumber()
    if not attested_device_id:
      raise Exception('attested_device_id is not set.')
    if not serial_number:
      raise Exception('serial_number is not set.')
    entry = [serial_number, attested_device_id]
    self.csv_entry_manager.Append('zero_touch_ids', entry)

  def UploadCSVEntries(self):
    self.csv_entry_manager.UploadAll(self.server)

  def UpdateToolkit(self):
    unused_toolkit_version, has_update = updater.CheckForUpdate(
        # yapf: disable
        self.args.timeout_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    if not has_update:
      return

    # Update necessary. Note that updateFactory() will kill this test.
    # yapf: disable
    if not self.args.update_without_prompt:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # Display message and require update.
      # yapf: disable
      self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
          _('A software update is available. Press SPACE to update.'))
      # yapf: disable
      self.ui.WaitKeysOnce(test_ui.SPACE_KEY)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # yapf: disable
    self.ui.CallJSFunction('window.test.updateFactory')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # Let this test sleep forever, and wait for either the SPACE event, or the
    # factory update to complete. Note that we want the test to neither pass or
    # fail, so we won't be accidentally running other tests when the
    # updateFactory is running.
    self.WaitTaskEnd()

  def SyncTime(self):
    if not time_utils.SyncTimeWithFactoryServer():
      raise Exception('Failed to sync time with factory server')

  def FlushEventLogs(self):
    self.goofy.FlushEventLogs()

  def GetTasks(self):
    # Setup tasks to perform.
    tasks = [(_('Ping'), self.Ping)]

    # yapf: disable
    if isinstance(self.args.server_url, dict) and self.args.server_url:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # Server URL must be confirmed before Ping.
      tasks = [(_('Detect Server URL'), self.DetectServerURL)] + tasks

    # yapf: disable
    if self.args.sync_time:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Sync time'), self.SyncTime)]

    # yapf: disable
    if self.args.sync_event_logs:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Flush Event Logs'), self.FlushEventLogs)]

    # yapf: disable
    if self.args.flush_testlog:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Flush Test Log'), self.FlushTestlog)]

    # yapf: disable
    if self.args.upload_report:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Create Report'), self.CreateReport)]
      tasks += [(_('Upload report'), self.UploadReport)]

    # yapf: disable
    if self.args.upload_reg_codes:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Upload Reg Codes'), self.UploadRegCodes)]

    # yapf: disable
    if self.args.upload_sn:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Upload Serial Number for auditing'),
                 self.UploadSerialNumberForAuditing)]

    # yapf: disable
    if self.args.upload_zero_touch_ids:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Upload Zero Touch Ids'), self.UploadZeroTouchIds)]

    upload_csv_entries = any({
        # yapf: disable
        self.args.upload_csv_entries,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        self.args.upload_reg_codes,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        self.args.upload_zero_touch_ids,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
    })
    if upload_csv_entries:
      tasks += [(_('Upload CSV Entries'), self.UploadCSVEntries)]

    # yapf: disable
    if self.args.update_toolkit:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      tasks += [(_('Update Toolkit'), self.UpdateToolkit)]
    else:
      session.console.info('Toolkit update is disabled.')

    return tasks

  def ProcessTasks(self):
    # It's very often that a DUT under FA is left without network connected for
    # hours to days, so we should not log (which will increase TestLog events)
    # if the exception string is not changed.
    logger = log_utils.NoisyLogger(
        lambda fault, prompt: logging.exception(prompt, fault))

    tasks = self.GetTasks()
    # yapf: disable
    self.ui.DrawProgressBar(len(tasks))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    retry_secs = self.args.first_retry_secs  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    for label, task in tasks:
      logging.info('Waiting for retrying task: %s.', label['en-US'])
      while True:
        try:
          logging.info('Running task: %s.', label['en-US'])
          # yapf: disable
          self.ui.SetState(_('Running task: {label}', label=label))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          task()
          logging.info('Server task finished: %s.', label['en-US'])
          # yapf: disable
          self.ui.SetState([  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
              '<span style="color: green">',
              _('Server Task Finished: {label}', label=label), '</span>'
          ])
          self.Sleep(0.5)
          break
        except server_proxy.Fault as f:
          message = f.faultString
          logger.Log(message, 'Server fault with message: %s')
        except Exception:
          message = debug_utils.FormatExceptionOnly()
          logger.Log(message, 'Unable to sync with server: %s')

        msg = lambda time_left, label_: _(
            'Task <b>{label}</b> failed, retry in {time_left} seconds...',
            time_left=time_left,
            label=label_)
        edit_url_button = (['<p>', self.CreateChangeURLButton(), '</p>']
                           if self.allow_edit_url else '')
        # yapf: disable
        self.ui.SetState([  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
            '<span id="retry">',
            msg(retry_secs, label), '</span>', edit_url_button,
            '<p><textarea rows=25 cols=90 readonly class="sync-detail">',
            test_ui.Escape(message, False), '</textarea>'
        ])

        try:
          # sync_utils.EventWait() may log timeout message every second, so we
          # disable logging.INFO temporarily.
          logging.disable(logging.INFO)
          for sec in range(retry_secs):
            if sync_utils.EventWait(self.do_setup_url, timeout=1,
                        enable_logging=False):
              break
            # yapf: disable
            self.ui.SetHTML(msg(retry_secs - sec - 1, label), id='retry')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
            # yapf: enable
        finally:
          logging.disable(logging.NOTSET)
        # yapf: disable
        retry_secs = min(2 * retry_secs, self.args.retry_secs)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable

      # yapf: disable
      self.ui.AdvanceProgress()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

  def runTest(self):
    # yapf: disable
    self.ui.SetInstruction(_('Preparing...'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # yapf: disable
    self.event_loop.AddEventHandler(EVENT_SET_URL, self.OnButtonSetClicked)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.event_loop.AddEventHandler(EVENT_CANCEL_SET_URL,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                                    self.OnButtonCancelClicked)
    # yapf: disable
    self.event_loop.AddEventHandler(EVENT_DO_SET_URL, self.OnButtonEditClicked)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # Setup new server URL
    server_proxy.ValidateServerConfig()
    self.ChangeServerURL(
        # yapf: disable
        URLSpec.FindServerURL(self.args.server_url, self.station))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.ProcessTasks()
