# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Umpire DUT remote procedures.

This is the gRPC implementation of
cros.factory.umpire.server.rpc_dut.UmpireDUTCommands.
"""

import contextlib
import io
import json
import logging
import os
import random
import re
import shutil
import string
import tarfile
import tempfile
import threading
import time
from typing import Generator, Iterator, Optional, cast
import xmlrpc.client

from google.protobuf import empty_pb2
import grpc  # pylint: disable=import-error
import zstandard  # pylint: disable=import-error

from cros.factory.umpire.server.grpc import report_index
from cros.factory.umpire.server.proto import umpire_dut_commands_pb2
from cros.factory.umpire.server.proto import umpire_dut_commands_pb2_grpc
from cros.factory.umpire.server import resource
from cros.factory.umpire.server import rpc_cli
from cros.factory.umpire.server import umpire_env
from cros.factory.utils import file_utils
from cros.factory.utils import json_utils
from cros.factory.utils import process_utils
from cros.factory.utils import time_utils


_PEER_PATTERN = re.compile(r'ipv4:(.*):\d+')


def _ParseIpFromPeer(peer: str) -> str:
  """Parse ip from peer.

  Example input: "ipv4:192.168.71.139:42710"
  Example output: "192.168.71.139"
  """
  match = _PEER_PATTERN.fullmatch(peer)
  if not match:
    raise ValueError(f'{peer} does not match ${_PEER_PATTERN.pattern}')
  return match.group(1)


def _AdbConnect(target: str, log: bool = True,
                log_stderr_on_error: bool = True) -> None:
  process_utils.CheckCall(['adb', 'connect', target], log=log,
                          log_stderr_on_error=log_stderr_on_error)


def _AdbRoot(target: str, log: bool = True,
             log_stderr_on_error: bool = True) -> None:
  process_utils.CheckCall(['adb', '-s', target, 'root'], log=log,
                          log_stderr_on_error=log_stderr_on_error)


def _AdbDisconnect(target: str, log: bool = True,
                   log_stderr_on_error: bool = True) -> None:
  process_utils.CheckCall(['adb', 'disconnect', target], log=log,
                          log_stderr_on_error=log_stderr_on_error)


class UmpireDUTCommandsServicer(
    umpire_dut_commands_pb2_grpc.UmpireDUTCommandsServicer):

  _UMPIRE_DIR = os.path.join('/', umpire_env.DEFAULT_BASE_DIR)
  _UMPIRE_DATA_DIR = os.path.join(_UMPIRE_DIR, 'umpire_data')
  _REPORT_DATA_DIR = os.path.join(_UMPIRE_DATA_DIR, 'report')
  _CSR_DATA_DIR = os.path.join(_UMPIRE_DATA_DIR, 'csr')

  _TEST_PHASE_TO_NAME_MAPPING = {
      umpire_dut_commands_pb2.TEST_PHASE_PROTO: "PROTO",
      umpire_dut_commands_pb2.TEST_PHASE_EVT: "EVT",
      umpire_dut_commands_pb2.TEST_PHASE_DVT: "DVT",
      umpire_dut_commands_pb2.TEST_PHASE_PVT: "PVT",
      umpire_dut_commands_pb2.TEST_PHASE_MP: "MP"
  }

  def __init__(self, umpire_cli_url: str) -> None:
    super().__init__()
    self._umpire_cli_url = umpire_cli_url
    self._local = threading.local()
    self._report_index_manager = report_index.ReportIndexManager()

  @property
  def _CLI_command(self) -> rpc_cli.CLICommand:
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
      target = request.target or _ParseIpFromPeer(context.peer())
      logging.info('target: %s', target)
      config = json.loads(self._CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
      with tempfile.NamedTemporaryFile('+ab', suffix='.apk') as f:
        self._CLI_command.ExportPayload(
            bundle_id, resource.AndroidPayloadTypes.android_apk.name, f.name)
        _AdbConnect(target)
        connected = True
        _AdbRoot(target)
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
        _AdbDisconnect(target)
    return umpire_dut_commands_pb2.UpdateFactoryAppResponse(
        success=True, messages='')

  def GetUpdateVersion(
      self,
      request: umpire_dut_commands_pb2.GetUpdateVersionRequest,
      context: grpc.ServicerContext,
  ):
    logging.info('GetUpdateVersion: peer: %s', context.peer())
    payloads = self._CLI_command.GetActivePayload()
    if not payloads:
      return umpire_dut_commands_pb2.GetUpdateVersionResponse()
    # May add more components later.
    field_name = {
        umpire_dut_commands_pb2.COMPONENT_TOOLKIT: 'android_apk'
    }.get(request.component)
    return umpire_dut_commands_pb2.GetUpdateVersionResponse(
        version=payloads.get(field_name, {}).get('version', ''))

  def DownloadPayload(self,
                      request: umpire_dut_commands_pb2.DownloadPayloadRequest,
                      context: grpc.ServicerContext):
    logging.info('request.target: %s, path: %s, peer: %s', request.target,
                 request.path, context.peer())
    target = request.target or _ParseIpFromPeer(context.peer())
    logging.info('DownloadPayload target: %s', target)

    try:
      config = json.loads(self._CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
    except (ValueError, KeyError) as e:
      return umpire_dut_commands_pb2.DownloadPayloadResponse(
          success=False, messages=f'Config error: {str(e)}')

    payload_map = {
        umpire_dut_commands_pb2.PAYLOAD_TYPE_APK: {
            'resource': resource.AndroidPayloadTypes.android_apk.name,
            'ext': '.apk'
        },
        umpire_dut_commands_pb2.PAYLOAD_TYPE_OTA: {
            'resource': resource.AndroidPayloadTypes.ota_zip.name,
            'ext': '.zip'
        }
    }

    if request.payload_type not in payload_map:
      return umpire_dut_commands_pb2.DownloadPayloadResponse(
          success=False, messages='Unsupported payload type.')

    payload_info = payload_map[request.payload_type]

    active_payloads = self._CLI_command.GetActivePayload()
    if payload_info['resource'] not in active_payloads:
      return umpire_dut_commands_pb2.DownloadPayloadResponse(
          success=False,
          messages=(f'Payload {payload_info["resource"]} not found in'
                    ' the active bundle.'))

    connected = False
    try:
      with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, f'payload{payload_info["ext"]}')
        self._CLI_command.ExportPayload(bundle_id, payload_info['resource'],
                                        temp_file_path)
        _AdbConnect(target)
        connected = True
        _AdbRoot(target)

        process_utils.CheckCall(
            ['adb', '-s', target, 'push', temp_file_path, request.path],
            log=True, log_stderr_on_error=True)

    except Exception as err:
      logging.error('DownloadPayload failed: %s', err)
      return umpire_dut_commands_pb2.DownloadPayloadResponse(
          success=False, messages=str(err))
    finally:
      if connected:
        _AdbDisconnect(target)

    return umpire_dut_commands_pb2.DownloadPayloadResponse(
        success=True, messages='')

  def DownloadFactoryDrives(
      self,
      request: umpire_dut_commands_pb2.DownloadFactoryDrivesRequest,
      context: grpc.ServicerContext,
  ) -> umpire_dut_commands_pb2.DownloadFactoryDrivesResponse:
    logging.info(
        'request.target: %s, dest_path: %s, source_namespace: %s, '
        'source_file: %s, peer: %s',
        request.target,
        request.dest_path,
        request.source_namespace,
        request.source_file,
        context.peer(),
    )
    connected = False
    extract_path = tempfile.mkdtemp()
    try:
      target = request.target or _ParseIpFromPeer(context.peer())
      logging.info('DownloadFactoryDrives target: %s', target)
      remote_path = request.dest_path
      content = self._CLI_command.GetFactoryDrives(request.source_namespace,
                                                   request.source_file).data
      tar_stream = io.BytesIO(content)
      with tarfile.open(fileobj=tar_stream, mode='r') as tar:
        tar.extractall(path=extract_path)
        _AdbConnect(target)
        connected = True
        _AdbRoot(target)
        process_utils.CheckCall([
            'adb', '-s', target, 'push',
            f'{extract_path}/{request.source_file}', remote_path
        ], log=True, log_stderr_on_error=True)
    except Exception as err:
      return umpire_dut_commands_pb2.DownloadFactoryDrivesResponse(
          success=False, messages=str(err))
    finally:
      shutil.rmtree(extract_path)
      if connected:
        _AdbDisconnect(target)
    return umpire_dut_commands_pb2.DownloadFactoryDrivesResponse(
        success=True,
        messages=f'Successfully download from the factory drives on {target}')

  # pylint: disable=unused-argument
  def GetFactoryDriveManifest(
      self,
      request: umpire_dut_commands_pb2.GetFactoryDriveManifestRequest,
      context: grpc.ServicerContext,
  ) -> umpire_dut_commands_pb2.GetFactoryDriveManifestResponse:
    logging.info('GetFactoryDriveManifest from peer %s started', context.peer())
    manifest = self._CLI_command.GetFactoryDriveManifest()
    response = umpire_dut_commands_pb2.GetFactoryDriveManifestResponse(files=[
        umpire_dut_commands_pb2.FileMetadata(**item) for item in manifest
    ])
    return response

  def GetOtaPackage(self, request, context):
    logging.info('request.target: %s, path: %s, peer: %s', request.target,
                 request.path, context.peer())
    connected = False
    try:
      target = request.target or _ParseIpFromPeer(context.peer())
      logging.info('GetOtaPackage target: %s', target)
      remote_path = request.path
      config = json.loads(self._CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
      with tempfile.NamedTemporaryFile('+ab', suffix='.otazip') as f:
        self._CLI_command.ExportPayload(
            bundle_id, resource.AndroidPayloadTypes.ota_zip.name, f.name)
        _AdbConnect(target)
        connected = True
        _AdbRoot(target)
        process_utils.CheckCall(
            ['adb', '-s', target, 'push', f.name, remote_path], log=True,
            log_stderr_on_error=True)
    except Exception as err:
      return umpire_dut_commands_pb2.GetOtaPackageResponse(
          success=False, messages=str(err))
    finally:
      if connected:
        _AdbDisconnect(target)
    return umpire_dut_commands_pb2.GetOtaPackageResponse(
        success=True, messages='')

  def _GetTimezone(self) -> Optional[int]:
    """Gets current time zone.

    Returns:
      The time zone in int type (e.g. 1 indicates UTC+1), or `None` if the
      timezone is unknown.
    """
    timezone = None
    active_config_file = self._CLI_command.GetActiveConfig()
    self_active_config = json_utils.LoadStr(active_config_file)['services']
    if 'umpire_timezone' in self_active_config:
      if self_active_config['umpire_timezone']['active']:
        timezone = self_active_config['umpire_timezone']['timezone']
    return timezone

  def _GetFileSavePath(self, save_dir: str, serial_number: str, test_phase: str,
                       data_type: str) -> str:
    date_str = time.strftime('%Y%m%d',
                             time_utils.GetNowWithTimezone(self._GetTimezone()))
    timestamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(time.time()))
    file_name = f'{serial_number}-{test_phase}-{timestamp}.{data_type}.zst'
    return os.path.join(save_dir, date_str, file_name)

  @contextlib.contextmanager
  def _SaveFileAsZst(
      self, save_dir: str, data_type: str,
      request_iterator: Iterator[umpire_dut_commands_pb2.UploadFileRequest],
      context: grpc.ServicerContext) -> Generator[io.RawIOBase, None, None]:
    # TODO: b/514279711 - Remove trivial debugging logs after the bug is fixed.
    request_id = cast(str, getattr(context, 'request_id', 'unspecified'))

    first_request = next(request_iterator, None)
    if first_request is None:
      context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                    'Received an empty request stream.')
      return

    data_type = first_request.WhichOneof('data')
    if data_type != 'device_metadata':
      context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                    'The first message must be device metadata.')
      return

    serial_number = first_request.device_metadata.serial_number
    if not serial_number:
      context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                    'Serial number must be provided.')
      return
    logging.debug("[%s] Serial number is %s.", request_id, serial_number)

    try:
      test_phase = self._TEST_PHASE_TO_NAME_MAPPING[
          first_request.device_metadata.test_phase]
    except KeyError:
      context.abort(
          grpc.StatusCode.INVALID_ARGUMENT,
          f'Invalid test phase: {first_request.device_metadata.test_phase}')
      return

    save_path = self._GetFileSavePath(save_dir, serial_number, test_phase,
                                      data_type)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    logging.debug("[%s] Saving file to %s.", request_id, save_path)

    with file_utils.AtomicWrite(save_path, binary=True) as f:
      with zstandard.ZstdCompressor().stream_writer(
          f,
          # Don't auto close fd on ZstdCompressor; AtomicWrite will close it.
          closefd=False) as _compressor:
        # Zstd writer conforms to io.RawIOBase so cast type to let mypy work
        compressor = cast(io.RawIOBase, _compressor)

        for request in request_iterator:
          if request.WhichOneof('data') != 'chunk':
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                'Expected a file chunk, but received another message type '
                'mid-stream.',
            )
            return
          chunk_size = len(request.chunk)
          compressor.write(request.chunk)
          logging.debug("[%s] Wrote %d bytes.", request_id, chunk_size)

        yield compressor

    logging.debug("[%s] File saved.", request_id)

  def UploadReport(
      self,
      request_iterator: Iterator[umpire_dut_commands_pb2.UploadFileRequest],
      context: grpc.ServicerContext,
  ) -> empty_pb2.Empty:

    # Generate a random ID for each request and log messages with it for
    # debugging purpose.
    # TODO: b/514279711 - Remove trivial debugging logs after the bug is fixed.
    request_id = ''.join(random.choices(string.digits, k=6))
    context.request_id = request_id  # type: ignore

    with self._report_index_manager.AllocateNextIndex() as report_index_entry:
      with self._SaveFileAsZst(self._REPORT_DATA_DIR, 'rpt', request_iterator,
                               context) as writer:
        report_index_entry_str = json_utils.DumpStr(report_index_entry,
                                                    pretty=False, newline=True)
        writer.write(report_index_entry_str.encode('utf8'))
      return empty_pb2.Empty()

  def SyncDeviceTime(
      self,
      request: umpire_dut_commands_pb2.SyncDeviceTimeRequest,
      context: grpc.ServicerContext,
  ) -> umpire_dut_commands_pb2.SyncDeviceTimeResponse:
    """Synchronizes the DUT's time zone to the Umpire server's time zone."""
    logging.info('SyncDeviceTime: peer: %s', context.peer())
    connected = False
    try:
      target = request.target or _ParseIpFromPeer(context.peer())
      epoch_time = int(time.time())

      _AdbConnect(target)
      connected = True
      _AdbRoot(target)

      logging.info('Setting device time to host epoch: %d', epoch_time)
      set_date_cmd = ['adb', '-s', target, 'shell', f'date @{epoch_time}']
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
      if connected:
        _AdbDisconnect(target)
    return umpire_dut_commands_pb2.SyncDeviceTimeResponse(
        success=True,
        messages=f'Successfully synced time on {target} to epoch {epoch_time}')

  def UploadCSR(self, request_iterator: Iterator[
      umpire_dut_commands_pb2.UploadFileRequest],
                context: grpc.ServicerContext) -> empty_pb2.Empty:
    with self._SaveFileAsZst(self._CSR_DATA_DIR, 'jsonl', request_iterator,
                             context) as _:
      pass
    return empty_pb2.Empty()
