# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import re
import tempfile
from typing import Dict, List

from cros.factory.utils import file_utils

from cros.factory.external.chromeos_cli import shell


# Ref: src/platform/ti50/common/capsules/src/ap_ro_verification/gscvd.rs
GSCVD_AREA_NAME = 'RO_GSCVD'
GSCVD_MAGIC = b'5afe'
GSCVD_RLZ_OFFSET = 12

class FutilityError(Exception):
  """All exceptions when calling futility or flashrom."""


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
      raise FutilityError(
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

  def SetGBBFlags(self, flags):
    """Sets the GBB flags"""
    self._InvokeCommand(f'futility gbb --set --flash --flags={flags} 2>&1',
                        'Failed setting GBB flags')

  def GetGBBFlags(self, fw_file='--flash'):
    """Reads the GBB flags.

    Args:
      fw_filename: The file of main firmware.
    """
    result = self._InvokeCommand(f'futility gbb --get --flags {fw_file}',
                                 'Failed getting GBB flags')
    match = re.match(r'flags: (\S*)', result.stdout)
    if match:
      return int(match.group(1), 16)
    raise FutilityError(f'Fail to parse the GBB flags {result.stdout}')

  def VerifyECKey(self, pubkey_path=None, pubkey_hash=None):
    """Verifies EC public key.
    Verify by pubkey_path should have higher priority than pubkey_hash.

    Args:
      pubkey_path: A string for public key path. If not None, it verifies the
          EC with the given pubkey_path.
      pubkey_hash: A string for the public key hash. If not None, it verifies
          the EC with the given pubkey_hash.
    """
    with tempfile.NamedTemporaryFile() as tmp_ec_bin:
      self._InvokeCommand(f'flashrom -p ec -r {tmp_ec_bin.name}',
                          'Failed to read EC image')
      if pubkey_path:
        self._InvokeCommand(
            f'futility show --type rwsig --pubkey {pubkey_path} '
            f'{tmp_ec_bin.name}',
            f'Failed to verify EC key with pubkey {pubkey_path}')
      elif pubkey_hash:
        live_ec_hash = self.GetKeyHashFromFutil(tmp_ec_bin.name)
        if live_ec_hash != pubkey_hash:
          raise FutilityError(
              f'Failed to verify EC key: expects ({pubkey_hash}) got '
              f'({live_ec_hash})')
      else:
        raise ValueError('All arguments are None.')

  def GetKeyHashFromFutil(self, fw_file):
    """Gets the pubkey hash from `futility show` output.

    Args:
      fw_file: The path to the firmware blob

    Returns:
      The public key hash of the specified firmware file
    """

    futil_out = self._InvokeCommand(
        ['futility', 'show', '--type', 'rwsig', fw_file],
        'Failed to get EC pubkey hash')
    # A typical example of the output from `futility show` is:
    # Public Key file:       /tmp/ec_binasdf1234
    #    Vboot API:           2.1
    #    Desc:                ""
    #    Signature Algorithm: 7 RSA3072EXP3
    #    Hash Algorithm:      2 SHA256
    #    Version:             0x00000001
    #    ID:                  c80def123456789058e140bbc44c692cc23ecb4d
    #  Signature:             /tmp/ec_binasdf1234
    #    Vboot API:           2.1
    #    Desc:                ""
    #    Signature Algorithm: 7 RSA3072EXP3
    #    Hash Algorithm:      2 SHA256
    #    Total size:          0x1b8 (440)
    #    ID:                  c80def123456789058e140bbc44c692cc23ecb4d
    #    Data size:           0x17164 (94564)
    #  Signature verification succeeded.
    key_hash = re.search(r'\n\s*ID:\s*([a-z0-9]*)', futil_out.stdout).group(1)  # type: ignore #TODO(b/338318729) Fixit!
    return key_hash

  def WriteHWID(self, fw_filename, hwid=None):
    """Writes specified HWID value into the system BB.

    Args:
      hwid: The HWID string to be written to the device.
      fw_filename: The file of main firmware.
    """

    self._InvokeCommand(f'futility gbb --set --hwid="{hwid}" "{fw_filename}"',
                        "Failed to write the HWID string")

  def ReadHWID(self, fw_filename):
    """Reads the HWID string from firmware GBB.

    Args:
      fw_filename: The file of main firmware.
    """

    result = self._InvokeCommand(f'futility gbb -g --hwid "{fw_filename}"',
                                 'Failed to read the HWID string')

    return re.findall(r'hardware_id:(.*)', result.stdout)[0].strip()

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
    region_str = ','.join(regions)
    self._InvokeCommand(
        f'futility read --region {region_str} --split-output {prefix}',
        f'Failed to read FW region {region_str} from firmware.')

    return {region: f'{prefix}_{region}'
            for region in regions}

  def GetRLZFromROGSCVD(self):
    """Gets the RLZ from FW RO_GSCVD region."""
    with file_utils.TempDirectory() as tempd:
      gscvd_file = self.GetRegions([GSCVD_AREA_NAME], tempd)[GSCVD_AREA_NAME]
      with open(gscvd_file, 'rb') as gscvd:
        magic = gscvd.read(len(GSCVD_MAGIC))
        if magic != GSCVD_MAGIC:
          raise ValueError('Failed to find magic number in GSCVD! '  # type: ignore #TODO(b/338318729) Fixit!
                           f'Expected: {GSCVD_MAGIC}, Found: {magic}')
        gscvd.seek(GSCVD_RLZ_OFFSET, 0)
        rlz_bytes = gscvd.read(4)
        try:
          rlz_code = rlz_bytes.decode('ascii')
          assert rlz_code.isalpha() and rlz_code.isupper()
          # Reads as little endian.
          return rlz_code[::-1]
        except (UnicodeDecodeError, AssertionError) as e:
          raise ValueError('Each char in the RLZ code should be a char between '  # type: ignore #TODO(b/338318729) Fixit!
                           f'A~Z. Found: {rlz_bytes}') from e

  def _InvokeCommand(self, cmd, failure_msg, cmd_result_checker=None):
    cmd_result_checker = cmd_result_checker or (lambda result: result.success)
    result = self._shell(cmd)
    if not cmd_result_checker(result):
      raise FutilityError(failure_msg + f' (command result: {result!r})')
    return result
