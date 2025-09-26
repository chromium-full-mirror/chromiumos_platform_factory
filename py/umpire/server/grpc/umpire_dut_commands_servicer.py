# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Umpire DUT remote procedures.

This is the gRPC implementation of
cros.factory.umpire.server.rpc_dut.UmpireDUTCommands.
"""

import json
import logging
import os
import re
import tempfile
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


def ParseIpFromPeer(peer: str) -> str:
  """Parse ip from peer.

  Example input: "ipv4:192.168.71.139:42710"
  Example output: "192.168.71.139"
  """
  match = _PEER_PATTERN.fullmatch(peer)
  if not match:
    raise ValueError(f'{peer} does not match ${_PEER_PATTERN.pattern}')
  return match.group(1)


class UmpireDUTCommandsServicer(
    umpire_dut_commands_pb2_grpc.UmpireDUTCommandsServicer):

  def __init__(self, umpire_cli_url: str) -> None:
    super().__init__()
    self.CLI_command = cast(rpc_cli.CLICommand,
                            xmlrpc.client.ServerProxy(umpire_cli_url))

  def UpdateFactoryApp(self,
                       request: umpire_dut_commands_pb2.UpdateFactoryAppRequest,
                       context: grpc.ServicerContext):
    logging.info('request.target: %s, peer: %s', request.target, context.peer())
    try:
      target = request.target or ParseIpFromPeer(context.peer())
      logging.info('target: %s', target)
      config = json.loads(self.CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
      with tempfile.NamedTemporaryFile('+ab', suffix='.apk') as f:
        self.CLI_command.ExportPayload(
            bundle_id, resource.AndroidPayloadTypes.android_apk.name, f.name)
        cmd = [
            '/usr/local/factory/py/tools/install_as_priv_app.py', f.name,
            '--target', target
        ]
        if request.dpc:
          cmd.append('--dpc_enabled')
        process_utils.CheckCall(cmd, log=True, log_stderr_on_error=True)
    except Exception as err:
      return umpire_dut_commands_pb2.UpdateFactoryAppResponse(
          success=False, messages=str(err))
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
    try:
      target = request.target or ParseIpFromPeer(context.peer())
      logging.info('GetOtaPackage target: %s', target)
      remote_path = request.path
      config = json.loads(self.CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
      with tempfile.NamedTemporaryFile('+ab', suffix='.otazip') as f:
        self.CLI_command.ExportPayload(
            bundle_id, resource.AndroidPayloadTypes.ota_zip.name, f.name)
        process_utils.CheckCall(['adb', 'connect', target], log=True,
                                log_stderr_on_error=True)
        process_utils.CheckCall(['adb', '-s', target, 'root'], log=True,
                                log_stderr_on_error=True)
        process_utils.CheckCall(
            ['adb', '-s', target, 'push', f.name, remote_path], log=True,
            log_stderr_on_error=True)
    except Exception as err:
      return umpire_dut_commands_pb2.GetOtaPackageResponse(
          success=False, messages=str(err))
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
    try:
      first_request = next(request_iterator)
      if first_request.WhichOneof('data') != 'metadata':
        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        context.set_details('The first message must be metadata.')
        return umpire_dut_commands_pb2.UploadReportResponse(success=False)
    except StopIteration:
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
      context.set_details('Received an empty request stream.')
      return umpire_dut_commands_pb2.UploadReportResponse(success=False)

    serial_number = first_request.metadata.serial_number
    if not serial_number:
      context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
      context.set_details('Serial number must be provided.')
      return umpire_dut_commands_pb2.UploadReportResponse(success=False)

    save_path = self._GetReportSavePath(serial_number,
                                        first_request.metadata.stage)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    try:
      with open(save_path, 'wb') as f:
        with zstandard.ZstdCompressor().stream_writer(f) as compressor:
          for request in request_iterator:
            if request.WhichOneof('data') != 'chunk':
              context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
              context.set_details(
                  'Expected a file chunk, but received another message type '
                  'mid-stream.')
              return umpire_dut_commands_pb2.UploadReportResponse(success=False)
            compressor.write(request.chunk)
      return umpire_dut_commands_pb2.UploadReportResponse(success=True)
    except Exception as e:
      context.set_code(grpc.StatusCode.INTERNAL)
      context.set_details(f'An error occurred: {e}')
      return umpire_dut_commands_pb2.UploadReportResponse(success=False)
