# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os.path
import unittest

from cros.factory.hwid.service.appengine.data import firmware_qual
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3 import database


_FirmwareQual = hwid_api_messages_pb2.FirmwareQual

HWIDV3_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'testdata',
    'v3-from-factory-bundle.yaml')


class FirmwareQualTest(unittest.TestCase):

  def testPatchFirmareQualStatus_Success(self):
    db = database.Database.LoadFile(HWIDV3_FILE, verify_checksum=False)

    firmware_quals = [_FirmwareQual(build_version='1111.1.1')]
    new_db = firmware_qual.PatchFirmwareQualStatus(db, firmware_quals)

    self.assertEqual(
        new_db.GetComponents('ro_main_firmware')['ro_main_firmware_1'].status,
        'supported')
    self.assertEqual(
        new_db.GetComponents('ro_ec_firmware')['ro_ec_firmware_1'].status,
        'supported')


if __name__ == '__main__':
  unittest.main()
