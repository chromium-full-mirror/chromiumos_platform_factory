# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Umpire DUT remote procedures.

This is the gRPC implementation of
cros.factory.umpire.server.rpc_dut.UmpireDUTCommands.
"""

import io
import json
import logging
import os
import re
import tempfile
import threading
import time
from typing import Iterator, Optional, cast
import xmlrpc.client

import grpc
import zstandard

from cros.factory.umpire.server.proto import umpire_dut_commands_pb2
from cros.factory.umpire.server.proto import umpire_dut_commands_pb2_grpc
from cros.factory.umpire.server import resource
from cros.factory.umpire.server import rpc_cli
from cros.factory.umpire.server import umpire_env
from cros.factory.utils import json_utils
from cros.factory.utils import process_utils
from cros.factory.utils import time_utils


_PEER_PATTERN = re.compile(r'ipv4:(.*):\d+')
_REPORT_INDEX_JSON_FILE = '/var/db/factory/umpire/properties/report_index.json'


def ParseIpFromPeer(peer: str) -> str:
  """Parse ip from peer.

  Example input: "ipv4:192.168.71.139:42710"
  Example output: "192.168.71.139"
  """
  match = _PEER_PATTERN.fullmatch(peer)
  if not match:
    raise ValueError(f'{peer} does not match ${_PEER_PATTERN.pattern}')
  return match.group(1)


def AdbConnect(target: str, log: bool = True,
               log_stderr_on_error: bool = True) -> None:
  process_utils.CheckCall(['adb', 'connect', target], log=log,
                          log_stderr_on_error=log_stderr_on_error)


def AdbRoot(target: str, log: bool = True,
            log_stderr_on_error: bool = True) -> None:
  process_utils.CheckCall(['adb', '-s', target, 'root'], log=log,
                          log_stderr_on_error=log_stderr_on_error)


def AdbDisconnect(target: str, log: bool = True,
                  log_stderr_on_error: bool = True) -> None:
  process_utils.CheckCall(['adb', 'disconnect', target], log=log,
                          log_stderr_on_error=log_stderr_on_error)

class UmpireDUTCommandsServicer(
    umpire_dut_commands_pb2_grpc.UmpireDUTCommandsServicer):

  def __init__(self, umpire_cli_url: str) -> None:
    super().__init__()
    self._umpire_cli_url = umpire_cli_url
    self._local = threading.local()
    self._report_index_manager = umpire_env.ReportIndexManager(
        _REPORT_INDEX_JSON_FILE)

  @property
  def CLI_command(self) -> rpc_cli.CLICommand:
    """Provides a thread-safe XML-RPC proxy."""
    if not hasattr(self._local, 'proxy'):
      self._local.proxy = cast(rpc_cli.CLICommand,
                               xmlrpc.client.ServerProxy(self._umpire_cli_url))
    return self._local.proxy

  def UpdateFactoryApp(self,
                       request: umpire_dut_commands_pb2.UpdateFactoryAppRequest,
                       context: grpc.ServicerContext):
    logging.info('request.target: %s, peer: %s', request.target, context.peer())
    connected = False
    try:
      target = request.target or ParseIpFromPeer(context.peer())
      logging.info('target: %s', target)
      config = json.loads(self.CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
      with tempfile.NamedTemporaryFile('+ab', suffix='.apk') as f:
        self.CLI_command.ExportPayload(
            bundle_id, resource.AndroidPayloadTypes.android_apk.name, f.name)
        AdbConnect(target)
        connected = True
        AdbRoot(target)
        process_utils.CheckCall([
            'adb', '-s', target, 'shell', 'pm', 'disable-user', '--user', '10',
            'com.google.android.factory.factory'
        ], log=True, log_stderr_on_error=True)
        process_utils.CheckCall(
            ['adb', '-s', target, 'install', '-g', '-t', '-r', f.name],
            log=True, log_stderr_on_error=True)
    except Exception as err:
      return umpire_dut_commands_pb2.UpdateFactoryAppResponse(
          success=False, messages=str(err))
    finally:
      if connected:
        process_utils.CheckCall([
            'adb', '-s', target, 'shell', 'pm', 'enable', '--user', '10',
            'com.google.android.factory.factory'
        ], log=True, log_stderr_on_error=True)
        process_utils.CheckCall([
            'adb', '-s', target, 'shell', 'am', 'start', '-a',
            'android.intent.action.MAIN', '-c', 'android.intent.category.HOME'
        ], log=True, log_stderr_on_error=True)
        AdbDisconnect(target)
    return umpire_dut_commands_pb2.UpdateFactoryAppResponse(
        success=True, messages='')

  def GetUpdateVersion(
      self,
      request: umpire_dut_commands_pb2.GetUpdateVersionRequest,
      context: grpc.ServicerContext,
  ):
    logging.info('GetUpdateVersion: peer: %s', context.peer())
    payloads = self.CLI_command.GetActivePayload()
    if not payloads:
      return umpire_dut_commands_pb2.GetUpdateVersionResponse()
    # May add more components later.
    field_name = {
        umpire_dut_commands_pb2.COMPONENT_TOOLKIT: 'android_apk'
    }.get(request.component)
    return umpire_dut_commands_pb2.GetUpdateVersionResponse(
        version=payloads.get(field_name, {}).get('version', ''))

  def GetOtaPackage(self, request, context):
    logging.info('request.target: %s, path: %s, peer: %s', request.target,
                 request.path, context.peer())
    connected = False
    try:
      target = request.target or ParseIpFromPeer(context.peer())
      logging.info('GetOtaPackage target: %s', target)
      remote_path = request.path
      config = json.loads(self.CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
      with tempfile.NamedTemporaryFile('+ab', suffix='.otazip') as f:
        self.CLI_command.ExportPayload(
            bundle_id, resource.AndroidPayloadTypes.ota_zip.name, f.name)
        AdbConnect(target)
        connected = True
        AdbRoot(target)
        process_utils.CheckCall(
            ['adb', '-s', target, 'push', f.name, remote_path], log=True,
            log_stderr_on_error=True)
    except Exception as err:
      return umpire_dut_commands_pb2.GetOtaPackageResponse(
          success=False, messages=str(err))
    finally:
      if connected:
        AdbDisconnect(target)
    return umpire_dut_commands_pb2.GetOtaPackageResponse(
        success=True, messages='')

  def _GetTimezone(self) -> Optional[int]:
    """Gets current time zone.

    Returns:
      The time zone in int type (e.g. 1 indicates UTC+1), or `None` if the
      timezone is unknown.
    """
    timezone = None
    active_config_file = self.CLI_command.GetActiveConfig()
    self_active_config = json_utils.LoadStr(active_config_file)['services']
    if 'umpire_timezone' in self_active_config:
      if self_active_config['umpire_timezone']['active']:
        timezone = self_active_config['umpire_timezone']['timezone']
    return timezone

  def _GetReportSavePath(self, serial_number: str, stage: Optional[str]) -> str:
    date_str = time.strftime('%Y%m%d',
                             time_utils.GetNowWithTimezone(self._GetTimezone()))
    stage = stage or 'Unknown'
    timestamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(time.time()))
    file_name = f'{serial_number}-{stage}-{timestamp}.rpt.zst'
    return os.path.join('/', umpire_env.DEFAULT_BASE_DIR, 'umpire_data',
                        'report', date_str, file_name)

  def UploadReport(
      self,
      request_iterator: Iterator[umpire_dut_commands_pb2.UploadReportRequest],
      context: grpc.ServicerContext,
  ) -> umpire_dut_commands_pb2.UploadReportResponse:
    with self._report_index_manager.AllocateNextIndex() as (
        server_uuid,
        report_index,
    ):
      first_request = next(request_iterator, None)
      if first_request is None:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                      'Received an empty request stream.')

      first_data_type = first_request.WhichOneof('data')
      if first_data_type != 'metadata':
        context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                      'The first message must be metadata.')

      serial_number = first_request.metadata.serial_number
      if not serial_number:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                      'Serial number must be provided.')

      save_path = self._GetReportSavePath(serial_number,
                                          first_request.metadata.stage)
      os.makedirs(os.path.dirname(save_path), exist_ok=True)

      with open(save_path, 'wb') as f:
        with zstandard.ZstdCompressor().stream_writer(f) as compressor:
          for request in request_iterator:
            if request.WhichOneof('data') != 'chunk':
              context.abort(
                  grpc.StatusCode.INVALID_ARGUMENT,
                  'Expected a file chunk, but received another message type '
                  'mid-stream.',
              )
            compressor.write(request.chunk)
          self._WriteReportIndex(compressor, server_uuid, report_index)

      return umpire_dut_commands_pb2.UploadReportResponse(success=True)

  def _WriteReportIndex(self, writer: io.RawIOBase, server_uuid: str,
                        report_index: str) -> None:
    entry = {
        'type': 'metadata',
        'serverUuid': server_uuid,
        'reportIndex': f'{report_index:010d}',
        'domeVersion': os.environ.get('DOCKER_IMAGE_TIMESTAMP', ''),
    }
    entry_str = json_utils.DumpStr(entry, pretty=False, newline=True)
    writer.write(entry_str.encode('utf8'))

  def SyncDeviceTime(
      self,
      request: umpire_dut_commands_pb2.SyncDeviceTimeRequest,
      context: grpc.ServicerContext,
  ) -> umpire_dut_commands_pb2.SyncDeviceTimeResponse:
    """Synchronizes the DUT's time zone to the Umpire server's time zone."""
    logging.info('SyncDeviceTime: peer: %s', context.peer())
    conneected = False
    try:
      target = request.target or ParseIpFromPeer(context.peer())
      epoch_time = int(time.time())

      AdbConnect(target)
      conneected = True
      AdbRoot(target)

      logging.info('Setting device time to host epoch: %d', epoch_time)
      set_date_cmd = [
          'adb', '-s', target, 'shell', f'date @{epoch_time}'
      ]
      process_utils.CheckCall(set_date_cmd, log=True, log_stderr_on_error=True)

      set_hwclock_cmd = ['adb', '-s', target, 'shell', 'hwclock -w --utc']
      logging.info('Executing: %s', ' '.join(set_hwclock_cmd))
      process_utils.CheckCall(set_hwclock_cmd, log=True,
                              log_stderr_on_error=True)

    except Exception as err:
      error_message = f'Failed to set time on {target}: {err}'
      logging.error(error_message)
      return umpire_dut_commands_pb2.SyncDeviceTimeResponse(
          success=False, messages=error_message)
    finally:
      if conneected:
        AdbDisconnect(target)
    return umpire_dut_commands_pb2.SyncDeviceTimeResponse(
        success=True,
        messages=f'Successfully synced time on {target} to epoch {epoch_time}')
