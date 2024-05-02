# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Check the retimer firmware version.

Description
-----------
Verifies the retimer firmware version.

Retimer device gets enumerated if the port connect to nothing when booting and
it offlines itself if there is no updates to perform. We need to poke registers
to enumerate the retimer. See b/299950312#comment2 for more information.

Test Procedure
--------------
1. Operator to remove all devices from usb type c ports.
2. The device enumerates retimers.
3. The test compares the actual version and the expected version.
4. The device offlines retimers.

Dependency
----------
- The retimer device node must support nvm_version.

Examples
--------
The minimal working example::

  {
    "CheckRetimerFirmware": {
      "pytest_name": "check_retimer_firmware",
      "args": {
        "controller_ports": [
          "0-0:1.1",
          "0-0:3.1"
        ],
        "usb_ports": [
          0,
          1
        ],
        "min_retimer_version": "21.0"
      }
    }
  }
"""

from distutils import version
import logging
import os

from cros.factory.device import device_utils
from cros.factory.device import sensor_utils
from cros.factory.test.i18n import _
from cros.factory.test.rules import phase
from cros.factory.test import test_case
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import sync_utils


_RETIMER_VERSION_PATH = '/sys/bus/thunderbolt/devices/%s/nvm_version'
_CONTROLLER_PORTS = ('0-0:1.1', '0-0:3.1', '1-0:1.1', '1-0:3.1')
_CONTROLLER_PORTS_PREFIX = ('0-0', '1-0')



class RetimerFirmwareTest(test_case.TestCase):
  """Retimer firmware test."""
  related_components = tuple()


  ARGS = [
      Arg('wait_all_ports_unplugged', bool, 'Deprecated', default=None),
      Arg('controller_ports', list,
          ('All the controller ports that we want ot test. Must be a subset of '
           f'{_CONTROLLER_PORTS!r}'), default=None),
      Arg('usb_ports', list, ('All the usb ports that we want ot test.'),
          default=None),
      Arg('min_retimer_version', str,
          ('The minimum Retimer firmware version. Set to None to disable the '
           'check.'), default=None),
      Arg('max_retimer_version', str,
          ('The maximum Retimer firmware version. Set to None to disable the '
           'check.'), default=None),
      Arg('timeout_secs', int,
          ('Timeout in seconds when we ask operator to complete the challenge.'
           ' None means no timeout.'), default=30),
  ]

  def setUp(self):
    self.ui.ToggleTemplateClass('font-large', True)  # type: ignore #TODO(b/338318729) Fixit!
    self._dut = device_utils.CreateDUTInterface()
    self.controller_ports = self.args.controller_ports  # type: ignore #TODO(b/338318729) Fixit!
    self.usb_ports = self.args.usb_ports  # type: ignore #TODO(b/338318729) Fixit!
    if not set(_CONTROLLER_PORTS).issuperset(self.controller_ports):
      raise ValueError(f'controller_ports {self.controller_ports!r} must be a '
                       f'subset of {_CONTROLLER_PORTS!r}.')
    phase.AssertStartingAtPhase(phase.PVT, self.args.min_retimer_version,  # type: ignore #TODO(b/338318729) Fixit!
                                'min_retimer_version must be specified.')

  def _CheckOneRetimer(self, controller_port: str):
    """Check the firmware version of the retimer.

    Args:
      controller_port: The target controller port.

    Raises:
      type_utils.TimeoutError: The device does not get enumerated.
      ValueError: If the version does not meet the constraints.
    """
    retimer_version_path = _RETIMER_VERSION_PATH % controller_port
    logging.info('cat %s', retimer_version_path)

    version_string = self._dut.ReadFile(retimer_version_path)
    retimer_version = version.LooseVersion(version_string.strip())
    logging.info('retimer_version %s', retimer_version)

    self.ui.SetState(_('Checking the retimer firmware version...'))  # type: ignore #TODO(b/338318729) Fixit!
    if self.args.min_retimer_version:  # type: ignore #TODO(b/338318729) Fixit!
      min_retimer_version = version.LooseVersion(self.args.min_retimer_version)  # type: ignore #TODO(b/338318729) Fixit!
      if retimer_version < min_retimer_version:
        raise ValueError(
            f'retimer_version {retimer_version} < min_retimer_version '
            f'{min_retimer_version}')

    if self.args.max_retimer_version:  # type: ignore #TODO(b/338318729) Fixit!
      max_retimer_version = version.LooseVersion(self.args.max_retimer_version)  # type: ignore #TODO(b/338318729) Fixit!
      if retimer_version > max_retimer_version:
        raise ValueError(
            f'retimer_version {retimer_version} > max_retimer_version '
            f'{max_retimer_version}')

  def _WaitOneUSBUnplugged(self, usb_port):
    """Waits until usb_port is disconnected."""
    test_timer = None
    if self.args.timeout_secs:  # type: ignore #TODO(b/338318729) Fixit!
      test_timer = self.ui.StartCountdownTimer(self.args.timeout_secs)  # type: ignore #TODO(b/338318729) Fixit!

    self.ui.SetState(  # type: ignore #TODO(b/338318729) Fixit!
        _('Please remove USB type-C cable from port {port}', port=usb_port))

    def _VerifyDisconnect():
      usbpd_verified, unused_mismatch = self._dut.usb_c.VerifyPDStatus({
          'connected': False,
          'port': usb_port,
      })
      return usbpd_verified

    sync_utils.WaitFor(_VerifyDisconnect, self.args.timeout_secs,  # type: ignore #TODO(b/338318729) Fixit!
                       poll_interval=0.5)
    if test_timer:
      test_timer.set()

  def _WaitUSBUnplugged(self):
    """Waits until all ports in self.usb_ports are disconnected."""
    for usb_port in self.usb_ports:
      self._WaitOneUSBUnplugged(usb_port)
    self.ui.SetInstruction('')  # type: ignore #TODO(b/338318729) Fixit!

  def _RetimerSwitcher(self, controller_port_prefix, mode):
    retimer_switcher_path = self._GetRetimerSwitcherPath(controller_port_prefix)
    if mode == 'ON':
      self.ui.SetState(_('Enumerating Retimer...'))  # type: ignore #TODO(b/338318729) Fixit!
      self._dut.CheckCall(f'echo 1 > {retimer_switcher_path}/offline')
      self._dut.CheckCall(f'echo 1 > {retimer_switcher_path}/rescan')
    else:
      self._dut.CheckCall(f'echo 0 > {retimer_switcher_path}/offline')

  def _GetRetimerSwitcherPath(self, controller_port_prefix):
    pattern = (f'/sys/bus/thunderbolt/devices/{controller_port_prefix}'
               '/usb4_port?/offline')
    path = sensor_utils.FindDevice(self._dut, pattern, allow_multiple=False)
    retimer_switcher_path = os.path.dirname(path)
    logging.info('Found retimer switcher path at %s.', retimer_switcher_path)
    return retimer_switcher_path

  def runTest(self):
    errors = {}
    self._WaitUSBUnplugged()
    for controller_port_prefix in _CONTROLLER_PORTS_PREFIX:
      if any(
          controller_port.startswith(controller_port_prefix)
          for controller_port in self.controller_ports):
        self._RetimerSwitcher(controller_port_prefix, 'ON')
        self.addCleanup(self._RetimerSwitcher, controller_port_prefix, 'OFF')
    for controller_port in self.controller_ports:
      try:
        self._CheckOneRetimer(controller_port)
      except Exception as e:
        errors[controller_port] = e
    if errors:
      self.FailTask(errors)
