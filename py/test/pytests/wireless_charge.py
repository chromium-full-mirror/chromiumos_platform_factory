# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test wireless charge port functionality.

Description
-----------
Verify wireless charging port functionality by asking operator to follow the
instructions by occupy/free charging port then probe the port status.

Test Procedure
--------------
1. Show instruction on screen and instruct operator to occupy port with
   peripheral, then press SPACE to probe state.
2. Show instruction on screen and instruct operator to free port with
   peripheral, then press SPACE to probe state.


Dependency
----------
- Based on ectool pchg <port>

Examples
--------
To test charging port 0::

  {
    "pytest_name": "wireless_charge",
    "args": {
      "port": 0,
      "occupy_instruction": "Attach stylus on the DUT right side",
      "release_instruction": "Remove stylus from the DUT right side"
    }
  }
"""

import enum

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test.i18n import arg_utils as i18n_arg_utils
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils.string_utils import ParseDict


class ChargeState(enum.Enum):
  """A subset of ectool pchg output state."""
  ENABLED = enum.auto()
  CHARGING = enum.auto()
  FULL = enum.auto()


class PortState(enum.Enum):
  Unknown = enum.auto()
  Occupied = enum.auto()
  Available = enum.auto()


def GetPortStateFromChargeState(charge_state):
  """Converts charge state to port state.

  CHARGING and FULL in ChargeState map to Occupied, whereas ENABLED maps to
  Available.
  """
  if charge_state in [ChargeState.CHARGING, ChargeState.FULL]:
    return PortState.Occupied
  if charge_state == ChargeState.ENABLED:
    return PortState.Available
  return PortState.Unknown


class WirelessChargeTest(test_case.TestCase):
  related_components = tuple()
  ARGS = [
      Arg('port', int, 'Wireless charging port to test.', default=0),
      i18n_arg_utils.I18nArg(
          'occupy_instruction',
          'Text to display the instruction to operator to occupy port',
          default='Attach peripheral to charging port'),
      i18n_arg_utils.I18nArg(
          'release_instruction',
          'Text to display the instruction to operator to release port',
          default='Remove peripheral from charging port'),
      Arg('timeout', int, 'Timeout of the test.', default=200)
  ]

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    # yapf: disable
    self.ui.SetState(_('Wireless Charge Port testing...'))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def runTest(self):
    # yapf: disable
    self.ui.StartFailingCountdownTimer(self.args.timeout)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # test port charge ability
    # yapf: disable
    self.InstructAndWaitStateFulfilled(self.args.occupy_instruction,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                                       PortState.Occupied)
    # test idling port
    # yapf: disable
    self.InstructAndWaitStateFulfilled(self.args.release_instruction,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                                       PortState.Available)

  def InstructAndWaitStateFulfilled(self, instruction, desired_state):
    """Waits until desired state is fulfilled.

    Args:
      instruction: test instruction displayed to operator
      desired_state: the desired PortState
    """
    # yapf: disable
    self.ui.SetInstruction(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        _('{instruction} then hit SPACE', instruction=instruction))
    while True:
      # yapf: disable
      self.ui.WaitKeysOnce(test_ui.SPACE_KEY)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      charge_state = self.GetPortChargingState()

      charge_state_info = f'Current port state: {charge_state.name}'
      # yapf: disable
      self.ui.SetState(charge_state_info)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      session.console.info(charge_state_info)

      if GetPortStateFromChargeState(charge_state) == desired_state:
        break

  def GetPortChargingState(self):  # pylint: disable=inconsistent-return-statements
    # yapf: disable
    cmd = f'ectool pchg {self.args.port}'  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    output = self._dut.CheckOutput(cmd, log=True)
    parsed_dict = ParseDict(output.split('\n'))
    self.assertIn('State', parsed_dict, msg=f'State not in output: {output}')
    # state field is composed of a state and a number, e.g. FULL (4)
    state_field_tokens = parsed_dict['State'].split()
    self.assertGreaterEqual(
        len(state_field_tokens), 1,
        msg=f'Invalid State field: {parsed_dict["State"]}')
    state = state_field_tokens[0]
    try:
      return ChargeState[state]
    except KeyError:
      self.FailTask(
          # yapf: disable
          f'The state of port {self.args.port}: {state} is unsupported!')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
