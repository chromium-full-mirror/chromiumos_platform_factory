# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging

from cros.factory.probe.runtime_probe import probe_config_types
from cros.factory.utils import json_utils
from cros.factory.utils import process_utils


RUNTIME_PROBE_BIN = '/usr/local/usr/bin/factory_runtime_probe'
CATEGORY_NAME = 'adaptor_category'
COMPONENT_NAME = 'adaptor_component'


def RunProbeFunction(probe_function_name, args):
  definition = probe_config_types.ProbeStatementDefinition(
      CATEGORY_NAME, probe_function_name, {})
  probe_statement = definition.GenerateProbeStatement(
      COMPONENT_NAME, probe_function_name, {}, args)
  payload = probe_config_types.ProbeConfigPayload()
  payload.AddComponentProbeStatement(probe_statement)

  process_result = process_utils.LogAndCheckCall(
      [RUNTIME_PROBE_BIN, '--log_level=-2',
       payload.DumpToString()], read_stdout=True, read_stderr=True)
  logging.info('Runtime probe logs: %s', process_result.stderr_data)
  res = json_utils.LoadStr(process_result.stdout_data)
  return [x['values'] for x in res[CATEGORY_NAME]]
