# Copyright 2022 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines the flexible field value types.

This module consists of converter types which could be used to compare with
different value representations.
"""

from __future__ import annotations

import abc
import logging
import re
from typing import Any, Callable, Optional, Union


# Formatter type
class IStrFormatter(abc.ABC):

  @abc.abstractmethod
  def __call__(self, value: Union[str, FormattedStrType]) -> str:
    ...


class ConvertedValueType:
  """Base class of value types."""


ConvertedValueTypeFactory = Callable[[str], ConvertedValueType]


class IntValueType(int, ConvertedValueType):
  """Flexible int value type to match integers repsented in str."""

  def __eq__(self, other: Any):

    if isinstance(other, int):
      return super().__eq__(other)
    if isinstance(other, str):
      # hexadecimal
      other = other.lower().strip()
      if other.startswith('0x'):
        try:
          v = int(other, 16)
        except ValueError:
          return False
        return super().__eq__(v)

      # decimal
      try:
        v = int(other)
      except ValueError:
        return False
      return super().__eq__(v)
    return False

  def __ne__(self, other: Any):
    return not self.__eq__(other)


class StrValueType(str, ConvertedValueType):
  """Raw str value for comparison."""


class StrFormatterError(Exception):
  """An exception raised when the formatter cannot be applied to the value."""


class FormattedStrType(str, ConvertedValueType):
  """Flexible str value type to match str values with formatter.

  This type tries to override __eq__ function of str to customize the equality
  check by formatter_self and formatter_other which could be used to format
  self/other before comparison.
  """

  __hash__ = str.__hash__

  def __new__(cls, *args, formatter_self: Optional[IStrFormatter] = None,
              formatter_other: Optional[IStrFormatter] = None, **kwargs):
    instance = super().__new__(cls, *args, **kwargs)
    instance._formatter_self = formatter_self  # type: ignore #TODO(b/338318729) Fixit!
    instance._formatter_other = formatter_other  # type: ignore #TODO(b/338318729) Fixit!
    return instance

  def __eq__(self, other: Any):
    if isinstance(other, str):
      if self._formatter_self:  # type: ignore #TODO(b/338318729) Fixit!
        try:
          formatted_self = self._formatter_self(self)  # type: ignore #TODO(b/338318729) Fixit!
        except StrFormatterError:
          logging.exception('Invalid value %r for str formatter.', self)
          return False
      else:
        formatted_self = self

      if self._formatter_other:  # type: ignore #TODO(b/338318729) Fixit!
        try:
          formatted_other = self._formatter_other(other)  # type: ignore #TODO(b/338318729) Fixit!
        except StrFormatterError:
          logging.exception('Invalid value %r for str formatter.', other)
          return False
      else:
        formatted_other = other
      return self.IsEqual(formatted_self, formatted_other)
    return False

  def __ne__(self, other: Any):
    return not self.__eq__(other)

  @classmethod
  def CreateInstanceFactory(
      cls, formatter_self: Optional[IStrFormatter] = None,
      formatter_other: Optional[IStrFormatter] = None
  ) -> Callable[..., FormattedStrType]:

    def _Callable(*args, **kwargs) -> FormattedStrType:
      return cls(*args, formatter_self=formatter_self,
                 formatter_other=formatter_other, **kwargs)

    return _Callable

  def IsEqual(self, formatted_self: str, formatted_other: str) -> bool:
    return str.__eq__(formatted_self, formatted_other)


class FormattedRegexStrType(FormattedStrType):

  def IsEqual(self, formatted_self: str, formatted_other: str) -> bool:
    return bool(re.fullmatch(formatted_self, formatted_other))
