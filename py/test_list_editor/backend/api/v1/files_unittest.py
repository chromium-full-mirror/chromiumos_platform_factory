#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest
from unittest import mock

from cros.factory.test.test_lists import test_list_common
from cros.factory.test_list_editor.backend.main import CreateApp
from cros.factory.test_list_editor.backend.models import files as file_model
from cros.factory.test_list_editor.backend.schema import common as common_schema
from cros.factory.test_list_editor.backend.schema import files as file_schema


class TestFilesEndpoint(unittest.TestCase):

  def setUp(self) -> None:
    self.app = CreateApp()
    self.client = self.app.test_client()

    self.user_session_header = {
        'user_id': 'uid123',
        'session_id': 'sid123',
    }

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  @mock.patch.object(test_list_common, 'SaveTestList')
  def testSuccessFiles(self, mock_save, _: mock.Mock):  # pylint: disable=unused-argument
    file1 = file_schema.FileObject(
        filename='foo1.json', data={
            'inherit': [],
            'options': {},
            'constants': {},
            'definitions': {}
        })
    files_request = file_schema.FilesRequest(files=[file1])
    response = self.client.put('/api/v1/files/', json=files_request.dict(),
                               headers=self.user_session_header)

    self.assertEqual(response.status_code, 200)

    self.assertEqual(response.get_json()['status'],
                     common_schema.StatusEnum.SUCCESS)


if __name__ == '__main__':
  unittest.main()
