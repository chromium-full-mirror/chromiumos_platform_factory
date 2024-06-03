# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines a builder to build matchers from AVL ProbeInfo."""

from __future__ import annotations

import abc
import dataclasses
import enum
import functools
from typing import ClassVar, Iterable, MutableSequence, Optional, Set, Tuple

from cros.factory.hwid.v3.avl import matcher
from cros.factory.hwid.v3 import rule as v3_rule
from cros.factory.probe.runtime_probe import matchers as runtime_probe_matchers


@dataclasses.dataclass
class OSVersion:
  """Represent a chromeos version."""
  build: int
  branch: int = 0
  patch: int = 0

  # Represent TOT version (a maximum value).
  TOT: ClassVar[OSVersion]


OSVersion.TOT = OSVersion(9999999, 0, 0)


@functools.total_ordering
class BranchesOSVersions:
  """A collection of OSVersions on branches.

  Each branch can hold only one OSVersion. The main branch build version cannot
  precede any other OSVersion because, if it does, it will not be comparable.
  Two OSVersions on the same branch share the same build version. An OSVersion
  on the main branch has a branch version of 0.

  Here is an example:
         /---X======Y======>
        /      /===Y======>
  >------X=======Y=======>

  'X' are OSVersions. '-' are versions less than. '=' are versions greater than.
  With the above guarantees, 'Y' can't be added to set because they are after
  'X'.
  """

  def __init__(self, versions: Iterable[OSVersion]):
    s: Set[int] = set()
    self._main_branch_version: Optional[int] = None
    self._versions: MutableSequence[OSVersion] = []

    for v in versions:
      if v.build in s:
        # We assume that each build will have at most 1 branch.
        raise ValueError(f'Duplicate build version {v.build}')
      s.add(v.build)
      if v.branch == 0:
        if self._main_branch_version is not None:
          raise ValueError('Can has only one main branch version')
        self._main_branch_version = v.build
      else:
        self._versions.append(v)

    if self._main_branch_version is not None:
      for v in self._versions:
        if v.build >= self._main_branch_version:
          raise ValueError(f'{v!r} is after '
                           f'main branch version {self._main_branch_version}')

  def _Compare(self, version: OSVersion) -> int:
    """Check if `version` is greater than any of the OSVersions or not.

    Returns:
      -1 if all OSVersions is less than `version`.
      0 if any OSVersion is equal to `version`.
      1 if all OSVersions is greater than `version`.
    """
    if self._main_branch_version is not None:
      if version.branch == 0 and self._main_branch_version == version.build:
        return 0
      if self._main_branch_version < version.build:
        return -1
    for v in self._versions:
      if v.build == version.build:
        if v.branch < version.branch:
          return -1
        if v.branch == version.branch:
          return 0
        return 1
    return 1

  def __eq__(self, oth) -> bool:
    if isinstance(oth, OSVersion):
      return self._Compare(oth) == 0
    return False

  def __lt__(self, version: OSVersion) -> bool:
    return self._Compare(version) < 0


class AVLComponentStatus(enum.Enum):
  ALL = enum.auto()
  UNQUALIFIED = enum.auto()
  QUALIFIED = enum.auto()


IProbeInfoConverterBuildResult = Optional[Tuple[runtime_probe_matchers.IMatcher,
                                                matcher.ISuggester]]


class IProbeInfoConverter(abc.ABC):
  """Builds matcher and suggester from ProbeInfo."""

  # Name of this converter, to be log to the HWID database after converting.
  IDENTIFIER: ClassVar[str]
  # Last versions this converter could be applied to.
  LAST_SUPPORT_VERSIONS: ClassVar[BranchesOSVersions] = BranchesOSVersions(
      [OSVersion.TOT])
  # Component status this converter could be applied to.
  COMPONENT_STATUS: ClassVar[AVLComponentStatus] = AVLComponentStatus.ALL

  @abc.abstractmethod
  def Build(self,
            probe_info: v3_rule.AVLProbeInfo) -> IProbeInfoConverterBuildResult:
    """Returns None if fails to convert."""
