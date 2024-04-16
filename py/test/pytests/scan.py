# Copyright 2014 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Prompts the operator to input a string of data.

Description
-----------
This test asks the operator to scan or type a string, usually
for provisioning manufacturing info like device serial number
or operator's ID.

Test Procedure
--------------
1. A prompt message will be displayed on the UI.
2. Operator enters a string using a barcode scanner, or by
   typing on keyboard.

Dependency
----------
If `bft_fixture` is specified, the ScanBarcode and related functions
must be implemented to provide scanned data.

Examples
--------
To ask the operator to scan the MLB serial number, add this in test list::

  {
    "pytest_name": "scan",
    "args": {
      "device_data_key": "serials.mlb_serial_number",
      "label": "MLB Serial Number"
    }
  }


A regular expression can also be specified to check the validity::

  {
    "pytest_name": "scan",
    "args": {
      "regexp": ".+",
      "device_data_key": "serials.mlb_serial_number",
      "label": "MLB Serial Number"
    }
  }
"""

import logging
import re
from typing import List, Optional, Tuple, cast

from cros.factory.device import device_utils
from cros.factory.test import device_data
from cros.factory.test import event as test_event
from cros.factory.test import event_log  # TODO(chuntsen): Deprecate event log.
from cros.factory.test.fixture import bft_fixture
from cros.factory.test.i18n import _
from cros.factory.test.i18n import arg_utils as i18n_arg_utils
from cros.factory.test import state
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import debug_utils


class Scan(test_case.TestCase):
  """The main class for this pytest."""
  related_components = (test_case.TestCategory.VPD, )

  ARGS = [
      i18n_arg_utils.I18nArg(
          'label', 'Name of the ID or serial number being scanned, '
          'e.g., "MLB serial number"'),
      Arg('event_log_key', str, 'Key to use for event log',
          default=None),
      Arg('testlog_key', str, 'Parameter key to use for testlog',
          default=None),
      Arg('shared_data_key', str,
          'Key to use to store in scanned value in shared data',
          default=None),
      Arg('serial_number_key', str,
          'Key to use to store in scanned value in serial numbers',
          default=None),
      Arg('device_data_key', str,
          'Key to use to store in scanned value in device data',
          default=None),
      Arg('dut_data_key', str,
          'Key to use to store in scanned value in DUT.',
          default=None),
      Arg('ro_vpd_key', str,
          'Key to use to store in scanned value in RO VPD',
          default=None),
      Arg('rw_vpd_key', str,
          'Key to use to store in scanned value in RW VPD',
          default=None),
      Arg('save_path', str, 'The file path of saving scanned value',
          default=None),
      Arg('regexp', str, 'Regexp that the scanned value must match',
          default=None),
      Arg('check_device_data_key', str,
          'Checks that the given value in device data matches the scanned '
          'value',
          default=None),
      Arg('bft_scan_fixture_id', bool, 'True to scan BFT fixture ID.',
          default=False),
      Arg('bft_scan_barcode', bool, 'True to trigger BFT barcode scanner.',
          default=False),
      Arg('bft_save_barcode', bool,
          'True to trigger BFT barcode scanner and save in BFT.',
          default=False),
      Arg('bft_get_barcode', (bool, str),
          'True to get barcode from BFT. BFT stores barcode in advance so this '
          'obtains barcode immidiately. If a string is given, will override '
          'default path (`nuc_dut_serial_path`)', default=False),
      Arg('bft_fixture', dict, bft_fixture.TEST_ARG_HELP,
          default=None),
      Arg('barcode_scan_interval_secs', (int, float),
          "Interval for repeatedly trigger BFT's barcode scaner",
          default=2.0),
      Arg('match_the_last_few_chars', int,
          'This is for OP to manually input last few SN chars based on the '
          'sticker on machine to make sure SN in VPD matches sticker SN.',
          default=0),
      Arg('ignore_case', bool, 'True to ignore case from input.',
          default=False),
      Arg('value_assigned', str,
          'If not None, use the value to fill the key.',
          default=None)
  ]

  def HandleScanValue(self, event):
    def SetError(label):
      logging.info('Scan error: %r', label['en-US'])
      self.ui.SetHTML(  # type: ignore #TODO(b/338318729) Fixit!
          ['<span class="test-error">', label, '</span>'], id='scan-status')
      self.ui.RunJS('document.getElementById("scan-value").disabled = false;'  # type: ignore #TODO(b/338318729) Fixit!
                    'document.getElementById("scan-value").value = ""')
      self.ui.SetFocus('scan-value')  # type: ignore #TODO(b/338318729) Fixit!

    self.ui.RunJS('document.getElementById("scan-value").disabled = true')  # type: ignore #TODO(b/338318729) Fixit!
    scan_value = event.data.strip()
    if self.args.ignore_case:  # type: ignore #TODO(b/338318729) Fixit!
      scan_value = scan_value.upper()
    esc_scan_value = test_ui.Escape(scan_value)
    if not scan_value:
      SetError(_('The scanned value is empty.'))
      return
    if self.args.regexp:  # type: ignore #TODO(b/338318729) Fixit!
      match = re.match(self.args.regexp, scan_value)  # type: ignore #TODO(b/338318729) Fixit!
      if not match or match.group(0) != scan_value:
        SetError(
            _('The scanned value "{value}" does not match the expected format.',
              value=esc_scan_value))
        return

    if self.args.event_log_key:  # type: ignore #TODO(b/338318729) Fixit!
      event_log.Log('scan', key=self.args.event_log_key, value=scan_value)  # type: ignore #TODO(b/338318729) Fixit!
      testlog.LogParam(self.args.event_log_key, scan_value)  # type: ignore #TODO(b/338318729) Fixit!
    elif self.args.testlog_key:  # type: ignore #TODO(b/338318729) Fixit!
      event_log.Log('scan', key=self.args.testlog_key, value=scan_value)  # type: ignore #TODO(b/338318729) Fixit!
      testlog.LogParam(self.args.testlog_key, scan_value)  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.shared_data_key:  # type: ignore #TODO(b/338318729) Fixit!
      state.DataShelfSetValue(self.args.shared_data_key, scan_value)  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.serial_number_key:  # type: ignore #TODO(b/338318729) Fixit!
      device_data.SetSerialNumber(self.args.serial_number_key, scan_value)  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.device_data_key:  # type: ignore #TODO(b/338318729) Fixit!
      device_data.UpdateDeviceData({self.args.device_data_key: scan_value})  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.dut_data_key:  # type: ignore #TODO(b/338318729) Fixit!
      self.dut.storage.UpdateDict({self.args.dut_data_key: scan_value})  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.check_device_data_key:  # type: ignore #TODO(b/338318729) Fixit!
      expected_value = device_data.GetDeviceData(
          self.args.check_device_data_key, None)  # type: ignore #TODO(b/338318729) Fixit!

      if self.args.match_the_last_few_chars != 0:  # type: ignore #TODO(b/338318729) Fixit!
        expected_value = expected_value[-self.args.match_the_last_few_chars:]  # type: ignore #TODO(b/338318729) Fixit!

      if expected_value != scan_value:
        logging.error('Expected %r but got %r', expected_value, scan_value)

        # Show expected value only in engineering mode, so the user
        # can't fake it.
        esc_expected_value = test_ui.Escape(expected_value or 'None')
        SetError(
            _('The scanned value "{value}" does not match '
              'the expected value <span class=test-engineering-mode-only>'
              '"{expected_value}"</span>.',
              value=esc_scan_value,
              expected_value=esc_expected_value))
        return

    if self.args.rw_vpd_key or self.args.ro_vpd_key:  # type: ignore #TODO(b/338318729) Fixit!
      self.ui.SetHTML(_('Writing to VPD. Please wait...'), id='scan-status')  # type: ignore #TODO(b/338318729) Fixit!
      try:
        if self.args.rw_vpd_key:  # type: ignore #TODO(b/338318729) Fixit!
          self.dut.vpd.rw.Update({self.args.rw_vpd_key: scan_value})  # type: ignore #TODO(b/338318729) Fixit!
        if self.args.ro_vpd_key:  # type: ignore #TODO(b/338318729) Fixit!
          self.dut.vpd.ro.Update({self.args.ro_vpd_key: scan_value})  # type: ignore #TODO(b/338318729) Fixit!
      except Exception:
        logging.exception('Setting VPD failed')
        SetError(debug_utils.FormatExceptionOnly())
        return

    if self.args.save_path:  # type: ignore #TODO(b/338318729) Fixit!
      try:
        dirname = self.dut.path.dirname(self.args.save_path)  # type: ignore #TODO(b/338318729) Fixit!
        self.dut.CheckCall(['mkdir', '-p', dirname])
        self.dut.WriteFile(self.args.save_path, scan_value)  # type: ignore #TODO(b/338318729) Fixit!
      except Exception:
        logging.exception('Save file failed')
        SetError(debug_utils.FormatExceptionOnly())
        return

    self.event_loop.PostNewEvent(test_event.Event.Type.UPDATE_SYSTEM_INFO)  # type: ignore #TODO(b/338318729) Fixit!
    self.PassTask()

  def setUp(self):
    self.dut = device_utils.CreateDUTInterface()
    self.auto_scan_timer = None
    self.fixture = None
    if self.args.bft_fixture:  # type: ignore #TODO(b/338318729) Fixit!
      self.fixture = bft_fixture.CreateBFTFixture(**self.args.bft_fixture)  # type: ignore #TODO(b/338318729) Fixit!

  def tearDown(self):
    if self.fixture:
      self.fixture.Disconnect()

    if self.auto_scan_timer:
      self.auto_scan_timer.cancel()

  def ScanBarcode(self):
    while True:
      self.fixture.ScanBarcode()  # type: ignore #TODO(b/338318729) Fixit!
      self.Sleep(self.args.barcode_scan_interval_secs)  # type: ignore #TODO(b/338318729) Fixit!

  def BFTScanSaveBarcode(self):
    while True:
      self.fixture.TriggerScanner()  # type: ignore #TODO(b/338318729) Fixit!
      self.Sleep(self.args.barcode_scan_interval_secs)  # type: ignore #TODO(b/338318729) Fixit!

  def _GetOriginalValues(self) -> List[Tuple[str, Optional[str]]]:
    existed_data_source = {
        'serial_number_key': (
            self.args.serial_number_key, device_data.GetSerialNumber),  # type: ignore #TODO(b/338318729) Fixit!
        'device_data': (self.args.device_data_key, device_data.GetDeviceData),  # type: ignore #TODO(b/338318729) Fixit!
        'ro_vpd': (self.args.ro_vpd_key, self.dut.vpd.ro.get),  # type: ignore #TODO(b/338318729) Fixit!
        'rw_vpd': (self.args.rw_vpd_key, self.dut.vpd.rw.get),  # type: ignore #TODO(b/338318729) Fixit!
    }
    return [
        (f'{display_key_name}={data_key}', cast(Optional[str],
                                                getter(data_key)))
        for display_key_name, (data_key, getter) in existed_data_source.items()
        if data_key
    ]

  def runTest(self) -> None:
    self.ui.SetTitle(_('Scan {label}', label=self.args.label))  # type: ignore #TODO(b/338318729) Fixit!

    original_values = self._GetOriginalValues()

    self.ui.SetState([  # type: ignore #TODO(b/338318729) Fixit!
        _('Please scan the {label} and press ENTER.', label=self.args.label),  # type: ignore #TODO(b/338318729) Fixit!
        '<input id="scan-value" type="text" size="20">'
        '<p id="scan-status">&nbsp;</p>'
    ] + [
        _('<p>original value from {source}: {value}</p>', source=source,
          value=value) for source, value in original_values
    ])
    self.ui.SetFocus('scan-value')  # type: ignore #TODO(b/338318729) Fixit!
    self.ui.BindKeyJS(  # type: ignore #TODO(b/338318729) Fixit!
        test_ui.ENTER_KEY,
        'window.test.sendTestEvent("scan_value",'
        'document.getElementById("scan-value").value)')
    self.event_loop.AddEventHandler('scan_value', self.HandleScanValue)  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.value_assigned is not None:  # type: ignore #TODO(b/338318729) Fixit!
      self.ui.CallJSFunction(  # type: ignore #TODO(b/338318729) Fixit!
          'window.test.sendTestEvent', 'scan_value', self.args.value_assigned)  # type: ignore #TODO(b/338318729) Fixit!
    elif self.args.bft_scan_fixture_id:  # type: ignore #TODO(b/338318729) Fixit!
      logging.info('Getting fixture ID...')
      fixture_id = self.fixture.GetFixtureId()  # type: ignore #TODO(b/338318729) Fixit!
      self.ui.CallJSFunction('window.test.sendTestEvent', 'scan_value',  # type: ignore #TODO(b/338318729) Fixit!
                             str(fixture_id))
    elif self.args.bft_scan_barcode:  # type: ignore #TODO(b/338318729) Fixit!
      logging.info('Triggering barcode scanner...')
      self.ScanBarcode()
    elif self.args.bft_save_barcode:  # type: ignore #TODO(b/338318729) Fixit!
      logging.info('Triggering barcode scanner...')
      self.BFTScanSaveBarcode()
    elif self.args.bft_get_barcode:  # type: ignore #TODO(b/338318729) Fixit!
      logging.info('Getting barcode from BFT...')
      saved_barcode_path = None
      if isinstance(self.args.bft_get_barcode, str):  # type: ignore #TODO(b/338318729) Fixit!
        saved_barcode_path = self.args.bft_get_barcode  # type: ignore #TODO(b/338318729) Fixit!
      barcode = self.fixture.ScanBarcode(saved_barcode_path)  # type: ignore #TODO(b/338318729) Fixit!
      self.ui.CallJSFunction('window.test.sendTestEvent', 'scan_value', barcode)  # type: ignore #TODO(b/338318729) Fixit!

    self.WaitTaskEnd()
