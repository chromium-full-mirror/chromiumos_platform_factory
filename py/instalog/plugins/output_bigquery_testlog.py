#!/usr/bin/env python3
#
# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""BigQuery upload output plugin.

Subclasses OutputBigQuery to create table rows for Testlog events.
"""

import datetime
import json
import math

from google.cloud.bigquery.schema import SchemaField

from cros.factory.instalog import plugin_base
from cros.factory.instalog.plugins import output_bigquery
from cros.factory.utils import time_utils


class OutputBigQueryTestlog(output_bigquery.AbstractOutputBigQuery):

  def GetTableSchema(self):
    """Returns a list of fields in the table schema."""
    return [
        # history
        SchemaField('history', 'record', 'REPEATED', None,
                    (SchemaField('node_id', 'string', 'NULLABLE', None, ()),
                     SchemaField('time', 'timestamp', 'NULLABLE', None, ()),
                     SchemaField('plugin_id', 'string', 'NULLABLE', None, ()),
                     SchemaField('plugin_type', 'string', 'NULLABLE', None, ()),
                     SchemaField('target', 'string', 'NULLABLE', None, ()))),

        # station
        SchemaField('uuid', 'string', 'NULLABLE', None, ()),
        SchemaField('type', 'string', 'NULLABLE', None, ()),
        SchemaField('apiVersion', 'string', 'NULLABLE', None, ()),
        SchemaField('time', 'timestamp', 'NULLABLE', None, ()),
        SchemaField('seq', 'integer', 'NULLABLE', None, ()),
        SchemaField('dutDeviceId', 'string', 'NULLABLE', None, ()),
        SchemaField('stationDeviceId', 'string', 'NULLABLE', None, ()),
        SchemaField('stationInstallationId', 'string', 'NULLABLE', None, ()),

        # station.status
        SchemaField('filePath', 'string', 'NULLABLE', None, ()),
        SchemaField('serialNumbers', 'record', 'REPEATED', None, (SchemaField(
            'key', 'string', 'NULLABLE', None,
            ()), SchemaField('value', 'string', 'NULLABLE', None, ()))),
        SchemaField(
            'parameters', 'record', 'REPEATED', None,
            (SchemaField('key', 'string', 'NULLABLE', None, ()),
             SchemaField('description', 'string', 'NULLABLE', None, ()),
             SchemaField('group', 'string', 'NULLABLE', None, ()),
             SchemaField('valueUnit', 'string', 'NULLABLE', None, ()),
             SchemaField('data', 'record', 'REPEATED', None,
                         (SchemaField('id', 'integer', 'NULLABLE', None, ()),
                          SchemaField('status', 'string', 'NULLABLE', None, ()),
                          SchemaField('numericValue', 'float', 'NULLABLE', None,
                                      ()),
                          SchemaField('expectedMinimum', 'float', 'NULLABLE',
                                      None, ()),
                          SchemaField('expectedMaximum', 'float', 'NULLABLE',
                                      None, ()),
                          SchemaField('textValue', 'string', 'NULLABLE', None,
                                      ()),
                          SchemaField('expectedRegex', 'string', 'NULLABLE',
                                      None, ()),
                          SchemaField('serializedValue', 'string', 'NULLABLE',
                                      None, ()))))),

        # station.init
        SchemaField('count', 'integer', 'NULLABLE', None, ()),
        SchemaField('success', 'boolean', 'NULLABLE', None, ()),
        SchemaField('failureMessage', 'string', 'NULLABLE', None, ()),

        # station.message
        SchemaField('message', 'string', 'NULLABLE', None, ()),
        SchemaField('lineNumber', 'integer', 'NULLABLE', None, ()),
        SchemaField('functionName', 'string', 'NULLABLE', None, ()),
        SchemaField('logLevel', 'string', 'NULLABLE', None, ()),
        SchemaField('testRunId', 'string', 'NULLABLE', None, ()),

        # station.test_run (also use testRunId)
        SchemaField('testName', 'string', 'NULLABLE', None, ()),
        SchemaField('testType', 'string', 'NULLABLE', None, ()),
        SchemaField('arguments', 'record', 'REPEATED', None, (SchemaField(
            'key', 'string', 'NULLABLE', None,
            ()), SchemaField(
                'description', 'string', 'NULLABLE', None,
                ()), SchemaField('value', 'string', 'NULLABLE', None, ()))),
        SchemaField('status', 'string', 'NULLABLE', None, ()),
        SchemaField('startTime', 'timestamp', 'NULLABLE', None, ()),
        SchemaField('endTime', 'timestamp', 'NULLABLE', None, ()),
        SchemaField('duration', 'float', 'NULLABLE', None, ()),
        SchemaField('operatorId', 'string', 'NULLABLE', None, ()),
        SchemaField(
            'attachments', 'record', 'REPEATED', None,
            (SchemaField('key', 'string', 'NULLABLE', None, ()),
             SchemaField('description', 'string', 'NULLABLE', None,
                         ()), SchemaField('path', 'string', 'NULLABLE', None,
                                          ()),
             SchemaField('mimeType', 'string', 'NULLABLE', None, ()))),
        SchemaField(
            'failures', 'record', 'REPEATED', None,
            (SchemaField('id', 'integer', 'NULLABLE', None,
                         ()), SchemaField('code', 'string', 'NULLABLE', None,
                                          ()),
             SchemaField('details', 'string', 'NULLABLE', None, ()))),

        # serialized
        SchemaField('serialized', 'string', 'NULLABLE', None, ())
    ]

  def ConvertEventToRow(self, event):
    """Converts an event to its corresponding BigQuery table row JSON string."""
    if not event.get('__testlog__', False):
      return None

    def DateTimeToUnixTimestamp(obj):
      if isinstance(obj, datetime.datetime):
        return time_utils.DatetimeToUnixtime(obj)
      if isinstance(obj, float):
        return obj
      return None

    # yapf: disable
    row = {}  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    # history
    row['history'] = []
    for process_stage in event.history:
      row['history'].append({})
      row['history'][-1]['node_id'] = process_stage.node_id
      row['history'][-1]['time'] = DateTimeToUnixTimestamp(
          process_stage.time)
      row['history'][-1]['plugin_id'] = process_stage.plugin_id
      row['history'][-1]['plugin_type'] = process_stage.plugin_type
      row['history'][-1]['target'] = process_stage.target

    # station
    row['uuid'] = event.get('uuid')
    row['type'] = event.get('type')
    row['apiVersion'] = event.get('apiVersion')
    row['time'] = DateTimeToUnixTimestamp(event.get('time'))
    row['seq'] = event.get('seq')
    row['dutDeviceId'] = event.get('dutDeviceId')
    row['stationDeviceId'] = event.get('stationDeviceId')
    row['stationInstallationId'] = event.get('stationInstallationId')

    # station.status
    row['filePath'] = event.get('filePath')  # also in station.message
    row['serialNumbers'] = []
    for key, value in event.get('serialNumbers', {}).items():
      row['serialNumbers'].append({})
      row['serialNumbers'][-1]['key'] = key
      row['serialNumbers'][-1]['value'] = value

    row['parameters'] = []
    for key, dct in event.get('parameters', {}).items():
      dct = dct or {}
      row['parameters'].append({})
      row['parameters'][-1]['key'] = key
      row['parameters'][-1]['description'] = dct.get('description')
      row['parameters'][-1]['group'] = dct.get('group')
      row['parameters'][-1]['status'] = dct.get('status')
      row['parameters'][-1]['valueUnit'] = dct.get('valueUnit')



    row['parameters'] = []
    for key, dct in event.get('parameters', {}).items():
      row['parameters'].append({})
      row['parameters'][-1]['key'] = key
      row['parameters'][-1]['description'] = dct.get('description')
      row['parameters'][-1]['group'] = dct.get('group')
      row['parameters'][-1]['valueUnit'] = dct.get('valueUnit')
      row['parameters'][-1]['data'] = []
      for i, data_dct in enumerate(dct.get('data', [])):
        row['parameters'][-1]['data'].append({})
        row['parameters'][-1]['data'][-1]['id'] = i
        row['parameters'][-1]['data'][-1]['status'] = data_dct.get('status')
        # TODO(chuntsen): Remove these casts when numericValue is reliable.
        if data_dct.get('numericValue') is not None:
          numeric_value = float(data_dct.get('numericValue'))
          if math.isinf(numeric_value) or math.isnan(numeric_value):
            # yapf: disable
            numeric_value = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
            # yapf: enable
          row['parameters'][-1]['data'][-1]['numericValue'] = numeric_value
        if data_dct.get('expectedMinimum') is not None:
          expected_minimum = float(data_dct.get('expectedMinimum'))
          if math.isinf(expected_minimum) or math.isnan(expected_minimum):
            # yapf: disable
            expected_minimum = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
            # yapf: enable
          row['parameters'][-1]['data'][-1][
              'expectedMinimum'] = expected_minimum
        if data_dct.get('expectedMaximum') is not None:
          expected_maximum = float(data_dct.get('expectedMaximum'))
          if math.isinf(expected_maximum) or math.isnan(expected_maximum):
            # yapf: disable
            expected_maximum = None  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
            # yapf: enable
          row['parameters'][-1]['data'][-1][
              'expectedMaximum'] = expected_maximum
        row['parameters'][-1]['data'][-1]['textValue'] = data_dct.get(
            'textValue')
        row['parameters'][-1]['data'][-1]['expectedRegex'] = data_dct.get(
            'expectedRegex')
        row['parameters'][-1]['data'][-1]['serializedValue'] = data_dct.get(
            'serializedValue')

    # station.init
    row['count'] = event.get('count')
    row['success'] = event.get('success')
    row['failureMessage'] = event.get('failureMessage')

    # station.message
    row['message'] = event.get('message')
    row['lineNumber'] = event.get('lineNumber')
    row['functionName'] = event.get('functionName')
    row['logLevel'] = event.get('logLevel')
    row['testRunId'] = event.get('testRunId')  # also in station.test_run

    # station.test_run
    row['testName'] = event.get('testName')
    row['testType'] = event.get('testType')

    row['arguments'] = []
    for key, dct in event.get('arguments', {}).items():
      row['arguments'].append({})
      row['arguments'][-1]['key'] = key
      row['arguments'][-1]['description'] = dct.get('description')
      # Cast to string since it can be any type.
      row['arguments'][-1]['value'] = dct.get('value')

    row['status'] = event.get('status')
    row['startTime'] = DateTimeToUnixTimestamp(event.get('startTime'))
    row['endTime'] = DateTimeToUnixTimestamp(event.get('endTime'))
    row['duration'] = event.get('duration')
    row['operatorId'] = event.get('operatorId')

    row['attachments'] = []
    for key, dct in event.get('attachments', {}).items():
      row['attachments'].append({})
      row['attachments'][-1]['key'] = key
      row['attachments'][-1]['description'] = dct.get('description')
      row['attachments'][-1]['path'] = dct.get('path')
      # Check to see whether the attachment path has been modified by
      # UploadAttachments.  If so, use that path instead.
      if ('__attachments__' in event and
          key in event['__attachments__']):
        row['attachments'][-1]['path'] = event['__attachments__'][key]
      row['attachments'][-1]['mimeType'] = dct.get('mimeType')

    row['failures'] = []
    for i, dct in enumerate(event.get('failures', [])):
      row['failures'].append({})
      row['failures'][-1]['id'] = i
      row['failures'][-1]['code'] = dct.get('code')
      row['failures'][-1]['details'] = dct.get('details')

    row['serialized'] = event.Serialize()
    return json.dumps(row, allow_nan=False)


if __name__ == '__main__':
  plugin_base.main()
