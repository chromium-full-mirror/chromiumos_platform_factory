# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines a builder to build matchers from AVL ProbeInfo."""

from __future__ import annotations

import abc
import contextlib
import dataclasses
import enum
import functools
import logging
from typing import ClassVar, Iterable, Iterator, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple

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

  @classmethod
  def FromFactoryBranch(cls, factory_branch: str) -> OSVersion:
    """Parses from a factory branch."""
    _, _, version_string = factory_branch.rpartition('-')
    vers = version_string.split('.')
    try:
      if len(vers) == 2:
        # For "factory-boardname-12345.B"
        return cls(int(vers[0]))
      if len(vers) == 3:
        # For "factory-boardname-12345.67.B".
        return cls(int(vers[0]), int(vers[1]))

      raise ValueError('Unexpected format')
    except ValueError as e:
      raise ValueError(
          f'Failed to parse version from factory branch {factory_branch!r}, '
          f'{e!r}') from e


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


@dataclasses.dataclass
class ConverterSet:
  """Set of converters."""

  # An identifier in probe info indicates which probe function and converters
  # to be used.
  probe_info_identifier: str
  # All converters supporting the above identifier.
  # Note: Converters will be tried in the same order they defined. If not match,
  # the last available one will be logged and will be used to generate
  # suggestions.
  converters: Sequence[IProbeInfoConverter]

  def Get(
      self, version: OSVersion,
      component_status: AVLComponentStatus) -> Sequence[IProbeInfoConverter]:
    """Returns converters match the conditions.

    Args:
      version: The target version to apply the converters.
    """
    return [
        c for c in self.converters
        if (c.LAST_SUPPORT_VERSIONS >= version and
            c.COMPONENT_STATUS in [component_status, AVLComponentStatus.ALL])
    ]


class _BuildErrorLogger:
  BUILDER_ERRORS: Optional[MutableSequence[str]] = None


def LogBuilderError(message: str):
  """Logs builder error if all converters fail."""
  if _BuildErrorLogger.BUILDER_ERRORS is None:
    raise Exception('Not in a BuilderErrorLogger context manager')
  _BuildErrorLogger.BUILDER_ERRORS.append(message)


@contextlib.contextmanager
def BuilderErrorLogger(build_info: str) -> Iterator[MutableSequence[str]]:
  """Logs builder errors when exit.

  This prevents expected failures from polluting the logging. This also catches
  and logs exceptions.
  """
  backup = _BuildErrorLogger.BUILDER_ERRORS
  try:
    _BuildErrorLogger.BUILDER_ERRORS = []
    yield _BuildErrorLogger.BUILDER_ERRORS
  except Exception as e:
    LogBuilderError(f'{e!r}')
    raise
  finally:
    if _BuildErrorLogger.BUILDER_ERRORS:
      errs = '\n'.join(_BuildErrorLogger.BUILDER_ERRORS)
      full_err = ('ProbeInfoMatcherBuilder: '
                  f'Error occurs when building {build_info}\n'
                  f'Errors:\n{errs}\n--------------------')
      logging.error(full_err)
    _BuildErrorLogger.BUILDER_ERRORS = backup


class Builder:
  """Collects converter sets and builds matchers."""

  def __init__(self):
    self._converter_sets: MutableMapping[str, ConverterSet] = {}

  def AddConverterSet(self, converter_set: ConverterSet):
    """Add a converter set to this builder."""
    if converter_set.probe_info_identifier in self._converter_sets:
      raise ValueError('Duplicate probe_info_identifier '
                       f'{converter_set.probe_info_identifier!r}')
    self._converter_sets[converter_set.probe_info_identifier] = converter_set

  def Build(self, probe_info: v3_rule.AVLProbeInfo, model: str,
            factory_branch: Optional[str], cid: int, qid: int,
            is_probe_info_override: bool) -> Optional[matcher.Matcher]:
    """Builds a matcher."""
    with BuilderErrorLogger(
        f'Model {model!r}, factory_branch {factory_branch!r}, '
        f'component {cid}-{qid} (override: {is_probe_info_override}), '
        f'{probe_info!r}') as logs:
      converter_set = self._converter_sets.get(probe_info.identifier)
      if converter_set is None:
        LogBuilderError(
            f'Unsupported ProbeInfoIdentifier {probe_info.identifier!r}.')
        return None

      component_status = (
          AVLComponentStatus.QUALIFIED
          if qid != 0 else AVLComponentStatus.UNQUALIFIED)

      version = OSVersion.TOT
      if factory_branch is not None:
        version = OSVersion.FromFactoryBranch(factory_branch)

      converters: MutableSequence[matcher.Matcher.Converters] = []
      for converter in converter_set.Get(version, component_status):
        res = converter.Build(probe_info)
        if res is None:
          LogBuilderError(
              f'Converter {converter.IDENTIFIER!r} failed to build.')
          continue
        converters.append(
            matcher.Matcher.Converters(converter.IDENTIFIER, res[0], res[1]))
      if not converters:
        LogBuilderError('Failed to build any matcher for '
                        f'ProbeInfoIdentifier {probe_info.identifier!r}. ')
        return None

      logs.clear()
      return matcher.Matcher(converters)
