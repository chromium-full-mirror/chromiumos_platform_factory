# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A factory test for ambient light sensor.

Description
-----------
Tests that ambient light sensor reacts to both darkening by covering with
finger as well as brightening by shining with flashlight.

Test Procedure
--------------
When the test starts, all subtests will be listed on the screen.  Operator
needs to press ``SPACE`` to start subtests.

After ``SPACE`` is pressed, the first subtest will become ``ACTIVE`` and
operator should follow the instruction shown on the screen, e.g. "Cover light
sensor with finger".  The pytest will keep polling light sensor value, as soon
as the  value meets the requirement, the subtest will be marked as ``PASSED``
and next subtest will become ``ACTIVE``  When all subtests are ``PASSED`` the
test will pass and stop.

Dependency
----------
- Device API (``cros.factory.device.ambient_light_sensor``).

Examples
--------
To perform 3 subtests,

1. ``'Light sensor dark'`` (below 30)
2. ``'Light sensor exact'`` (between 60 and 300)
3. ``'Light sensor light'`` (above 500)

.. test_list::

  generic_ec_component_als_examples:LightSensor

The sensor value represents in lux. For reference, see
https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-bus-iio.

Note that you have to specify ``subtest_list``, ``subtests_instruction``,
``subtest_cfg`` at the same time.
"""

import logging
import os
import time
from typing import cast

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.test import test_ui
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg


_DEFAULT_SUBTEST_LIST = ['Light sensor dark',
                         'Light sensor exact',
                         'Light sensor light']
_DEFAULT_SUBTEST_CFG = {'Light sensor dark': {'below': 4},
                        'Light sensor exact': {'between': (10, 15)},
                        'Light sensor light': {'above': 200}}
_DEFAULT_SUBTEST_INSTRUCTION = {
    'Light sensor dark': _('Cover light sensor with finger'),
    'Light sensor exact': _('Remove finger from light sensor'),
    'Light sensor light': _('Shine light sensor with flashlight')}


class LightSensorTest(test_case.TestCase):
  """Tests light sensor."""
  related_components = (test_case.TestCategory.AMBIENTLIGHTSENSOR, )
  ARGS = [
      Arg('device_path', str, '[Deprecated] device path', default=None),
      Arg('device_name', (str, type(None)),
          'device name. If unset, do auto detection.', default='cros-ec-light'),
      Arg('location', str, 'device location. If unset, do auto detection.',
          default=None),
      Arg('device_input', str, '[Deprecated] device input file', default=None),
      Arg('timeout_per_subtest', int, 'timeout for each subtest', default=10),
      Arg('subtest_list', list, 'subtest list', default=None),
      Arg('subtest_cfg', dict, 'subtest configuration', default=None),
      Arg('subtest_instruction', dict, 'subtest instruction', default=None),
      Arg('check_per_subtest', int, 'check times for each subtest', default=3),
  ]

  def setUp(self):
    self._device = device_utils.CreateDUTInterface()
    self._als = self._device.ambient_light_sensor.GetController(
        name=self.args.device_name, location=self.args.location)
    # pylint: disable=protected-access
    device_path = cast(str, self._als._iio_path)
    # pylint: enable=protected-access
    device_name = self._device.ReadFile(os.path.join(device_path,
                                                     'name')).strip()
    logging.info('Select light sensor %s(%s)', device_path, device_name)

    self._calibrate = os.path.join(device_path, 'calibrate')

    subtest_args = [
        self.args.subtest_list, self.args.subtest_cfg,
        self.args.subtest_instruction
    ]
    if all(subtest_args):
      self._subtest_list = self.args.subtest_list
      self._subtest_cfg = self.args.subtest_cfg
      self._subtest_instruction = self.args.subtest_instruction
    elif any(subtest_args):
      raise ValueError(
          'Missing some of subtest_list, subtest_cfg or subtest_instruction.')
    else:
      self._subtest_list = _DEFAULT_SUBTEST_LIST
      self._subtest_cfg = _DEFAULT_SUBTEST_CFG
      self._subtest_instruction = _DEFAULT_SUBTEST_INSTRUCTION

    self._timeout_per_subtest = self.args.timeout_per_subtest
    self._iter_req_per_subtest = self.args.check_per_subtest

    for test_idx, name in enumerate(self._subtest_list):
      instruction = self._subtest_instruction[name]
      desc = f'{name} ({self.GetConfigDescription(self._subtest_cfg[name])})'
      html = [
          '<div class="task">', f'<div id="title{test_idx}">', instruction,
          '</div>'
          '<div class="desc-row">', f'<div id="desc{test_idx}" class="desc">',
          test_ui.Escape(desc),
          f'</div><div id="result{test_idx}" class="result">UNTESTED</div>',
          '</div>', '</div>'
      ]
      self.ui.SetHTML(html, id='tasks', append=True)

    # Group checker and details for Testlog.
    self._group_checker = testlog.GroupParam(
        'light', ['name', 'elapsed', 'light'])
    testlog.UpdateParam('name', param_type=testlog.ParamType.argument)
    testlog.UpdateParam('light', description=('Light sensor values over time'))
    testlog.UpdateParam('elapsed', value_unit='seconds')

  def GetConfigDescription(self, cfg):
    if 'above' in cfg:
      return f"Input > {int(cfg['above'])}"
    if 'below' in cfg:
      return f"Input < {int(cfg['below'])}"
    if 'between' in cfg:
      return f"{cfg['between'][0]} < Input < {cfg['between'][1]}"
    raise ValueError('Unknown type in subtest configuration')

  def _WriteCalibrate(self, value):
    """Write calibrate value."""
    try:
      self._device.WriteFile(self._calibrate, value)
    except Exception:
      logging.info('Unable to write to %s', self._calibrate)

  def runTest(self):
    # Starts to catch the signal.
    self._WriteCalibrate('1')
    # Stops catching the signal.
    self.addCleanup(self._WriteCalibrate, '0')

    self.ui.WaitKeysOnce(test_ui.SPACE_KEY)
    self.ui.HideElement('space-prompt')
    self.ui.StartFailingCountdownTimer(
        self._timeout_per_subtest * len(self._subtest_list))

    for idx, name in enumerate(self._subtest_list):
      self.ui.SetHTML('ACTIVE', id=f'result{int(idx)}')
      current_iter_remained = self._iter_req_per_subtest
      cumulative_val = 0
      start_time = time.time()
      while True:
        val = self._als.GetData(capture_count=5)[self._als.signal_names[0]]
        self.ui.SetHTML(f'Input: {int(val)}', id='input')

        cfg = self._subtest_cfg[name]
        passed = False
        with self._group_checker:
          testlog.LogParam('name', name)
          testlog.LogParam('elapsed', time.time() - start_time)
          if 'above' in cfg:
            passed = testlog.CheckNumericParam('light', val, min=cfg['above'])
            logging.info('%s checking "above" %d > %d',
                         'PASSED' if passed else 'FAILED',
                         val, cfg['above'])
          elif 'below' in cfg:
            passed = testlog.CheckNumericParam('light', val, max=cfg['below'])
            logging.info('%s checking "below" %d < %d',
                         'PASSED' if passed else 'FAILED',
                         val, cfg['below'])
          elif 'between' in cfg:
            lb, ub = cfg['between']
            passed = testlog.CheckNumericParam('light', val, min=lb, max=ub)
            logging.info('%s checking "between" %d < %d < %d',
                         'PASSED' if passed else 'FAILED',
                         lb, val, ub)
          else:
            self.fail('subtest_cfg doesn\'t have "above", "below" or "between"')

        if passed:
          cumulative_val += val
          current_iter_remained -= 1
          if not current_iter_remained:
            self.ui.SetHTML('PASSED', id=f'result{int(idx)}')
            mean_val = cumulative_val // self._iter_req_per_subtest
            logging.info('Passed subtest "%s" with mean value %d.', name,
                         mean_val)
            break
        else:
          if current_iter_remained != self._iter_req_per_subtest:
            logging.info('Resetting iter count.')
          cumulative_val = 0
          current_iter_remained = self._iter_req_per_subtest

        self.Sleep(0.5)
