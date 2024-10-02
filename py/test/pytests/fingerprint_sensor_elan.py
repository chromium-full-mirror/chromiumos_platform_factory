# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A factory test for the Elan fingerprint sensor.

Description
-----------
This pytest is to test the Elan fingerprint test.

The Elan fingerprint test consists of four sub-tests: base test, sensor test,
reset test, and WOE test. Only WOE test requires user interactions.

Test Procedure
--------------
The base, sensor and reset tests are automated. Don't touch the fingerprint
sensor during the test.

The WOE test requires user interaction. Please take the following steps.

1. Start the test, and wait until the screen tells the user to touch the
   fingerprint sensor.
2. Place your finger on the fingerprint sensor and then lift it away.
3. The UI should show that the WOE test is running. If not, the sensor does not
   detect your finger. It may be malfunctioning.
4. The pytest collects required data and analyzes the sensor's functionality
   automatically.
"""

import base64
import enum
import logging
import time
from typing import TYPE_CHECKING, Dict, Optional, Sequence, Tuple, cast

from cros.factory.device import device_utils
from cros.factory.test.i18n import _
from cros.factory.test import test_case
from cros.factory.test.utils import fpmcu_utils
from cros.factory.utils.arg_utils import Arg

if TYPE_CHECKING:
  import numpy
  _Image = numpy.ndarray[Tuple[int, int], numpy.dtype[numpy.uint16]]
else:
  from cros.factory.external.py_lib import numpy

# Follow the spec of Elan fingerprint sensor, the sensor is a square consisting
# of 80x80 pixels, and its ID is 0x4F4F.
_SENSOR_ID = '4f4f'
_FP_HEIGHT = 80
_FP_WIDTH = 80

# The timeout concerning interaction in milliseconds. The test fails if the user
# does not touch or untouch the fingerprint sensor in this period. The timeout
# is 1 minutes.
_INTERACTION_TIMEOUT_MS = 60 * 1000


class _TestCase(enum.Flag):
  BASE_TEST = 1
  SENSOR_TEST = 2
  RESET_TEST = 4
  WOE_TEST = 8


def _HasTooManyConsecutiveTrueInRow(
    bool_matrix: 'numpy.ndarray[Tuple[int, int], numpy.dtype[numpy.bool_]]',
    max_allowed_true_count: int) -> Optional[int]:
  """Checks if there are too many consecutive ``true``s in a 2D boolean matrix.

  Args:
    bool_matrix: The 2D boolean matrix to check,
    max_allowed_true_count: The maximal allowed ``true`` count.

  Returns:
    The row index (0-based) where too many consecutive ``true``s appear;
    ``None`` if not found.
  """
  for row_index, row in enumerate(bool_matrix):
    row = cast(Sequence[bool], row)
    for i in range(len(row) - max_allowed_true_count + 1):
      if all(row[i:i + max_allowed_true_count]):
        return row_index
  return None


def _GetImageFromFpframe(fpframe: bytes) -> '_Image':
  """Gets image from fpframe."""

  # The fpframe is a byte sequence where each 16-bit pixel is represented by two
  # bytes. The first byte of each pair is the low byte, and the second is the
  # high byte. For example, a fpframe byte sequence [0x0a, 0x0b, 0x0c, 0x0d]
  # represents the pixel values [0x0b0a, 0x0d0c].

  if len(fpframe) != _FP_HEIGHT * _FP_WIDTH * 2:
    raise ValueError(
        f'Unexpected fpframe length; expect {_FP_HEIGHT * _FP_WIDTH * 2} bytes '
        f'but got {len(fpframe)}.')

  image = numpy.zeros((_FP_HEIGHT, _FP_WIDTH), dtype=numpy.uint16)
  i = 0
  for y in range(_FP_HEIGHT):
    for x in range(_FP_WIDTH):
      image[y, x] = (fpframe[i + 1] << 8) | (fpframe[i])
      i += 2

  return image


class ElanFingerprintTest(test_case.TestCase):
  """Tests the Elan fingerprint sensor."""

  related_components = (test_case.TestCategory.FINGERPRINT_SENSOR, )

  ARGS = [
      Arg(
          'test_case', int,
          'The test case(s) to run in bitmap format. 1 for base test, 2 sensor '
          'test, 4 reset test, and 8 WOE test.', default=0b0111),
      Arg(
          'min_base_mean', float,
          'The allowed minimum mean value of frames in the base image. '
          'Required in base test and reset test.', default=1800.0),
      Arg(
          'max_base_mean', float,
          'The allowed maximum mean value of frames in the base image. '
          'Required in base test and reset test.', default=4200.0),
      Arg(
          'min_pixel_diff', int,
          'The minimum difference of frames between the raw image and the base '
          'image. Frames which difference lower than this value is considered '
          'a dead pixel. Required in sensor test.', default=700),
      Arg(
          'max_pixel_diff', int,
          'The maximum difference of frames between the raw image and the base '
          'image. Frames which difference exceeds this value is considered a '
          'dead pixel. Required in sensor test.', default=2300),
      Arg('max_dead_pixel_count', int,
          'The allowed dead pixel count. Required in sensor test.', default=19),
      Arg(
          'max_consecutive_dead_pixel_count', int,
          'The allowed consecutive dead pixel count in a horizontal or '
          'vertical line. Required in sensor test.', default=4),
      Arg(
          'contrast_threshold', int,
          'The required difference to judge the vendor image. Required in WOE '
          'test.', default=500),
      Arg('capture_fpmode_timeout_secs', float,
          'The timeout of capturing fpmode, in seconds.', default=5.0),
      Arg('fpmode_retry_count', int,
          'The maximum number of retry for fpmode waitevent and fpframe.',
          default=2),
      Arg('log_fpframe', bool, 'Whether to log fpframe for debugging.',
          default=False)
  ]

  if TYPE_CHECKING:

    class _Args:
      test_case: int
      min_base_mean: float
      max_base_mean: float
      min_pixel_diff: int
      max_pixel_diff: int
      max_dead_pixel_count: int
      max_consecutive_dead_pixel_count: int
      contrast_threshold: int
      capture_fpmode_timeout_secs: float
      fpmode_retry_count: int
      log_fpframe: bool

    args: _Args

  def setUp(self):
    self._dut = device_utils.CreateDUTInterface()
    self._fpmcu = fpmcu_utils.FpmcuDevice(self._dut)
    self._fpframe_cache: Dict[str, bytes] = {}

  def tearDown(self):
    self._ResetSensor()

  def _RequireSensorUntouched(self) -> None:
    """Requires that the fingerprint sensor is not touched.

    Detect if the fingerprint sensor is touched. If yes, show a message on the
    UI and block until users lifter their fingers from the sensor.

    Raises:
      FpmcuError: When the sensor is touched and the user does not lift the
      finger within the timeout.
    """
    try:
      self._fpmcu.RunFpmodeAndWaitEvent(
          'fingerup', wait_event_timeout_ms=500,
          max_attempt_count=self.args.fpmode_retry_count + 1)
      return
    except fpmcu_utils.FpmcuError:
      pass

    self.ui.SetState(  # type: ignore
        _('Please don\'t touch the fingerprint sensor.'))

    self._fpmcu.RunFpmodeAndWaitEvent(
        'fingerup', wait_event_timeout_ms=_INTERACTION_TIMEOUT_MS,
        max_attempt_count=self.args.fpmode_retry_count + 1)

  def _ResetSensor(self):
    """Resets the fingerprint sensor."""

    self._fpmcu.FpmcuCommand('fpmode', 'reset')
    self._fpmcu.FpmcuCommand('fpmode', 'reset_sensor')

    # Wait for a period to make the reset work. 0.5 second should be enough.
    time.sleep(0.5)

  def _GetAndCacheFpframe(self, capture_mode: str,
                          timeout_ms: Optional[int] = None) -> bytes:
    """Helper function to get and cache fpframe."""

    fpframe = self._fpframe_cache.get(capture_mode)
    if not fpframe:
      if not timeout_ms:
        timeout_ms = int(self.args.capture_fpmode_timeout_secs * 1000)
      self._fpmcu.CaptureFpmodeAndWaitEvent(capture_mode, timeout_ms,
                                            self.args.fpmode_retry_count + 1)
      fpframe = self._fpmcu.GetFpframe(
          raw=True, max_attempt_count=self.args.fpmode_retry_count + 1)
      # Log the fpframe for debugging.
      if self.args.log_fpframe:
        fpframe_base64 = base64.b64encode(fpframe).decode('ascii')
        logging.info('fpframe %s: %s', capture_mode, fpframe_base64)
      self._fpframe_cache[capture_mode] = fpframe
    return fpframe

  def _RunBaseTest(self):
    """Runs base test.

    This is a non-interactive test. Read fingerprint's base and check that the
    mean value of the frames is in the range.
    """
    self.ui.SetState(  # type: ignore
        _('Running base test. Please don\'t touch the sensor.'))

    pattern1_fpframe = self._GetAndCacheFpframe('pattern1')
    image = _GetImageFromFpframe(pattern1_fpframe)
    mean = numpy.mean(image)
    logging.info('Image mean: %f', mean)

    if self.args.min_base_mean > mean:
      self.FailTask(
          f'Base test fails: {self.args.min_base_mean} (allowed minimum mean)'
          f' > {mean} (observed mean)')

    if self.args.max_base_mean < mean:
      self.FailTask(
          f'Base test fails: {self.args.max_base_mean} (allowed maximum mean)'
          f' < {mean} (observed mean)')

    logging.info(
        'Base test passed. The base image mean %f meets the criteria [%f, %f].',
        mean, self.args.min_base_mean, self.args.max_base_mean)

  def _RunSensorTest(self):
    """Runs sensor test.

    This is a non-interactive test. Set fingerprint’s register and do sensor
    calibration to read the ADC value of every pixel, and check that the
    uniformity is in the range.
    """
    self.ui.SetState(  # type: ignore
        _('Running sensor test. Please don\'t touch the sensor.'))

    pattern1_fpframe = self._GetAndCacheFpframe('pattern1')
    base_image = _GetImageFromFpframe(pattern1_fpframe)
    pattern0_fpframe = self._GetAndCacheFpframe('pattern0')
    raw_image = _GetImageFromFpframe(pattern0_fpframe)
    pixel_diff_map = abs(raw_image - base_image)
    dead_pixel_matrix = (pixel_diff_map < self.args.min_pixel_diff) | (
        pixel_diff_map > self.args.max_pixel_diff)

    # Check that the difference in pixel values falls within an acceptable
    # range. It fails if too many pixels exceed the allowed deviation (a.k.a.
    # dead pixel).
    dead_pixel_count = numpy.count_nonzero(dead_pixel_matrix)
    if dead_pixel_count > self.args.max_dead_pixel_count:
      self.FailTask(
          f"Sensor test fails. {dead_pixel_count} dead pixels have difference "
          f"values outside the allowed range of [{self.args.min_pixel_diff}, "
          f"{self.args.max_pixel_diff}]. The maximum allowed number of dead "
          f"pixels is {self.args.max_dead_pixel_count}.")

    # Check that there is no too many dead pixels on each horizontal line and
    # vertical line.
    row_index = _HasTooManyConsecutiveTrueInRow(
        dead_pixel_matrix, self.args.max_consecutive_dead_pixel_count)
    if row_index is not None:
      self.FailTask('Sensor test fails. Found too many dead pixels in row '
                    f'{row_index} (0-based).')
    col_index = _HasTooManyConsecutiveTrueInRow(
        numpy.rot90(dead_pixel_matrix),
        self.args.max_consecutive_dead_pixel_count)
    if col_index is not None:
      self.FailTask('Sensor test fails. Found too many dead pixels in column '
                    f'{col_index} (0-based).')

    logging.info('Sensor test passes.')

  def _RunResetTest(self):
    """Runs reset test.

    This is a non-interactive test. Check that the fingerprint returns to the
    initial setting state, and check that the FPR initializes successfully.
    """

    self.ui.SetState(  # type: ignore
        _('Running reset test. Please don\'t touch the sensor.'))

    self._ResetSensor()

    pattern1_fpframe = self._GetAndCacheFpframe('pattern1')
    image = _GetImageFromFpframe(pattern1_fpframe)
    mean = numpy.mean(image)
    logging.info('Image mean: %f', mean)

    if self.args.min_base_mean > mean:
      self.FailTask(
          f'Reset test fails: {self.args.min_base_mean} (allowed minimum mean)'
          f' > {mean} (observed mean)')

    if self.args.max_base_mean < mean:
      self.FailTask(
          f'Reset test fails: {self.args.max_base_mean} (allowed maximum mean)'
          f' < {mean} (observed mean)')

    logging.info('The base image mean %f meets the criteria [%f, %f].', mean,
                 self.args.min_base_mean, self.args.max_base_mean)

    sensor_id = self._fpmcu.GetFpSensorInfo()[1]
    self.assertEqual(sensor_id, _SENSOR_ID)

    logging.info('Reset test passes.')

  def _RunWOETest(self):
    """Runs WOE test.

    This is an interactive test. Press finger or rubber on the FPR and confirm
    whether sensor can wake up.
    """
    pattern1_fpframe = self._GetAndCacheFpframe('pattern1')
    base_image = _GetImageFromFpframe(pattern1_fpframe)

    self.ui.SetState(  # type: ignore
        _('Touch the fingerprint sensor, then lift your finger.'))
    vendor_fpframe = self._GetAndCacheFpframe('vendor', _INTERACTION_TIMEOUT_MS)
    self._RequireSensorUntouched()
    self.ui.SetState(  # type: ignore
        _('Detected touch. Now running WOE test. Don\'t touch the sensor.'))
    vendor_image = _GetImageFromFpframe(vendor_fpframe)
    pixel_diff_map = abs(vendor_image - base_image)

    for r in range(0, _FP_HEIGHT, 8):
      for c in range(0, _FP_WIDTH, 8):
        max_pixel_diff = 0
        min_pixel_diff = float('inf')
        for mask_row in range(8):
          for mask_col in range(8):
            pixel_diff = pixel_diff_map[r | mask_row, c | mask_col]
            max_pixel_diff = max(max_pixel_diff, pixel_diff)
            min_pixel_diff = min(min_pixel_diff, pixel_diff)
        if max_pixel_diff - min_pixel_diff > self.args.contrast_threshold:
          logging.info('WOE Test passes.')
          return

    self.FailTask('WOE test fails.')

  def _ValidateArguments(self):
    """Validates test arguments.

    Raises:
      ValueError: If any argument has invalid value.
    """
    if not 0 < self.args.test_case < (1 << len(_TestCase)):
      raise ValueError(f"Argument `test_case` not in valid range (0, "
                       f"0b{'1' * len(_TestCase)}]: {self.args.test_case}")
    if not 0 <= self.args.min_base_mean <= 0xffff:
      raise ValueError("Argument `min_base_mean` not in valid range "
                       f"[0, 0xFFFF]: {self.args.min_base_mean}")
    if not 0 <= self.args.max_base_mean <= 0xffff:
      raise ValueError("Argument `max_base_mean` not in valid range "
                       f"[0, 0xFFFF]: {self.args.max_base_mean}")
    if self.args.min_base_mean > self.args.max_base_mean:
      raise ValueError(f"Argument `max_base_mean` ({self.args.max_base_mean}) "
                       "must be greater than `min_base_mean` "
                       f"({self.args.min_base_mean})")
    if not 0 <= self.args.max_dead_pixel_count <= _FP_HEIGHT * _FP_WIDTH:
      raise ValueError("Argument `max_dead_pixel_count` not in valid range "
                       f"[0, {_FP_HEIGHT * _FP_WIDTH}]: "
                       f"{self.args.max_dead_pixel_count}.")
    if not 0 <= self.args.max_consecutive_dead_pixel_count <= max(
        _FP_HEIGHT, _FP_WIDTH):
      raise ValueError("Argument `max_consecutive_dead_pixel_count` not in "
                       "valid range [0, {max(_FP_HEIGHT, _FP_WIDTH)}]: "
                       f"{self.args.max_consecutive_dead_pixel_count}")
    if not 0 <= self.args.contrast_threshold <= 0xffff:
      raise ValueError("Argument `contrast_threshold` not in valid range "
                       f"[0, 0xFFFF]: {self.args.contrast_threshold}")
    if self.args.capture_fpmode_timeout_secs < 0:
      raise ValueError("Argument `capture_fpmode_timeout_secs` cannot be "
                       f"negative: {self.args.capture_fpmode_timeout_secs}")
    if self.args.fpmode_retry_count < 0:
      raise ValueError("Argument `fpmode_retry_count` cannot be negative: "
                       f"{self.args.capture_fpmode_timeout_secs}")

  def runTest(self):
    self._ValidateArguments()

    tc = _TestCase(self.args.test_case)
    if tc & _TestCase.BASE_TEST:
      self._RunBaseTest()
    if tc & _TestCase.SENSOR_TEST:
      self._RunSensorTest()
    if tc & _TestCase.RESET_TEST:
      self._RunResetTest()
    if tc & _TestCase.WOE_TEST:
      self._RunWOETest()
