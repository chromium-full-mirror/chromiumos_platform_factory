# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Probes information from /org/freedesktop/ModemManager1.

Description
-----------
This test can probe requested data, including
``NAME={'imei', 'meid', 'lte_imei', 'lte_iccid'}`` from
/org/freedesktop/ModemManager1. When the argument ``probe_{NAME}`` is set
``True``, the data ``NAME`` will be logged and saved to device data.

The ``fields`` argument is a dictionary containing multiple
(``NAME``, ``FIELD``) pairs. It will override the following default fields:

============= ================== ===============
NAME          FIELD              probe_{NAME}
============= ================== ===============
``imei``      ``imei``           True
``meid``      ``meid``           True
``lte_imei``  ``Imei``           False
``lte_iccid`` ``SimIdentifier``  False
============= ================== ===============

Test Procedure
--------------
This is an automated test without user interaction.

The test will probe specific data from /org/freedesktop/ModemManager1, then log
to ``cros.factory.testlog`` and save to ``cros.factory.test.device_data``.

Dependency
----------
Some modems may have different identities for each fields. For example, Fibocom
LTE module will identify imei as ``EquipmentIdentifier``, so you will need
to specify the ``fields`` argument.

Examples
--------
The following argument will probe imei from field ``EquipmentIdentifier``:

.. test_list::

  generic_cellular_examples:ProbeImei

Example output::

  # "factory device-data" output before this test
  serials:
    serial_number: 12345678

  # "factory device-data" output after this test
  component:
    cellular:
      imei: '862227050001326'
  serials:
    serial_number: 12345678

"""

import logging
import unittest

from cros.factory.test import device_data
from cros.factory.test import event_log  # TODO(chuntsen): Deprecate event log.
from cros.factory.test.rf import cellular
from cros.factory.test import test_tags
from cros.factory.testlog import testlog
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import process_utils


class ProbeCellularInfoTest(unittest.TestCase):
  related_components = (test_tags.TestCategory.WWAN, )
  ARGS = [
      Arg('probe_imei', bool, 'Whether to probe IMEI', True),
      Arg('probe_meid', bool, 'Whether to probe MEID', True),
      Arg('probe_lte_imei', bool, 'Whether to probe IMEI on LTE modem', False),
      Arg('probe_lte_iccid', bool, 'Whether to probe ICCID on LTE SIM card',
          False),
      Arg('fields', dict,
          ('Specify the fields to probe. A {NAME: FIELD} pair will record the'
           'value of FIELD to KEY_COMPONENT.cellular.NAME'), {})
  ]

  def runTest(self):
    output = process_utils.CheckOutput(['modem', 'status'], log=True)
    logging.info('modem status output:\n%s', output)

    names = []
    fields = []
    for name, field, enabled in (
        # yapf: disable
        ('imei', 'imei', self.args.probe_imei),  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        ('meid', 'meid', self.args.probe_meid),  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        ('lte_imei', 'Imei', self.args.probe_lte_imei),  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        ('lte_iccid', 'SimIdentifier', self.args.probe_lte_iccid)):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      if not enabled:
        continue

      # yapf: disable
      field = self.args.fields[name] if name in self.args.fields else field  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      names.append(name)
      fields.append(field)

    values = [None] * len(fields)
    all_info = cellular.ProbeSimInfo(fields) + [cellular.ProbeModemInfo(fields)]
    for info in all_info:
      for index, value in enumerate(info):
        if value is not None:
          values[index] = value
    data = dict(zip(names, values))

    event_log.Log('cellular_info', modem_status_stdout=output, **data)
    testlog.LogParam('modem_status_stdout', output)
    for k, v in data.items():
      testlog.LogParam(k, v)

    missing = sorted(set(k for k, v in data.items() if v is None))
    self.assertFalse(
        missing,
        f"Missing elements in '/org/freedesktop/ModemManager1': {missing}")

    logging.info('Probed data: %s', data)
    device_data.UpdateDeviceData({
        device_data.JoinKeys(device_data.KEY_COMPONENT, 'cellular', name): value
        for name, value in data.items()
    })
