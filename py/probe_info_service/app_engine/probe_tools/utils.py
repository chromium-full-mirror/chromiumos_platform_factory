# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re
from typing import Iterator, Sequence

from cros.factory.probe_info_service.app_engine import probe_info_analytics


def GetProbeParameterValue(probe_param: probe_info_analytics.ProbeParameter):
  """Get the value of a `probe_info_analytics.ProbeParameter`"""
  which_one_of = probe_param.WhichOneof('value')
  if which_one_of is None:
    return None

  return getattr(probe_param, which_one_of)


def _ToRestrictedPatternArray(pattern: str) -> Sequence[str]:
  # Make sure the pattern is a valid regex pattern.
  re.compile(pattern)

  def _HandleCharacterSet(pattern_it: Iterator) -> str:
    character_set = '['
    for character in pattern_it:
      if character == '\\':
        character += next(pattern_it)

      character_set += character

      if character == ']':
        break

    return character_set

  pattern_arr = []
  it = iter(pattern)
  for character in it:
    if character == '\\':
      character += next(it)
    elif character == '[':
      character = _HandleCharacterSet(it)

    pattern_arr.append(character)

  return pattern_arr


def RestrictedPrefixRegexMatch(pattern: str, target: str):
  """Performs a prefix regex match.

  Restricted regex will only include operators "[", "]" and "-". Therefore, this
  function finds the length of `target`, and uses only the prefix of `pattern`
  with the same length to perform a `re.fullmatch` to `target`.

  For example, with the following arguments:
  ```
    pattern: abc[a-z][0-9][a-z]123
    target: abcd0
  ```
  The length of `target` is 5, so this function will use only the first 5
  characters or character sets of `pattern`, i.e. `abc[a-z][0-9]`, to match
  `target`.

  Args:
    pattern: The restricted regex pattern string.
    target: The target string to perform the match.

  Returns:
    True if `target` matches the prefix of `pattern`.

  Raises:
    `re.error`: If `pattern` is not a valid regex pattern.
  """
  pattern_arr = _ToRestrictedPatternArray(pattern)

  if len(pattern_arr) < len(target):
    return False

  return bool(re.fullmatch(''.join(pattern_arr[:len(target)]), target))
