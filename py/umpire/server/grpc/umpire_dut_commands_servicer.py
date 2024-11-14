# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Umpire DUT remote procedures.

This is the gRPC implementation of
cros.factory.umpire.server.rpc_dut.UmpireDUTCommands.
"""

import json
import logging
import tempfile
from typing import cast
import xmlrpc.client

import grpc

from cros.factory.umpire.server.proto import umpire_dut_commands_pb2
from cros.factory.umpire.server.proto import umpire_dut_commands_pb2_grpc
from cros.factory.umpire.server import resource
from cros.factory.umpire.server import rpc_cli
from cros.factory.utils import process_utils


class UmpireDUTCommandsServicer(
    umpire_dut_commands_pb2_grpc.UmpireDUTCommandsServicer):

  def __init__(self, umpire_cli_url: str) -> None:
    super().__init__()
    self.CLI_command = cast(rpc_cli.CLICommand,
                            xmlrpc.client.ServerProxy(umpire_cli_url))

  def UpdateFactoryApp(self,
                       request: umpire_dut_commands_pb2.UpdateFactoryAppRequest,
                       context: grpc.ServicerContext):
    target = request.target
    logging.info('target: %s, peer: %s', target, context.peer())
    try:
      config = json.loads(self.CLI_command.GetActiveConfig())
      bundle_id = config['active_bundle_id']
      with tempfile.NamedTemporaryFile('+ab', suffix='.apk') as f:
        self.CLI_command.ExportPayload(
            bundle_id, resource.PayloadTypes.toolkit.name, f.name)
        process_utils.CheckCall(['adb', 'connect', target], log=True,
                                log_stderr_on_error=True)
        process_utils.CheckCall(['adb', '-s', target, 'root'], log=True,
                                log_stderr_on_error=True)
        process_utils.CheckCall(['adb', '-s', target, 'install', '-t', f.name],
                                log=True, log_stderr_on_error=True)
    except Exception as err:
      return umpire_dut_commands_pb2.UpdateFactoryAppResponse(
          success=False, messages=str(err))
    return umpire_dut_commands_pb2.UpdateFactoryAppResponse(
        success=True, messages='')
