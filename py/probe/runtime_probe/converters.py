# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines converters to convert data to some consistent format for processing.
"""

import abc
from typing import Generic, NamedTuple, Optional, TypeVar


_T = TypeVar('_T')


class IConverter(abc.ABC, Generic[_T]):
  """Interface that converts between a target format and T.

  The implementation could define the target format. It will be the raw data
  format read from other places. T will be something that easy to be processed.
  """

  @abc.abstractmethod
  def Parse(self, value: str) -> Optional[_T]:
    """Parses a string with the target format to a T.

    Returns:
      None if conversion fails.
    """

  @abc.abstractmethod
  def Format(self, value: _T) -> str:
    """Format from a T to a string with the target format."""


class NopConverter(IConverter[str]):
  """A nop converter to be used to skip the type conversion in some API."""

  def Parse(self, value: str) -> Optional[str]:
    """See base class."""
    return value

  def Format(self, value: str) -> str:
    """See base class."""
    return value


class IntegerConverter(IConverter[int]):
  """Converts integer strings to integers.

  The strings should be an decimal integer, e.g. 1234
  """

  def Parse(self, value: str) -> Optional[int]:
    """See base class."""
    try:
      return int(value)
    except ValueError:
      return None

  def Format(self, value: int) -> str:
    """See base class."""
    return str(value)


class ConvertedHex(NamedTuple):
  """A helper type to distinguish with normal str."""
  value: str


class HexConverter(IConverter[ConvertedHex]):
  """Converts hex strings to consistent format.

  This converts any hex strings to a consistent format: lowercase, prefixes with
  0x, e.g. 0x12ab.
  """

  def Parse(self, value: str) -> Optional[ConvertedHex]:
    """See base class."""
    try:
      return ConvertedHex(hex(int(value, 16)))
    except ValueError:
      return None

  def Format(self, value: ConvertedHex) -> str:
    """See base class."""
    return value.value
