# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import contextlib
import os
import re
import sysconfig
import time
from types import TracebackType
from typing import Callable, Optional, Type

from cros.factory.utils import file_utils
from cros.factory.utils import process_utils


_SERVOD_BIN = 'servod'
_DUT_CONTROL_TIMEOUT_SEC = 10
_SERVOD_INIT_TIMEOUT_SEC = 10
_SERVOD_KILL_TIMEOUT_SEC = 3

# Directory where hdctools installs configuration files into.
_LIB_DIR = os.getenv(
    'PATH_SERVO_DATA',
    os.path.join(sysconfig.get_path('purelib'), 'servo', 'data'))


def GetSupportedBoards() -> list[str]:
  """The supported boards for the web UI."""
  all_boards: list[str] = []
  regex = r'servo_([a-zA-Z0-9\-]+)_overlay.xml'
  for unused_root, unused_dirs, files in os.walk(_LIB_DIR):
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

  def __init__(self, port=9999, board: Optional[str] = None,
               serial_name: Optional[str] = None):
    self._port = port
    self._servod_cmd = [_SERVOD_BIN, '-p', str(port)]
    self._servod_cmd += ['-b', board or 'none']
    if serial_name:
      self._servod_cmd += ['-s', serial_name]

    self._exit_stack = contextlib.ExitStack()

  @classmethod
  def _CheckServodHasInitialized(cls, dut_control: DutControl, stdout_file: str,
                                 stderr_file: str):
    """Wait until servod has initialized.

    If servod has stopped, RuntimeError should be raised.  If servod is
    initializing, dut_control should fail and CalledProcessError should be
    raised.
    """
    last_error: Optional[Exception] = None
    start = time.time()
    while time.time() - start < _SERVOD_INIT_TIMEOUT_SEC:
      try:
        dut_control.GetValue('servo_type')
        return
      except (process_utils.CalledProcessError,
              process_utils.TimeoutExpired) as e:
        last_error = e
    servod_logs = file_utils.ReadFile(stdout_file), file_utils.ReadFile(
        stderr_file)
    raise RuntimeError(
        f'Cannot initialize servod in {_SERVOD_INIT_TIMEOUT_SEC} seconds. '
        f'Last error: {last_error!r}. Servod logs: {servod_logs}')

  def _GetDutControl(self) -> DutControl:
    stdout_file = self._exit_stack.enter_context(
        file_utils.UnopenedTemporaryFile())
    stderr_file = self._exit_stack.enter_context(
        file_utils.UnopenedTemporaryFile())

    with open(stdout_file, 'w', encoding='utf8') as stdout, open(
        stderr_file, 'w', encoding='utf8') as stderr:
      # TODO(b/343624632): remove `I_NEED_SERVOD` when we drop support for the
      # HWID extractor in the chroot environment.
      servod_process = process_utils.Spawn(
          self._servod_cmd, stdout=stdout, stderr=stderr, env=dict(
              os.environ, I_NEED_SERVOD='1'))
    self._exit_stack.callback(process_utils.TerminateOrKillProcess,
                              servod_process, _SERVOD_KILL_TIMEOUT_SEC)

    def CheckServodAlive():
      if servod_process.poll() is None:
        return
      servod_logs = file_utils.ReadFile(stdout_file), file_utils.ReadFile(
          stderr_file)
      raise RuntimeError(
          f'Servod unexpectedly stopped. Servod logs: {servod_logs}')

    dut_control = DutControl(self._port, CheckServodAlive)
    self._CheckServodHasInitialized(dut_control, stdout_file, stderr_file)
    return dut_control

  def __enter__(self) -> DutControl:
    self._exit_stack.__enter__()
    try:
      return self._GetDutControl()
    except Exception:
      self._exit_stack.close()
      raise

  def __exit__(self, exc_type: Optional[Type[BaseException]],
               exc_val: Optional[BaseException],
               exc_tb: Optional[TracebackType]):
    self._exit_stack.__exit__(exc_type, exc_val, exc_tb)
