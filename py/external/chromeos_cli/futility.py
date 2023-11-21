# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import re
from typing import Dict, List

from cros.factory.utils import file_utils

from cros.factory.external.chromeos_cli import shell


# Ref: src/platform/ti50/common/capsules/src/ap_ro_verification/gscvd.rs
GSCVD_AREA_NAME = 'RO_GSCVD'
GSCVD_MAGIC = b'5afe'
GSCVD_RLZ_OFFSET = 12

class FutilityError(Exception):
  """All exceptions when calling futility."""


class FlashromError(Exception):
  """All exceptions when calling flashrom."""


class Futility:
  """Helper class for cmdline utility of futility and flashrom."""

  def __init__(self, dut=None):
    self._shell = shell.Shell(dut)

  # TODO(jasonchuang) We should use futility instead of using flashrom.
  def GetFlashSize(self):
    """Parses flash size from flashrom."""
    cmd = ['flashrom', '--flash-size']
    res = self._InvokeCommand(cmd, 'Fail to get flash size.').stdout

    try:
      size = int(res.splitlines()[-1])
    except (IndexError, ValueError) as parsing_error:
      raise FlashromError(
          f'Fail to parse the flash size {res}') from parsing_error
    return size

  def GetWriteProtectInfo(self):
    """Parses the start and the length of write protect from futility."""
    res = self._InvokeCommand(['futility', 'flash', '--flash-info'],
                              'Fail to get flash info.').stdout

    wp_conf = re.search(r'\(start = (?P<start>\w+), length = (?P<length>\w+)\)',
                        res)
    if not wp_conf:
      raise FutilityError(f'Fail to parse the wp region {res}')
    return wp_conf

  def GetRegions(self, regions: List[str], output_dir: str,
                 prefix: str = 'bios') -> Dict[str, str]:
    """Gets specific regions from the FW.

    Args:
      regions: A list which contains the name of the FW regions.
      output_dir: Path to the output directory.
      prefix: Prefix of the output FW regions.

    Returns:
      A dictionary with keys being the region name and the value being the
      path to the dumped FW.
    """
    prefix = os.path.join(output_dir, prefix)
    region_dict = {}
    for region in regions:
      region_dict[region] = f'{prefix}_{region}'
      self._InvokeCommand(
          f'futility read --region {region} {region_dict[region]}',
          f'Failed to read FW region {region} from firmware.')

    return region_dict

  def GetRLZFromROGSCVD(self):
    """Gets the RLZ from FW RO_GSCVD region."""
    with file_utils.TempDirectory() as tempd:
      gscvd_file = self.GetRegions([GSCVD_AREA_NAME], tempd)[GSCVD_AREA_NAME]
      with open(gscvd_file, 'rb') as gscvd:
        magic = gscvd.read(len(GSCVD_MAGIC))
        if magic != GSCVD_MAGIC:
          raise ValueError('Failed to find magic number in GSCVD! '
                           f'Expected: {GSCVD_MAGIC}, Found: {magic}')
        gscvd.seek(GSCVD_RLZ_OFFSET, 0)
        rlz_bytes = gscvd.read(4)
        try:
          rlz_code = rlz_bytes.decode('ascii')
          assert rlz_code.isalpha() and rlz_code.isupper()
          # Reads as little endian.
          return rlz_code[::-1]
        except (UnicodeDecodeError, AssertionError) as e:
          raise ValueError('Each char in the RLZ code should be a char between '
                           f'A~Z. Found: {rlz_bytes}') from e

  def _InvokeCommand(self, cmd, failure_msg, cmd_result_checker=None):
    cmd_result_checker = cmd_result_checker or (lambda result: result.success)
    result = self._shell(cmd)
    if not cmd_result_checker(result):
      raise FutilityError(failure_msg + f' (command result: {result!r})')
    return result
