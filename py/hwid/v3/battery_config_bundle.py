# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import hashlib
import os.path
from typing import Optional, Tuple

from cros.factory.hwid.v3 import common
from cros.factory.utils import sys_interface as sys_interface_module


_HEADER_PREFIX = '// '
_HEADER_SPLITTER = ': '

_HEADER_FIELD_CHECKSUM = 'checksum'
_HEADER_FIELD_VERSION = 'version'


def _RenderHeaderLine(field_name: str, field_value: str) -> str:
  """Constructs a header line from the given field name and value.

  Args:
    field_name: The field name in the target header line.
    field_value: The corresponding field value in the header line.

  Returns:
    The header line string without new-line character at the end.

  Raises:
    ValueError: If the given `field_name` or `field_value` is invalid.
  """
  if '\n' in field_name or _HEADER_SPLITTER in field_name:
    raise ValueError(f'Invalid field name ({field_name!r}).')
  if '\n' in field_value:
    raise ValueError(f'Invalid field value ({field_value!r}).')
  return f'{_HEADER_PREFIX}{field_name}{_HEADER_SPLITTER}{field_value}'


def _ParseHeaderLine(line: str) -> Tuple[str, str]:
  """Parses a header line into (name, value), raises `ValueError` on failure."""
  name_part, sep, value_part = line.partition(_HEADER_SPLITTER)
  if not sep or not name_part.startswith(_HEADER_PREFIX):
    raise ValueError(f'Invalid header line: {line!r}')
  return name_part[len(_HEADER_PREFIX):], value_part


def PackBatteryConfigContents(contents: str, version: str) -> str:
  """Packs the battery config contents into a payload for HWID bundle.

  Args:
    contents: The original battery config contents.
    version: A string that represents the version of the original battery config
        contents.

  Returns:
    The battery config payload for HWID bundle to pack.
  """
  contents_checksum = hashlib.sha1(contents.encode('utf-8')).hexdigest()
  parts = [
      _RenderHeaderLine(_HEADER_FIELD_CHECKSUM, contents_checksum),
      _RenderHeaderLine(_HEADER_FIELD_VERSION, version),
      '',
      contents,
  ]
  return '\n'.join(parts)


def GetBatteryConfigFileName(model_name: str) -> str:
  """Gets the battery config file name in the HWID bundle."""
  return f'{model_name}.battery_config.json'


def UnpackBatteryConfigContents(
    bundle_dir_path: str, model_name: str,
    sys_interface: sys_interface_module.SystemInterface) -> Optional[str]:
  """Loads the battery config payload from the HWID bundle.

  It also validates the data integrity.

  Args:
    bundle_dir_path: The base directory where the HWID bundle is installed.
    model_name: The model name.

  Returns:
    If the battery config exists in the HWID bundle, return the battery config
    contents.  Otherwise it returns `None`.

  Raises:
    common.HWIDException: If the related data in HWID bundle is invalid.
    OSError: If it fails to write the battery config to a file to return.
  """
  file_name_in_bundle = GetBatteryConfigFileName(model_name)
  full_pathname = os.path.join(bundle_dir_path, file_name_in_bundle)
  if not os.path.exists(full_pathname):
    return None

  try:
    bundle_payload = sys_interface.ReadFile(full_pathname)
  except OSError as ex:
    raise common.HWIDException(
        f'Invalid data at {full_pathname!r}: Cannot read.') from ex

  header_part, sep, contents_part = bundle_payload.partition('\n\n')
  if not sep:
    raise common.HWIDException(
        f'Invalid data at {full_pathname!r}: Header not found.')

  expected_checksum = None
  for header_line in header_part.split('\n'):
    try:
      field_name, field_value = _ParseHeaderLine(header_line)
    except ValueError as ex:
      raise common.HWIDException(
          f'Invalid header in {full_pathname!r}: {header_line!r}.') from ex
    if field_name == _HEADER_FIELD_CHECKSUM:
      expected_checksum = field_value

  actual_checksum = hashlib.sha1(contents_part.encode('utf-8')).hexdigest()
  if expected_checksum != actual_checksum:
    raise common.HWIDException(
        f'Invalid data at {full_pathname!r}: Checksum mismatch.')

  return contents_part
