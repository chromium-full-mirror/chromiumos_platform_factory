# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Fastboot service for umpire resources."""

import os

from cros.factory.umpire.common import UmpireError
from cros.factory.umpire.server.service import umpire_service
from cros.factory.utils import file_utils


LOG_FILENAME = 'fastboot_service.log'
SERVICE_NAME = 'fastboot_service'


class FastbootService(umpire_service.UmpireService):
  """Fastboot service for image installation."""

  def CreateProcesses(self, umpire_config, env):
    fastboot_service_config = umpire_config['services']['fastboot_service']

    # For an imaging service, the log can be too big if the imaging session
    # gets longer. Purge previous log if possible when starting new services.
    log_path = os.path.join(env.log_dir, LOG_FILENAME)
    file_utils.TryUnlink(log_path)

    ip_list = []
    if 'dut_ip_addrs' in fastboot_service_config:
      for addr in fastboot_service_config['dut_ip_addrs']:
        ip_list.append(addr['dut_ip'])

    interfaces = {}
    if 'broadcast_ping' in fastboot_service_config and fastboot_service_config[
        'broadcast_ping'] is not None:
      if len(fastboot_service_config['broadcast_ping']) == 0:
        raise UmpireError(
            'Network interface cannot be blank when broadcast ping is enabled.')
      for interface in fastboot_service_config['broadcast_ping'][
          'network_interfaces']:
        interfaces[interface['interface_name']] = interface['broadcast_address']
    elif len(ip_list) == 0:
      raise UmpireError('IP cannot be blank to start fastboot service.')

    scan_interval = 10
    if 'scan_interval' in fastboot_service_config:
      try:
        scan_interval = int(fastboot_service_config['scan_interval'])
        if scan_interval <= 0:
          raise ValueError('Scan interval cannot be 0 or negative number.')
      except ValueError as e:
        raise UmpireError('Cannot set interval with invalid values.') from e

    idle_timeout = 300
    if 'idle_timeout' in fastboot_service_config:
      try:
        idle_timeout = int(fastboot_service_config['idle_timeout'])
      except ValueError as e:
        raise UmpireError('Cannot set idle timeout with invalid values.') from e

    if ('board_name' not in fastboot_service_config or
        not fastboot_service_config['board_name']):
      raise UmpireError('Please input board name for orchestrator to run.')

    if ('model_name' not in fastboot_service_config or
        not fastboot_service_config['model_name']):
      raise UmpireError('Please input model name for orchestrator to run.')

    script_path = os.path.join(env.server_toolkit_dir, 'py', 'fastboot',
                               'fastboot_orchestrator.py')

    proc_list = []

    args = [
        '-v', '-s', env.fastboot_img_dir, '-p',
        fastboot_service_config['model_name'], '-b',
        fastboot_service_config['board_name'], '-t',
        str(scan_interval), '-l', log_path, '--idle_timeout',
        str(idle_timeout)
    ]

    if ip_list:
      args.append('-i')
      args.extend(ip_list)

    for interface_name, broadcast_addr in interfaces.items():
      args.extend(['-bi', interface_name, broadcast_addr])
      broadcast_ping_url = os.getenv('BROADCAST_PING_SERVICE_URL', '')
      if not broadcast_ping_url:
        raise UmpireError('Please provide the broadcast ping service url.')
      args.extend(['-bu', broadcast_ping_url])

    if 'ufs_provision' in fastboot_service_config and fastboot_service_config[
        'ufs_provision']:
      args.extend([
          '--enable_ufs_provision', '--factory_ufs_binary_path',
          '/usr/local/factory/bin/factory_ufs'
      ])

    if ('clear_secure_storage' in fastboot_service_config and
        fastboot_service_config['clear_secure_storage']):
      args.extend(['--clear_secure_storage'])

    proc_config = {
        'executable': script_path,
        'name': SERVICE_NAME,
        'args': args,
        'path': '/tmp',
        'env': os.environ
    }

    proc = umpire_service.ServiceProcess(self)
    proc.SetConfig(proc_config)
    proc_list.append(proc)

    return proc_list
