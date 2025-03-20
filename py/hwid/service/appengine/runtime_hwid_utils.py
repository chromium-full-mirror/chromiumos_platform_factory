# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Runtime HWID utility functions."""

import collections
from typing import Mapping, NamedTuple, Optional, Sequence, Tuple

import runtime_probe_pb2  # pylint: disable=import-error


_RuntimeHwidComponent = runtime_probe_pb2.RuntimeHwidComponent
RUNTIME_HWID_MAGIC_STRING = 'R:'
FEATURE_ENABLEMENT_FIELDS = frozenset(['feature_level', 'scope_level'])
VALID_COMPONENT_POSITION_CHAR = frozenset(['?', '#', 'X'])


def CheckIsRuntimeHWID(hwid_string: str) -> bool:
  """Checks if a given HWID string is a Runtime HWID.

  Args:
    hwid_string: The HWID string to be checked.

  Returns:
    A bool value indicating whether the HWID string is a Runtime HWID or not.
  """
  parts = hwid_string.split()
  return len(parts) == 3 and parts[2].startswith(RUNTIME_HWID_MAGIC_STRING)


class RuntimeHWIDComponents(NamedTuple):
  feature_level: int
  scope_level: int
  component_positions: Mapping[str, Sequence[str]]


class InvalidRuntimeHWIDError(ValueError):
  """Indicates the Runtime HWID is malformed."""


def GetRuntimeHWIDComponents(runtime_hwid_comps: str) -> RuntimeHWIDComponents:
  """Gets RuntimeHWIDComponents object from a Runtime HWID components string.

  Args:
    runtime_hwid: The given Runtime HWID.

  Returns:
    A RuntimeHWIDComponents object.

  Raises:
    InvalidRuntimeHWIDError: If the given HWID string is not a valid Runtime
      HWID.
  """
  if not runtime_hwid_comps.startswith(RUNTIME_HWID_MAGIC_STRING):
    raise InvalidRuntimeHWIDError(
        f'Got invalid Runtime HWID {runtime_hwid_comps!r}: does not contain '
        f'{RUNTIME_HWID_MAGIC_STRING!r}.')

  component_parts = runtime_hwid_comps[len(RUNTIME_HWID_MAGIC_STRING):].split(
      '-')  # Removes `R:` prefix.
  if len(component_parts) > len(
      _RuntimeHwidComponent.DESCRIPTOR.fields_by_number):
    raise InvalidRuntimeHWIDError(
        f'Got invalid Runtime HWID {runtime_hwid_comps!r}: contains too many '
        'fields.')

  feature_enablement_fields = {}
  component_positions = collections.defaultdict(list)
  for idx, comps in enumerate(component_parts, 1):
    comp_type = _RuntimeHwidComponent.DESCRIPTOR.fields_by_number[idx].name
    if comp_type in FEATURE_ENABLEMENT_FIELDS:
      if not comps.isdigit():
        raise InvalidRuntimeHWIDError(
            f'Got invalid Runtime HWID {runtime_hwid_comps!r}: feature '
            'enablement fields should be an integer.')
      feature_enablement_fields[comp_type] = int(comps)
      continue

    comp_pos_list = comps.split(',')
    for comp_pos in comp_pos_list:
      if comp_pos not in VALID_COMPONENT_POSITION_CHAR and not comp_pos.isdigit(
      ):
        raise InvalidRuntimeHWIDError(
            f'Got invalid Runtime HWID {runtime_hwid_comps!r}: contains '
            'invalid characters.')
      if comp_pos in ('#', 'X') and len(comp_pos_list) > 1:
        raise InvalidRuntimeHWIDError(
            f'Got invalid Runtime HWID {runtime_hwid_comps!r}: # or X can only '
            'appear alone.')
      component_positions[comp_type].append(comp_pos)

  return RuntimeHWIDComponents(
      feature_level=feature_enablement_fields['feature_level'],
      scope_level=feature_enablement_fields['scope_level'],
      component_positions=component_positions)


def ExtractRuntimeHWID(
    hwid_string: str) -> Tuple[str, Optional[RuntimeHWIDComponents]]:
  """Extract Runtime HWID into different parts.

  Extract Runtime HWID into two string parts: (masked) Factory HWID and Runtime
  HWID components.

  Args:
    hwid_string: The HWID string to be extracted.

  Returns:
    A tuple of strings. If the given HWID string is a Runtime HWID,
    (masked Factory HWID, Runtime HWID components) is returned.
    Otherwise, (Factory HWID, None) is returned.
  """
  if CheckIsRuntimeHWID(hwid_string):
    parts = hwid_string.split(maxsplit=2)
    masked_factory_hwid = ' '.join(parts[:2])
    runtime_hwid_comps = parts[2]
    return masked_factory_hwid, GetRuntimeHWIDComponents(runtime_hwid_comps)

  return hwid_string, None
