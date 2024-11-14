# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Run grpc servers."""

import os

from cros.factory.umpire.server.service import umpire_service
from cros.factory.umpire.server import umpire_env


LOG_FILENAME = 'umpire_grpc.log'
SERVICE_NAME = 'umpire_grpc'


class UmpireGrpc(umpire_service.UmpireService):
  """UmpireGrpc service.

  Example:
    svc = GetServiceInstance('umpire_grpc')
    procs = svc.CreateProcesses(umpire_config_dict, umpire_env)
    svc.Start(procs)
  """

  def CreateProcesses(self, umpire_config, env: umpire_env.UmpireEnv):
    """Creates list of processes via config.

    Args:
      umpire_config: Umpire config dict.
      env: UmpireEnv object.

    Returns:
      A list of ServiceProcess.
    """

    umpire_grpc_config = umpire_config.get('services', {}).get(
        'umpire_grpc', {})
    log_path = os.path.join(env.log_dir, LOG_FILENAME)

    keyfile = umpire_grpc_config.get('key_file')
    certfile = umpire_grpc_config.get('cert_file')

    # 0.0.0.0 allows clients out of docker to call the rpc.
    # 127.0.0.1 only allows clients inside docker to call the rpc.
    args = [
        '--address',
        f'0.0.0.0:{env.umpire_grpc_port}',
        '--log-file',
        log_path,
        '--shopfloor-service-url',
        env.shopfloor_service_url,
        '--umpire-cli-url',
        f'http://127.0.0.1:{env.umpire_cli_port}',
    ]
    if keyfile and certfile:
      args.extend([
          '--keyfile',
          keyfile,
          '--certfile',
          certfile,
      ])

    script_path = os.path.join(env.server_toolkit_dir, 'py', 'umpire', 'server',
                               'grpc', 'run_grpc_server.py')
    proc_config = {
        'executable': script_path,
        'name': SERVICE_NAME,
        'args': args,
        'path': '/tmp',
        'env': os.environ
    }
    proc = umpire_service.ServiceProcess(self)
    proc.SetConfig(proc_config)
    return [proc]
