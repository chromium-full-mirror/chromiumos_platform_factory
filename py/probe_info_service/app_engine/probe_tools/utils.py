# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from cros.factory.probe_info_service.app_engine import probe_info_analytics


def GetProbeParameterValue(probe_param: probe_info_analytics.ProbeParameter):
  """Get the value of a `probe_info_analytics.ProbeParameter`"""
  which_one_of = probe_param.WhichOneof('value')
  if which_one_of is None:
    return None

  return getattr(probe_param, which_one_of)
