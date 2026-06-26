# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import contextlib
import os
import re
import subprocess
import time
from types import TracebackType
from typing import Callable, Optional, Type

from cros.factory.utils import file_utils
from cros.factory.utils import process_utils


_DUT_CONTROL_TIMEOUT_SEC = 10
_SERVOD_INIT_TIMEOUT_SEC = 10
_PROCESS_KILL_TIMEOUT_SEC = 3

# Directory where hdctools installs configuration files into.
_SERVO_DATA_DIR = os.path.realpath(os.environ['PATH_SERVO_DATA'])
_SERVOD_BIN = 'servod'
_GRPC_SERVER_SETUP_SCRIPT = os.path.join(_SERVO_DATA_DIR, 'grpc_server',
                                         'grpc_server_setup.py')


def GetSupportedBoards() -> list[str]:
  """The supported boards for the web UI."""
  all_boards: list[str] = []
  regex = r'servo_([a-zA-Z0-9\-]+)_overlay.xml'
  for unused_root, unused_dirs, files in os.walk(_SERVO_DATA_DIR):
    for filename in files:
      res = re.fullmatch(regex, filename)
      if res:
        all_boards.append(res.group(1))
  return sorted(all_boards)


class DutControl:

  def __init__(self, port: int, check_servod_callback: Callable[[], None]):
    self._base_cmd = ['dut-control', f'--port={port}']
    self._check_servod_callback = check_servod_callback

  def _Execute(self, args: list[str]) -> str:
    self._check_servod_callback()
    return process_utils.CheckOutput(self._base_cmd + args, read_stderr=True,
                                     timeout=_DUT_CONTROL_TIMEOUT_SEC)

  def GetValue(self, arg: str) -> str:
    """Gets the value of `arg` from dut_control."""
    return self._Execute(['--value_only', arg]).strip()

  def Run(self, args: list[str]) -> None:
    """Runs a dut_control command.

    Args:
      args: The dut_control command to run.
    """
    self._Execute(args)


class Servod:
  """Run servod and get the interface to execute dut-control commands.

  Args:
    port: The port to run servod.
    board: The board argument of servod. The addition board configuration will
    be loaded.
    serial_name: The serial_name argument of servod. It is necessary if there
    are multiple servo connections.
  """

  _servod_process: subprocess.Popen
  _servod_stdout_file: str
  _servod_stderr_file: str

  def __init__(self, port=9999, board: Optional[str] = None,
               serial_name: Optional[str] = None):
    self._port = port
    self._servod_cmd = [
        _SERVOD_BIN, '-p',
        str(port), "--grpc-core-port", "50052", "--grpc-data-host", "localhost",
        "--grpc-data-port", "50051"
    ]
    self._servod_cmd += ['-b', board or 'none']
    if serial_name:
      self._servod_cmd += ['-s', serial_name]

    self._exit_stack = contextlib.ExitStack()

  def _GenerateTempFile(self) -> str:
    return self._exit_stack.enter_context(file_utils.UnopenedTemporaryFile())

  def _RunServod(self) -> None:
    self._servod_stdout_file = self._GenerateTempFile()
    self._servod_stderr_file = self._GenerateTempFile()

    with open(self._servod_stdout_file, 'w', encoding='utf8') as stdout, open(
        self._servod_stderr_file, 'w', encoding='utf8') as stderr:
      self._servod_process = process_utils.Spawn(self._servod_cmd,
                                                 stdout=stdout, stderr=stderr)
    self._exit_stack.callback(process_utils.TerminateOrKillProcess,
                              self._servod_process, _PROCESS_KILL_TIMEOUT_SEC)

  def _WaitUntilServodReady(self, dut_control: DutControl):
    """Wait until servod is ready.

    If servod has stopped, RuntimeError should be raised.  If servod is
    initializing, dut_control should fail and CalledProcessError should be
    raised.
    """
    last_error: Optional[Exception] = None
    deadline = time.time() + _SERVOD_INIT_TIMEOUT_SEC
    while time.time() < deadline:
      try:
        dut_control.GetValue('servo_type')
        return
      except (process_utils.CalledProcessError,
              process_utils.TimeoutExpired) as e:
        last_error = e
    servod_logs = self._GetServodLogs()
    raise RuntimeError(
        f'Cannot initialize servod in {_SERVOD_INIT_TIMEOUT_SEC} seconds.\n' +
        servod_logs) from last_error

  def _CheckServodAlive(self) -> None:
    if self._servod_process.poll() is None:
      return
    servod_logs = self._GetServodLogs()
    raise RuntimeError(f'Servod unexpectedly stopped.\n{servod_logs}')

  def _GetServodLogs(self) -> str:
    stdout = file_utils.ReadFile(self._servod_stdout_file)
    stderr = file_utils.ReadFile(self._servod_stderr_file)
    return f"${stdout}\n{stderr}"

  def _RunServoGrpcService(self) -> None:
    cmd = [
        'python3', _GRPC_SERVER_SETUP_SCRIPT, "--grpc-core-host", "localhost",
        "--grpc-core-port", "50052", "--grpc-data-port", "50051", "--logs",
        f"/var/log/servod_${self._port}"
    ]
    process = process_utils.Spawn(cmd, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
    self._exit_stack.callback(process_utils.TerminateOrKillProcess, process,
                              _PROCESS_KILL_TIMEOUT_SEC)

  def __enter__(self) -> DutControl:
    try:
      self._RunServoGrpcService()
      self._RunServod()
      dut_control = DutControl(self._port, self._CheckServodAlive)
      self._WaitUntilServodReady(dut_control)
      return dut_control
    except Exception:
      self._exit_stack.close()
      raise

  def __exit__(self, exc_type: Optional[Type[BaseException]],
               exc_val: Optional[BaseException],
               exc_tb: Optional[TracebackType]):
    self._exit_stack.__exit__(exc_type, exc_val, exc_tb)
