# Copyright 2020 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import re
import subprocess
from typing import Optional, cast

from cros.factory.utils import file_utils


_FUTILITY_BIN = '/usr/bin/futility'
_VPD_BIN = '/usr/sbin/vpd'
_CMD_TIMEOUT_SEC = 20

_HWID_RE = re.compile(r'hardware_id: ([A-Z0-9- ]+)')
_SERIAL_NUMBER_RE = re.compile(r'"serial_number"="([A-Za-z0-9-]+)"')


def _GetHWID(firmware_binary_file: str) -> Optional[str]:
  """Get HWID from ap firmware binary."""
  futility_cmd = [_FUTILITY_BIN, 'gbb', firmware_binary_file]
  output = subprocess.check_output(futility_cmd, encoding='utf-8',
                                   stderr=subprocess.PIPE,
                                   timeout=_CMD_TIMEOUT_SEC)
  logging.debug('futility output:\n%s', output)
  output.split(':')
  m = _HWID_RE.fullmatch(output.strip())
  return m and cast(str, m.group(1))


def _GetSerialNumber(firmware_binary_file: str) -> Optional[str]:
  """Get serial number from ap firmware binary."""
  vpd_cmd = [_VPD_BIN, '-l', '-f', firmware_binary_file]
  output = subprocess.check_output(vpd_cmd, encoding='utf-8',
                                   stderr=subprocess.PIPE,
                                   timeout=_CMD_TIMEOUT_SEC)
  logging.debug('vpd output:\n%s', output)
  for line in output.splitlines():
    m = _SERIAL_NUMBER_RE.fullmatch(line.strip())
    if m:
      return m.group(1)
  return None


def ExtractHWIDAndSerialNumber() -> tuple[Optional[str], Optional[str]]:
  """Extract HWID and serial no. from DUT.

  Read the ap firmware binary from DUT and extract the info from it. Only the
  necessary blocks are read to reduce the reading time.

  Returns:
    hwid, serial_number. The value may be None.
  """
  with file_utils.UnopenedTemporaryFile() as tmp_file:
    futility_cmd = [
        _FUTILITY_BIN, 'read', '--servo', '-r', 'FMAP,RO_VPD,GBB', tmp_file
    ]
    output = subprocess.check_output(futility_cmd, encoding='utf-8',
                                     stderr=subprocess.PIPE,
                                     timeout=_CMD_TIMEOUT_SEC)
    logging.debug('futility read output:\n%s', output)
    hwid = _GetHWID(tmp_file)
    serial_number = _GetSerialNumber(tmp_file)
    logging.info('Extract result: HWID: "%s", serial number: "%s"', hwid,
                 serial_number)

  return hwid, serial_number
