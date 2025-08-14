#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from cros.factory.gooftool import commands
from cros.factory.gooftool.core import FactoryProcessEnum
from cros.factory.gooftool.core import FinalizeMode
from cros.factory.test.pytests import finalize
from cros.factory.test.rules import phase
from cros.factory.test.rules.phase import PhaseAssertionError
from cros.factory.test.utils import cbi_utils


class DefaultArgs:

  def __init__(self):
    self.write_protection = None
    self.has_ectool = True
    self.secure_wipe = True
    self.upload_method = None
    self.upload_max_retry_times = 0
    self.upload_retry_interval = None
    self.upload_allow_fail = False
    self.enable_factory_server = True
    self.hwid_need_vpd = False
    self.factory_process = FactoryProcessEnum.FULL
    self.is_cros_core = False
    self.has_ec_pubkey = None
    self.ec_pubkey_path = None
    self.ec_pubkey_hash = None
    self.use_local_gooftool = True
    self.station_ip = None
    self.gooftool_waive_list = []
    self.gooftool_skip_list = []
    self.enable_zero_touch = False
    self.cbi_eeprom_wp_status = cbi_utils.CbiEepromWpStatus.Locked
    self.is_reference_board = False
    self.project = None
    self.mode = FinalizeMode.ASSEMBLED
    self.enforced_release_channels = None
    self.skip_feature_tiering_steps = False
    self.block_dev_mode = False


class FinalizeUnittest(unittest.TestCase):

  def MockFunction(self, function_name, return_value=None):
    if return_value is None:
      patcher = mock.patch(function_name)
    else:
      patcher = mock.patch(function_name, return_value=return_value)
    patcher.start()
    self.addCleanup(patcher.stop)

  def setUp(self):
    self.test = finalize.Finalize()
    # yapf: disable
    self.test.args = DefaultArgs()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.test.test_states_path = 'states_path'
    self.MockFunction('cros.factory.test.server_proxy.GetServerURL', 'url')
    self.MockFunction('cros.factory.test.device_data.GetSerialNumber', 123)
    self.MockFunction('cros.factory.test.rules.phase.GetPhase', phase.DVT)
    self.MockFunction('cros.factory.test.state.GetInstance')
    self.MockFunction(f'{finalize.__name__}.Finalize.Warn')

  def _FakeAppendUploadReportArgs(self, command):
    return command + ' upload_args'

  @mock.patch(f'{finalize.__name__}.Finalize.AppendUploadReportArgs')
  @mock.patch(f'{finalize.__name__}.Finalize._DoFinalize')
  def testFinalizeMLB(self, mock_finalize, mock_upload_report_args):
    mock_upload_report_args.side_effect = self._FakeAppendUploadReportArgs
    self.test.FinalizeMLB()
    mock_finalize.assert_called_with(
        'gooftool -v 4 smt_finalize upload_args --factory_process FULL', True)

  @mock.patch(f'{finalize.__name__}.Finalize.AppendUploadReportArgs')
  @mock.patch(f'{finalize.__name__}.Finalize._DoFinalize')
  def testFinalizeShimlessMLB(self, mock_finalize, mock_upload_report_args):
    # yapf: disable
    self.test.args.factory_process = FactoryProcessEnum.RMA  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.mode = FinalizeMode.SHIMLESS_MLB  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    mock_upload_report_args.side_effect = self._FakeAppendUploadReportArgs

    self.test.FinalizeMLB()
    mock_finalize.assert_called_with(
        'gooftool -v 4 smt_finalize upload_args --factory_process RMA '
        '--boot_to_shimless', False)

    # yapf: disable
    self.test.args.secure_wipe = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.test.FinalizeMLB()
    mock_finalize.assert_called_with(
        'gooftool -v 4 smt_finalize upload_args --factory_process RMA '
        '--boot_to_shimless --fast', False)

  def testUploadReportArgsUploadMethodNone(self):
    # yapf: disable
    self.test.args.enable_factory_server = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    for upload_method in [None, 'none']:
      # yapf: disable
      self.test.args.upload_method = upload_method  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      actual = self.test.AppendUploadReportArgs('')
      self.assertTrue('--upload_method "none"' in actual)

  def testUploadReportArgsUploadMethodFactoryServer(self):
    # yapf: disable
    self.test.args.enable_factory_server = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.upload_method = 'factory_server'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    actual = self.test.AppendUploadReportArgs('')
    self.assertTrue('--upload_method "factory_server:url#123"' in actual)

  def testUploadReportArgsEnableFactoryServer(self):
    # yapf: disable
    self.test.args.enable_factory_server = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    actual = self.test.AppendUploadReportArgs('')
    self.assertTrue('--factory_server_url "url"' in actual)

  @mock.patch('cros.factory.test.server_proxy.GetServerURL')
  def testUploadReportArgsNoServerUrl(self, mock_server_url):
    mock_server_url.return_value = None
    # yapf: disable
    self.test.args.enable_factory_server = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    actual = self.test.AppendUploadReportArgs('')
    self.assertFalse('--factory_server_url' in actual)

  def testUploadReportArgsNotEnableFactoryServer(self):
    # yapf: disable
    self.test.args.enable_factory_server = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    actual = self.test.AppendUploadReportArgs('')
    self.assertFalse('--factory_server_url' in actual)

  def testUploadReportArgsAlways(self):
    self.test.test_states_path = 'path'
    actual = self.test.AppendUploadReportArgs('')
    self.assertTrue('--add_file "path"' in actual)

  def testUploadReportArgsAppend(self):
    # yapf: disable
    self.test.args.enable_factory_server = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.upload_max_retry_times = 1  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.upload_retry_interval = 2  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.upload_allow_fail = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    actual = self.test.AppendUploadReportArgs('')

    self.assertTrue('--upload_max_retry_times 1' in actual)
    self.assertTrue('--upload_retry_interval 2' in actual)
    self.assertTrue('--upload_allow_fail' in actual)

  def testUploadReportArgsNotAppend(self):
    # yapf: disable
    self.test.args.upload_max_retry_times = 0  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.upload_retry_interval = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.upload_allow_fail = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    actual = self.test.AppendUploadReportArgs('')

    self.assertFalse('--upload_max_retry_times' in actual)
    self.assertFalse('--upload_retry_interval' in actual)
    self.assertFalse('--upload_allow_fail' in actual)

  def _FakeAppendAssembledArgs(self, command):
    return command + ' assembled_args'

  @mock.patch(f'{finalize.__name__}.Finalize.AppendUploadReportArgs')
  @mock.patch(f'{finalize.__name__}.Finalize.AppendAssembledArgs')
  @mock.patch(f'{finalize.__name__}.Finalize._DoFinalize')
  def testFinalize(self, mock_finalize, mock_assembled_args,
                   mock_upload_report_args):
    mock_assembled_args.side_effect = self._FakeAppendAssembledArgs
    mock_upload_report_args.side_effect = self._FakeAppendUploadReportArgs
    # yapf: disable
    self.test.args.gooftool_skip_list = []  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.test.Finalize()
    mock_finalize.assert_called_with(
        'gooftool -v 4 finalize upload_args assembled_args', False)

  @mock.patch(f'{finalize.__name__}.Finalize.AppendUploadReportArgs')
  @mock.patch(f'{finalize.__name__}.Finalize.AppendAssembledArgs')
  @mock.patch(f'{finalize.__name__}.Finalize._DoFinalize')
  def testFinalizeSkipWipe(self, mock_finalize, mock_assembled_args,
                           mock_upload_report_args):
    mock_assembled_args.side_effect = self._FakeAppendAssembledArgs
    mock_upload_report_args.side_effect = self._FakeAppendUploadReportArgs
    # yapf: disable
    self.test.args.gooftool_skip_list = [commands.WIPE_IN_PLACE]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.test.Finalize()
    mock_finalize.assert_called_with(
        'gooftool -v 4 finalize upload_args assembled_args', True)

  @mock.patch('cros.factory.test.rules.phase.GetPhase')
  def testAssembledArgsAlways(self, mock_phase):
    mock_phase.return_value = 'phase'
    # yapf: disable
    self.test.args.cbi_eeprom_wp_status = "status"  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.factory_process = FactoryProcessEnum.TWOSTAGES  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    actual = self.test.AppendAssembledArgs('')

    self.assertTrue('--cbi_eeprom_wp_status status' in actual)
    self.assertTrue('--phase "phase"' in actual)
    self.assertTrue('--factory_process TWOSTAGES' in actual)

  def testAssembledArgsAppended(self):
    # yapf: disable
    self.test.args.write_protection = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.has_ectool = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.secure_wipe = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.hwid_need_vpd = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.is_cros_core = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.has_ec_pubkey = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.ec_pubkey_path = 'pubkey_path'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.gooftool_waive_list = ['waive_item1', 'waive_item2']  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.gooftool_skip_list = ['skip_item1', 'skip_item2']  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.enforced_release_channels = ['1', '2', '3']  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.enable_zero_touch = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.is_reference_board = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.project = 'project'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    actual = self.test.AppendAssembledArgs('')

    required_flags = [
        '--no_write_protect',
        '--no_ectool',
        '--fast',
        '--hwid-run-vpd',
        '--cros_core',
        '--has_ec_pubkey',
        '--ec_pubkey_path pubkey_path',
        '--waive_list waive_item1 waive_item2',
        '--skip_list skip_item1 skip_item2',
        '--enforced_release_channels 1 2 3',
        '--enable_zero_touch',
        '--is_reference_board',
        '--has_ec_pubkey',
        '--project project',
    ]

    for flag in required_flags:
      self.assertTrue(flag in actual)

  def testAssembledArgsNotAppended(self):
    # yapf: disable
    self.test.args.write_protection = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.has_ectool = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.secure_wipe = True  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.hwid_need_vpd = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.is_cros_core = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.has_ec_pubkey = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.ec_pubkey_path = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.gooftool_waive_list = []  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.gooftool_skip_list = []  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.enforced_release_channels = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.enable_zero_touch = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.is_reference_board = False  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.project = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    actual = self.test.AppendAssembledArgs('')

    not_append_flags = [
        '--no_write_protect',
        '--no_ectool',
        '--fast',
        '--hwid-run-vpd',
        '--cros_core',
        '--has_ec_pubkey',
        '--ec_pubkey_path',
        '--waive_list',
        '--skip_list',
        '--enforced_release_channels',
        '--enable_zero_touch',
        '--is_reference_board',
        '--has_ec_pubkey',
        '--project',
    ]
    for flag in not_append_flags:
      self.assertFalse(flag in actual)

  def testAssembledArgsOnlyEcPubkeyHash(self):
    # yapf: disable
    self.test.args.ec_pubkey_path = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.ec_pubkey_hash = 'pubkey_hash'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    actual = self.test.AppendAssembledArgs('')

    self.assertTrue('--ec_pubkey_hash pubkey_hash' in actual)

  def testAssembledArgsNoEcPubkeyHash(self):
    # yapf: disable
    self.test.args.ec_pubkey_path = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    self.test.args.ec_pubkey_hash = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    actual = self.test.AppendAssembledArgs('')

    self.assertFalse('--ec_pubkey_hash' in actual)

  @mock.patch('cros.factory.test.rules.phase.GetPhase')
  def testAssembledProjectInPVTRaise(self, mock_phase):
    mock_phase.return_value = phase.PVT
    # yapf: disable
    self.test.args.project = 'project'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    self.assertRaises(PhaseAssertionError, self.test.AppendAssembledArgs, '')


if __name__ == '__main__':
  unittest.main()
