# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Common classes and helpers acrosss RF stuff."""

class Frequency:
  """Class that represents a specific frequency."""

  _f = None

  def __init__(self, f):
    """Initialize a frequency instance. f must be convertable to float in Hz."""
    self._f = float(f)

  def __repr__(self):
    """Returns a string representation."""
    return f'Frequency({self._f:f} Hz)'

  @classmethod
  def FromHz(cls, f):
    """Return an f Hz frequency instance."""
    return Frequency(f)

  @classmethod
  def FromKHz(cls, f):
    """Return an f KHz frequency instance."""
    return Frequency(1e3 * float(f))

  @classmethod
  def FromMHz(cls, f):
    """Return an f MHz frequency instance."""
    return Frequency(1e6 * float(f))

  @classmethod
  def FromGHz(cls, f):
    """Return an f GHz frequency instance."""
    return Frequency(1e9 * float(f))

  def Hzf(self):
    """Return frequency in Hz (float)."""
    return self._f

  def KHzf(self):
    """Return frequency in KHz (float)."""
    # yapf: disable
    return self._f / 1e3  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def MHzf(self):
    """Return frequency in MHz (float)."""
    # yapf: disable
    return self._f / 1e6  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def GHzf(self):
    """return frequency in GHz (float)."""
    # yapf: disable
    return self._f / 1e9  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def Hzi(self):
    """Return frequency in Hz (integer), may lose precision."""
    # yapf: disable
    return int(self._f)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def KHzi(self):
    """Return frequency in KHz (integer), may lose precision."""
    # yapf: disable
    return int(self._f / 1e3)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def MHzi(self):
    """Return frequency in MHz (integer), may lose precision."""
    # yapf: disable
    return int(self._f / 1e6)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def GHzi(self):
    """return frequency in GHz (integer), may lose precision."""
    # yapf: disable
    return int(self._f / 1e9)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
