# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test display functionality with interactive mode.

Description
-----------
This test runs in interactive mode and allows external control via an XML-RPC
server. A host (e.g., test station) can connect to this DUT to interact with
the test and control the display.

Supported XML-RPC Functions:
  - GetSerialNumber: Retrieves the DUT device serial number.
  - ShowPattern: Displays a pattern on the DUT screen. The pattern can be
    defined in CSS or specified as an image file name (without extension).
    Multiple patterns can be shown sequentially, with the previous
    pattern being hidden before the new one is displayed.
  - SetDisplayBrightness: Sets the brightness level of the display.
  - JudgeTestResult: Judges the given test result. The result should be either
    'PASS' or 'FAIL'. A failure reason can be provided when the result is
    'FAIL'.

Test Procedure
--------------
  1. The test starts an XML-RPC server on the specified port.
  2. If the 'autostart' argument is set to True, the test automatically
     enters fullscreen mode and sets the display brightness to maximum.
  3. The test waits for the host to invoke XML-RPC functions to control
     the display and judge the test result.

Dependency
----------
- This test uses an XML-RPC server.
- The 'iptables' command is used to configure firewall rules.

Examples
--------
To start the test in interactive mode:

.. test_list::

  generic_display_panel_examples:DisplayPanelTests.
  EnterFrontOfScreenTestInteractiveMode

"""

import logging
import os
import socketserver
import threading
import time
from typing import Optional, Protocol
import xmlrpc.server

from cros.factory.device import device_utils
from cros.factory.test import device_data
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import process_utils


class _DisplayInteractiveArgs(Protocol):
  """Arguments for the DisplayInteractiveTest."""
  port: int
  autostart: bool
  timeout_secs: int


class ThreadXMLRPCServer(socketserver.ThreadingMixIn,
                         xmlrpc.server.SimpleXMLRPCServer):
  """A threaded XML-RPC server."""


class DisplayInteractiveTest(test_case.TestCase):
  """Provides interactive display testing functionality over XML-RPC.

  This test enables external control of display patterns and brightness
  for testing purposes.
  """

  related_components = (test_case.TestCategory.LCD, )
  ARGS = [
      Arg('autostart', bool,
          'Automatically start the test and enter fullscreen mode',
          default=False),
      Arg('port', int, 'XML-RPC server port', default=5566),
      Arg('timeout_secs', int, 'Test timed out waiting for result', default=300)
  ]

  args: _DisplayInteractiveArgs
  ui: test_ui.UI

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self._static_dir = self.ui.GetStaticDirectoryPath()
    self._frontend_proxy = self.ui.InitJSTestObject('DisplayInteractiveTest')

    self._result: Optional[str] = None
    self._reason: Optional[str] = None
    self._server: Optional[ThreadXMLRPCServer] = None

    # Set firewall rules to allow XML-RPC server listen on port.
    process_utils.Spawn([
        'iptables', '-A', 'INPUT', '-p', 'tcp', '--dport',
        str(self.args.port), '-j', 'ACCEPT'
    ], check_call=True)

    self.ui.BindStandardFailKeys()

    # Launch the XML-RPC server in a separate thread.
    self._server_thread = threading.Thread(target=self._RunAsServer,
                                           daemon=True)
    self._server_thread.start()

    self._start_time = time.time()

  def runTest(self):
    """Main test execution."""
    if not self.args.autostart:
      self.ui.WaitKeysOnce(test_ui.SPACE_KEY)

    self.SetDisplayBrightness(1.0)

    # Automatically toggle fullscreen and show a default pattern.
    self._frontend_proxy.ToggleFullscreen()
    self.ShowPattern(
        'message',
        'Display interactive test. Please connect to the test station...')

    self.JudgeTestResult(self._result, self._reason)

  def _RunAsServer(self):
    """Runs the XML-RPC server in a separate thread."""
    with ThreadXMLRPCServer(('0.0.0.0', self.args.port),
                            allow_none=True) as server:
      self._server = server
      self._server.register_introspection_functions()
      self._server.register_instance(self)
      logging.info('XML-RPC server started on port %d', self.args.port)
      server.serve_forever()

  def tearDown(self):
    """Cleans up the test environment."""
    self.SetDisplayBrightness(0.5)

    # Stop the XML-RPC server if it's running.
    if self._server is not None:
      self._server.shutdown()
      logging.info('XML-RPC server stopped.')

  @classmethod
  def GetSerialNumber(cls) -> str:
    """Retrieves the DUT's serial number.

    Returns:
      str: The serial number of the device.
    """
    return device_data.GetSerialNumber('serial_number')

  def SetDisplayBrightness(self, brightness: float) -> None:
    """Sets the display brightness.

    Args:
      brightness: The desired brightness level between 0.0 and 1.0.
    """
    self._dut.display.SetBacklightBrightness(brightness)

  def ShowPattern(self, pattern_type: str, pattern: str,
                  ext: str = 'png') -> None:
    """Displays a pattern on the DUT screen.

    Args:
      pattern_type: Type of pattern, either 'css' or 'image'.
      pattern: The pattern to be displayed.
        For 'css', it's a CSS file name.
        For 'image', it's an image file name without extension.
      ext: The extension of the image file, defaults to 'png'.
    """
    if pattern_type not in ('css', 'image', 'message'):
      self.JudgeTestResult(f'Invalid pattern type: {pattern_type!r}')

    if pattern_type == 'image':
      image_path = os.path.join(self._static_dir, f'{pattern}.{ext}')
      if not os.path.exists(image_path):
        self.JudgeTestResult(f'Image file {image_path} does not exist.')
      pattern = f'{pattern}.{ext}'

    self._frontend_proxy.ShowPattern(pattern_type, pattern)

  def JudgeTestResult(self, result: Optional[str],
                      reason: Optional[str] = None) -> None:
    """Judges the test result.

    Args:
      result: The test result, should be 'PASS', 'FAIL', or None.
              If result is None, the function will wait for the result
              to be set by other methods.
      reason: Optional reason for failure.
    """
    self._result = result
    self._reason = reason
    while self._result is None:
      # Wait until the test result is set.
      time.sleep(0.1)
      if time.time() - self._start_time > self.args.timeout_secs:
        self.FailTask('Test timed out waiting for result.')
    if self._result == 'PASS':
      self.PassTask()
    elif self._result == 'FAIL':
      self.FailTask(f'Test result: {self._result} - {self._reason}' if self
                    ._reason else f'Test result: {self._result}')
    else:
      self.FailTask(f'Test Fail: Invalid test result: {self._result}')
