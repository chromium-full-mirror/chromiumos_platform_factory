# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tests keyboard functionality.

Description
-----------
This test check basic keyboard functionality by asking operator to press each
keys on keyboard once at a time.

The layout of the keyboard is derived from vpd 'region' value, and can be
overwritten by argument ``layout``.

If ``allow_multi_keys`` is True, the operator can press multiple keys at once
to speed up the testing.

If ``sequential_press`` or ``strict_sequential_press`` is True, the operator
have to press each key in order from top-left to bottom-right. Additionally, if
``strict_sequential_press`` is True, the test would fail if the operator press
the wrong key.

A dict ``repeat_times`` can be specified to indicate number of times each key
have to be pressed before the key is marked as checked.

The test would fail after ``timeout_secs`` seconds.

Test Procedure
--------------
1. The test shows an image of the keyboard, and each key labeled with how many
   times it need to be pressed.
2. Operator press each key the number of times needed, and keys on UI would be
   marked as such.
3. The test pass when all keys have been pressed for the number of times
   needed, or fail after ``timeout_secs`` seconds.

Dependency
----------
Depends on 'evdev' module to monitor key presses.

Examples
--------
To test keyboard functionality, add this into test list::

  {
    "pytest_name": "keyboard"
  }

To test keyboard functionality, allow multiple keys to be pressed at once, and
have a timeout of 10 seconds, add this into test list::

  {
    "pytest_name": "keyboard",
    "args": {
      "allow_multi_keys": true,
      "timeout_secs": 10
    }
  }

To test keyboard functionality, ask operator to press keys in order, skip
keycode [4, 5, 6], have keycode 3 be pressed 5 times, and other keys be pressed
2 times to pass, add this into test list::

  {
    "pytest_name": "keyboard",
    "args": {
      "sequential_press": true,
      "skip_keycodes": [4, 5, 6],
      "repeat_times": {
        "3": 5,
        "default": 2
      }
    }
  }

To test keyboard functionality, ask operator to press keys in order (and fail
the test if wrong key is pressed), and set keyboard layout to ISO, add this
into test list::

  {
    "pytest_name": "keyboard",
    "args": {
      "strict_sequential_press": true,
      "layout": "ISO"
    }
  }

To test keyboard functionality, ask operator to press [2,3] and [4,5] at the
same time, and have a timeout of 300 seconds, add this into test list::

  {
    "pytest_name": "keyboard",
    "args": {
      "key_combinations": [[2, 3], [4, 5]],
      "timeout_secs": 300
    }
  }
"""

import array
import ast
import fcntl
import os
import re
import struct
import time
from typing import List

from cros.factory.test.l10n import regions
from cros.factory.test import session
from cros.factory.test import test_case
from cros.factory.test.utils import evdev_utils
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import file_utils
from cros.factory.utils import process_utils

from cros.factory.external.py_lib import evdev


# Defined in "uapi/linux/input.h":
#   struct input_keymap_entry {
#   #define INPUT_KEYMAP_BY_INDEX (1 << 0)
#     __u8 flags;
#     __u8 len;
#     __u16 index;
#     __u32 keycode;
#     __u8 scancode[32];
#   };

_INPUT_KEYMAP_ENTRY = 'BBHI32B'
# Defined in "uapi/linux/input.h":
#  #define EVIOCGKEYCODE_V2 _IOR('E', 0x04, struct input_keymap_entry)
# See more details in "uapi/asm-generic/ioctl.h"
_EVIOCGKEYCODE_V2 = ((2 << 30) | (struct.calcsize(_INPUT_KEYMAP_ENTRY) << 16) |
                     (ord('E') << 8) | 0x04)

# Check acpigen_ps2_keybd.c for the definition.
_DEFAULT_FN_KEYCODES_IN_FIRST_ROW = [59, 60, 61, 62, 63, 64, 65, 66, 67, 68]
_ESC_KEY_CODE = 1
_POWER_KEY_CODE = 116
_LAST_FN_KEYCODES = [115, 116, 142, 183]


def IsStraussKeyboard():
  """Checks if the device under test (DUT) uses a Strauss keyboard.

  This function executes the `ectool inventory` command on the DUT and
  parses the output to determine if the keyboard is a Strauss model.

  Returns:
    True if the DUT has a Strauss keyboard, False otherwise.
  """
  output = process_utils.CheckOutput(['ectool', 'inventory'])
  for line in output.splitlines():
    # This is defined in ec_feature_names in ectool.cc
    if 'Strauss support' in line:
      return True
  return False


class KeyboardTest(test_case.TestCase):
  """Tests if all the keys on a keyboard are functioning. The test checks for
  keydown and keyup events for each key, following certain order if required,
  and passes if both events of all keys are received.

  Among the args are two related arguments:
  - sequential_press: a keycode is simply ignored if the key is not pressed
    in order
  - strict_sequential_press: the test failed immediately if a key is skipped.
  """
  related_components = (test_case.TestCategory.KEYBOARD, )

  ARGS = [
      Arg(
          'allow_multi_keys', bool, 'Allow multiple keys pressed '
          'simultaneously. (Less strictly checking '
          'with shorter cycle time)', default=False),
      Arg(
          'multi_keys_delay', (int, float), 'When ``allow_multi_keys`` is '
          '``False``, do not fail the test if the delay between the '
          'consecutivepresses is more than ``multi_keys_delay`` seconds.',
          default=0),
      Arg(
          'layout', str, 'Use specified layout other than derived from VPD. '
          'If None, the layout from the VPD is used.', default=None),
      Arg('timeout_secs', int, 'Timeout for the test.', default=30),
      Arg(
          'sequential_press', bool, 'Indicate whether keycodes need to be '
          'pressed sequentially or not.', default=False),
      Arg(
          'strict_sequential_press', bool, 'Indicate whether keycodes need to '
          'be pressed strictly sequentially or not.', default=False),
      Arg('board', str,
          'If presents, in filename, the board name is appended after layout.',
          default=''),
      Arg(
          'device_filter', (int, str),
          'If present, the input event ID or a substring of the input device '
          'name specifying which keyboard to test.', default=None),
      Arg(
          'key_order', list,
          'Specify the sequential order of the keys to press. Will use the '
          'order in .layout files if it is not specified.', default=[]),
      Arg(
          'fn_keycodes', list, 'The keycodes in the first row, esc and '
          'power/lock key are excluded.', default=None),
      Arg(
          'last_fn_keycode', int, 'The keycode of the last fn key in the first '
          'row. Note that it should be a lock or a power key', default=142),
      Arg('replacement_keymap', dict, 'Deprecated, please use fn_keycodes',
          default={}),
      Arg(
          'has_power_key', bool, 'If True, the last key in the first row will '
          'be a power key, otherwise it will be a lock key.', default=True),
      Arg('skip_keycodes', list, 'Keycodes to skip', default=[]),
      Arg('skip_power_key', bool, 'Deprecated, please use skip_keycodes.',
          default=False),
      Arg(
          'detect_long_press', bool, 'Detect long press event. Usually for '
          'detecting bluetooth keyboard disconnection.', default=False),
      Arg(
          'repeat_times', dict, 'A dict object {key_code: times} to specify '
          'number of presses required for keys specified in key code, e.g. '
          '``{"28": 3, "57": 5}``, then ENTER (28) shall be pressed 3 times '
          'while SPACE (57) shall be pressed 5 times. If you want all keys to '
          'be pressed twice, you can do: ``{"default": 2}``. '
          'You can find keycode mappings in /usr/include/linux/input.h',
          default={}),
      Arg('has_numpad', bool, 'The keyboard has a number pad or not.',
          default=False),
      Arg('vivaldi_keyboard', bool, 'Get function keys map from sysfs.',
          default=True),
      Arg(
          'key_combinations', list, 'The element in the list is a list of key '
          'codes, and these keys should be held at the same time to pass the '
          'test. It is recommended to test 8 keys at once.', default=[]),
  ]

  def setUp(self):
    # yapf: disable
    self.assertFalse(self.args.skip_power_key,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                     'skip_power_key is deprecated, please use skip_keycodes.')
    self.assertFalse(
        # yapf: disable
        self.args.replacement_keymap,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        'replacement_keymap is deprecated, please use fn_keycodes.')

    # yapf: disable
    self.assertFalse(self.args.allow_multi_keys and self.args.sequential_press,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                     'Sequential press requires one key at a time.')
    self.assertFalse(
        # yapf: disable
        self.args.allow_multi_keys and self.args.strict_sequential_press,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        'Strict sequential press requires one key at a time.')
    # yapf: disable
    self.assertTrue(self.args.multi_keys_delay >= 0,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                    'multi_keys_delay should be a positive number.')
    # yapf: disable
    if self.args.allow_multi_keys and self.args.multi_keys_delay > 0:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      session.console.warning('multi_keys_delay is not effective when '
                              'allow_multi_keys is set to True.')
    # yapf: disable
    if (not self.args.strict_sequential_press and  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        not self.args.sequential_press and self.args.key_order):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      session.console.warning('key_order is not effective if it is not '
                              'needed to press sequentially.')

    # yapf: disable
    if self.args.fn_keycodes and self.args.vivaldi_keyboard:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      session.console.warning('the fn_keycodes will be '
                              'overridden by vivaldi_keyboard.')

    # yapf: disable
    if self.args.key_combinations:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.assertFalse(
          # yapf: disable
          self.args.repeat_times,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          'repeat_times is not supported '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          'with key_combinations.')
      # yapf: disable
      self.assertFalse(self.args.key_order, 'key_order is not supported with '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
                       'key_combinations.')
      self.assertFalse(
          # yapf: disable
          self.args.strict_sequential_press,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          'strict_sequential_press is not supported with key_combinations.')
      self.assertFalse(
          # yapf: disable
          self.args.sequential_press, 'sequential_press is not '  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          'supported with key_combinations.')
      self.assertTrue(
          # yapf: disable
          self.args.allow_multi_keys or self.args.multi_keys_delay == 0,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          'multi_keys should be allowed when using key_combinations.')
      self.assertTrue(
          # yapf: disable
          all(comb for comb in self.args.key_combinations),  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          'Combination should have at least 1 key.')

    # Get the keyboard input device.
    try:
      self.keyboard_device = evdev_utils.FindDevice(
          # yapf: disable
          self.args.device_filter, evdev_utils.IsKeyboardDevice)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    except evdev_utils.MultipleDevicesFoundError:
      session.console.info(
          "Please set the test argument 'device_filter' to one of the name.")
      raise

    layout = self.GetKeyboardLayout()
    first_row_keys = self.GetKeycodesInFirstRow()
    main_keys = self.GetLayoutKeycodes(layout)
    flatten_main_keys = [
        key for keys_in_row in main_keys for key in keys_in_row
    ]
    numpad_layout = ('strauss_numpad'
                     # yapf: disable
                     if self.args.layout == 'STRAUSS' else 'numpad')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    numpad_keys = []
    # yapf: disable
    if self.args.has_numpad:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      numpad_keys = self.GetLayoutKeycodes(numpad_layout)
    else:
      # yapf: disable
      self.ui.HideElement('instruction-sequential-numpad')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    flatten_numpad_keys = [
        key for keys_in_row in numpad_keys for key in keys_in_row
    ]

    self.hold_keys = set()
    self.last_press_time = 0
    # yapf: disable
    self.frontend_proxy = self.ui.InitJSTestObject(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        'KeyboardTest', layout, first_row_keys, main_keys, numpad_keys)

    # yapf: disable
    default_number_to_press = self.args.repeat_times.get('default', 1)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.need_press_keys = {}
    # yapf: disable
    keycodes_to_skip = set(self.args.skip_keycodes)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    for key in set(flatten_main_keys) | set(first_row_keys) | set(
        flatten_numpad_keys):
      if key in keycodes_to_skip:
        self.frontend_proxy.Skip(key)
      else:
        # yapf: disable
        self.need_press_keys[key] = self.args.repeat_times.get(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
            str(key), default_number_to_press)

    self.next_index = 0
    # yapf: disable
    if self.args.sequential_press or self.args.strict_sequential_press:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      if self.args.key_order:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        self.key_order_list = self.args.key_order  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        invalid_key_order = [
            key for key in self.key_order_list if key in keycodes_to_skip
        ]
        if invalid_key_order:
          session.console.warning(
              '%s is specified in both key_order and'
              'skip_keycodes.', invalid_key_order)
      else:
        self.key_order_list = [
            key for key in first_row_keys + flatten_main_keys +
            flatten_numpad_keys if key not in keycodes_to_skip
        ]
    else:
      self.key_order_list = []
      # yapf: disable
      self.ui.HideElement('instruction-sequential')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.HideElement('instruction-sequential-numpad')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # yapf: disable
    if self.args.allow_multi_keys or self.args.multi_keys_delay == 0:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.ui.HideElement('instruction-single-key')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # yapf: disable
    if self.args.key_combinations:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      self.frontend_proxy.Hint(self.args.key_combinations[0], True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    self.dispatcher = evdev_utils.InputDeviceDispatcher(
        # yapf: disable
        self.keyboard_device, self.event_loop.CatchException(self.HandleEvent))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    testlog.UpdateParam('malfunction_key',
                        description='The keycode of malfunction keys')

  def GetKeycodesInFirstRow(self) -> list:
    # yapf: disable
    if self.args.vivaldi_keyboard:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      fn_keycodes = self.GetVivaldiKeycodes()
    # yapf: disable
    elif self.args.fn_keycodes:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      fn_keycodes = self.args.fn_keycodes  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    else:
      fn_keycodes = _DEFAULT_FN_KEYCODES_IN_FIRST_ROW

    last_key = (
        _POWER_KEY_CODE
        # yapf: disable
        if self.args.has_power_key else self.args.last_fn_keycode)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.assertIn(last_key, _LAST_FN_KEYCODES)
    return [_ESC_KEY_CODE] + fn_keycodes + [last_key]

  def _GetKeyboardMapping(self):
    """Gets the scancode to keycode mapping.

    Repeatedly request EVIOCGKEYCODE_V2 ioctl on device node with flag
    INPUT_KEYMAP_BY_INDEX to fetch scancode keycode translation table for an
    input device. Sequetially increase index until it returns error.
    """
    mapping = {}
    buf = array.array('b', [0] * struct.calcsize(_INPUT_KEYMAP_ENTRY))

    # NOTE:
    # 1. index is a __u16.
    # 2. INPUT_KEYMAP_BY_INDEX = (1 << 0)
    # See more details in the definition of input_keymap_entry.
    for i in range(1 << 16):
      struct.pack_into(_INPUT_KEYMAP_ENTRY, buf, 0, 1, 0, i, 0, *([0] * 32))
      try:
        ret_no = fcntl.ioctl(self.keyboard_device, _EVIOCGKEYCODE_V2, buf)
        if ret_no != 0:
          session.console.warning(
              'Failed to fetch keymap at index %d: return_code=%d', i, ret_no)
          continue
      except OSError:
        break

      keymap_entry = struct.unpack(_INPUT_KEYMAP_ENTRY, buf)
      scancode_len = keymap_entry[1]
      keycode = keymap_entry[3]
      scancode = int.from_bytes(keymap_entry[4:4 + scancode_len],
                                byteorder='little')

      # Mapping to KEY_RESERVED (0) means the scancode is not used.
      if keycode != 0:
        mapping[scancode] = keycode
    return mapping

  def GetVivaldiKeycodes(self):
    """Gets the keycodes which are modifiable by partners, ESC is excluded."""
    match = re.search(r'\d+$', self.keyboard_device.path)
    if not match:
      raise RuntimeError('Failed to get keyboard device ID')
    event_id = match.group(0)
    file_content = file_utils.ReadFile(
        f'/sys/class/input/event{event_id}/device/device/function_row_physmap')
    scancode_to_keycode = self._GetKeyboardMapping()

    return [
        scancode_to_keycode[int(s, 16)]
        for s in file_content.strip().split()
        if int(s, 16) != 0
    ]

  def GetKeyboardLayout(self):
    """Uses the given keyboard layout or auto-detect from VPD."""
    # yapf: disable
    board = f'_{self.args.board}' if self.args.board else ''  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    if self.args.layout:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      return self.args.layout + board  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    # Use the primary keyboard_layout for testing.
    strauss = 'STRAUSS_' if IsStraussKeyboard() else ''
    region = process_utils.CheckOutput(['vpd', '-g', 'region']).strip()
    return strauss + regions.REGIONS[region].keyboard_mechanical_layout + board

  def GetLayoutKeycodes(self, layout) -> List[List[int]]:
    """Return a 2-D array for rendering the keyboard of different layout.

    Each element represents the keycodes in a row."""
    # yapf: disable
    layout_filename = os.path.join(self.ui.GetStaticDirectoryPath(),  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                                   layout + '.layout')
    return ast.literal_eval(file_utils.ReadFile(layout_filename))

  def HandleEvent(self, event):
    """Handler for evdev events."""
    # yapf: disable
    if event.type != evdev.ecodes.EV_KEY:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      return
    if event.value == 1:
      self.OnKeydown(event.code)
    elif event.value == 0:
      self.OnKeyup(event.code)
    # yapf: disable
    elif self.args.detect_long_press and event.value == 2:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      fail_msg = f'Got events on keycode {event.code} pressed too long.'
      session.console.error(fail_msg)
      self.FailTask(fail_msg)

  def OnKeydown(self, keycode):
    """Callback when got a keydown event from evdev."""
    if keycode not in self.need_press_keys:
      session.console.warning('Got key down event on an excluded keycode %d',
                              keycode)
      return

    # yapf: disable
    if (not self.args.allow_multi_keys and self.hold_keys and  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        time.time() - self.last_press_time < self.args.multi_keys_delay):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.FailTask(
          f'Got key down event on keycode {keycode} but there are other key '
          f'pressed: {next(iter(self.hold_keys))}.')

    if keycode in self.hold_keys:
      self.FailTask(f'Got 2 key down events on keycode {keycode} but didn\'t '
                    'get key up event.')

    # yapf: disable
    self.last_press_time = time.time()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.hold_keys.add(keycode)
    self.frontend_proxy.Hold(keycode, self.need_press_keys[keycode])

  def OnKeyup(self, keycode):
    """Callback when got a keyup event from evdev."""
    if keycode not in self.need_press_keys:
      return

    if keycode not in self.hold_keys:
      self.FailTask(
          f'Got key up event for keycode {keycode} but did not get key down '
          'event.')

    # yapf: disable
    if self.args.key_combinations:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      if self.next_index == len(self.args.key_combinations):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        return
      # yapf: disable
      keys = self.args.key_combinations[self.next_index]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      if self.hold_keys == set(keys):
        self.next_index += 1
        # yapf: disable
        if self.next_index == len(self.args.key_combinations):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          self.PassTask()
      self.hold_keys.remove(keycode)
      self.frontend_proxy.Click(keycode, 1)  # Restore the color of the key.
      if not self.hold_keys:
        # yapf: disable
        self.frontend_proxy.Hint(self.args.key_combinations[self.next_index],  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
                                 True)
      return

    self.hold_keys.remove(keycode)

    if (self.next_index < len(self.key_order_list) and
        keycode in self.key_order_list):
      next_key = self.key_order_list[self.next_index]
      if keycode != next_key:
        # yapf: disable
        if self.args.strict_sequential_press:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
          # yapf: enable
          self.FailTask(f'Expect keycode {next_key} but get {keycode}.')
        else:
          self.frontend_proxy.Click(keycode, self.need_press_keys[keycode])
          return
      if self.need_press_keys[keycode] == 1:
        self.next_index += 1

    if self.need_press_keys[keycode] > 0:
      self.need_press_keys[keycode] -= 1

    self.frontend_proxy.Click(keycode, self.need_press_keys[keycode])
    if max(self.need_press_keys.values()) == 0:
      self.PassTask()

  def FailTestTimeout(self):
    """Fail the test due to timeout, and log untested keys."""
    # yapf: disable
    if self.args.key_combinations:  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      # yapf: disable
      failed_keys = self.args.key_combinations[self.next_index:]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    else:
      failed_keys = [
          key for key, num_left in self.need_press_keys.items() if num_left
      ]
    for failed_key in failed_keys:
      testlog.LogParam('malfunction_key', failed_key)
    self.FailTask(f'Keyboard test timed out. Malfunction keys: {failed_keys}.')

  def runTest(self):
    self.keyboard_device.grab()
    self.dispatcher.StartDaemon()
    # yapf: disable
    self.ui.StartCountdownTimer(self.args.timeout_secs, self.FailTestTimeout)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self.WaitTaskEnd()

  def tearDown(self):
    """Terminates the running process or we'll have trouble stopping the test.
    """
    self.dispatcher.Close()
    self.keyboard_device.ungrab()
