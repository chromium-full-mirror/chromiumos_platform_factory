# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.probe_info_service.app_engine import probe_info_analytics
from cros.factory.probe_info_service.app_engine.probe_tools import utils


class GetProbeParameterValueTest(unittest.TestCase):

  def testGetStringValue(self):
    param = probe_info_analytics.ProbeParameter(name="param_name",
                                                string_value="param_val")

    result = utils.GetProbeParameterValue(param)

    self.assertEqual(result, "param_val")

  def testGetIntValue(self):
    param = probe_info_analytics.ProbeParameter(name="param_name",
                                                int_value=100)

    result = utils.GetProbeParameterValue(param)

    self.assertEqual(result, 100)

  def testGetNoneValue(self):
    param = probe_info_analytics.ProbeParameter(name="param_name")

    result = utils.GetProbeParameterValue(param)

    self.assertEqual(result, None)
