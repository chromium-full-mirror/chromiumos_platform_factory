# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from typing import Iterable, Mapping, Optional, Type

from cros.factory.hwid.v3.avl import builder
from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


class NopSuggester(matcher.ISuggester):
  """A placeholder which does nothing.

  TODO(chungsheng): Implement some real suggesters when we need them.
  """

  def BuildSuggestion(self, suggestion):
    return []


def GetFieldConverter(
    probe_info: v3_rule.AVLProbeInfo, key: str,
    matcher_type: Type[runtime_probe_matchers.FieldMatcher],
    runtime_probe_key_mapping: Optional[Mapping[str, str]] = None
) -> builder.IProbeInfoConverterBuildResult:
  """A general field converter.

  It tries to fetch values of a key and return a matcher to match any of them.

  Args:
    probe_info: The ProbeInfo.
    key: Key to fetch from `probe_info`.
    matcher_type: A runtime probe FieldMatcher.
    runtime_probe_key_mapping: If contains `key`, it will be used as the runtime
                               probe matcher field name.
  """
  values = probe_info.params.get(key)
  if not values:
    builder.LogBuilderError(f'Failed to get key {key!r}.')
    return None
  runtime_probe_key_mapping = runtime_probe_key_mapping or {}
  runtime_probe_key = runtime_probe_key_mapping.get(key, key)
  matchers = []
  for v in values:
    parsed = matcher_type.CONVERTER.Parse(v)
    if parsed is not None:
      matchers.append(matcher_type(runtime_probe_key, parsed))
      continue
    builder.LogBuilderError(
        f'Cannot parse {key!r} value {v!r} as type {matcher_type}. '
        'Fallback to StringEqualMatcher.')
    matchers.append(
        runtime_probe_matchers.StringEqualMatcher(runtime_probe_key, v))

  assert len(matchers) == len(values)
  if len(matchers) == 1:
    return (matchers[0], NopSuggester())
  return (runtime_probe_matchers.OrMatcher(matchers), NopSuggester())


def JoinFieldConverters(
    converters: Iterable[builder.IProbeInfoConverterBuildResult]
) -> builder.IProbeInfoConverterBuildResult:
  """Join multiple field converters to a single converter.

  Matchers are joined by AndMatcher. Returns None if any of them is None.
  """
  matchers = []
  suggesters = []
  for c in converters:
    if c is None:
      return None
    matchers.append(c[0])
    suggesters.append(c[1])
  assert len(matchers) >= 1
  if len(matchers) == 1:
    return (matchers[0], NopSuggester())
  return (runtime_probe_matchers.AndMatcher(matchers), NopSuggester())
