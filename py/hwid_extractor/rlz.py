# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
from typing import Any, Mapping, Optional, cast

from cros.factory.utils import json_utils


# RLZ json file.
_RLZ_JSON = os.path.join(os.path.dirname(__file__), 'rlz.json')


def _GetReferenceBoardName(device: Any) -> str:
  reference_board = device.get('reference_board')
  if reference_board and reference_board.get('is_active'):
    return reference_board['public_codename']
  # This board is not uni-build. Use the board name as the build image name.
  for board in device.get('boards', []):
    if board.get('is_active'):
      return board['public_codename']
  return device['public_codename']


def _ParseAllDevicesJSON(all_device: Any) -> dict[str, str]:
  res: dict[str, str] = {}
  for device in cast(list[Mapping[str, Any]], all_device.get('devices', [])):
    cr50_board_id = cast(Optional[str], device.get('cr50_board_id'))
    if not cr50_board_id or cr50_board_id == 'ZZCR':
      # "ZZCR" is a generic brandcode that all devices use in early bring-up
      # until the permanent brandcode is created.
      continue
    res[cr50_board_id] = _GetReferenceBoardName(device)
  return res


class RLZData:
  """RLZ data stores the mapping from rlz codes to name of reference boards."""

  def __init__(self):
    self._rlz_data: dict[str, str] = {}
    if os.path.isfile(_RLZ_JSON):
      self._rlz_data = json_utils.LoadFile(_RLZ_JSON)

  def Get(self, *args, **kwargs) -> Optional[str]:
    return self._rlz_data.get(*args, **kwargs)

  def UpdateFromAllDevicesJSON(self, all_device: Any) -> bool:
    """Update rlz.json with all_device.json.

    all_devices.json: gs://chromeos-build-release-console/all_devices.json

    Ask user to upload all_device.json, parse it and store the results to
    rlz.json.

    Args:
      all_device: The parsed json object of all_devices.json.
    Returns:
      True if update successfully.
    """
    rlz_data = _ParseAllDevicesJSON(all_device)
    if not rlz_data:
      return False
    json_utils.DumpFile(_RLZ_JSON, rlz_data, pretty=False)
    self._rlz_data = rlz_data
    return True
