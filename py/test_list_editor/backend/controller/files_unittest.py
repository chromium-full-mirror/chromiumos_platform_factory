# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from flask import Flask  # type: ignore #TODO(b/338318729) Fixit!
from flask import g

from cros.factory.test_list_editor.backend.controller import files as file_controller
from cros.factory.test_list_editor.backend.schema import common as common_schema


class TestFilesController(unittest.TestCase):

  def setUp(self) -> None:
    self.file_factory_mock = mock.Mock()
    self.file_mock = mock.Mock()
    self.file_factory_mock.Get.return_value = self.file_mock
    self.file_controller = file_controller.FileController(
        self.file_factory_mock)

    self.flask_app = Flask(__name__)

  def testValidateAllFiles(self):
    files_request = mock.Mock()
    files_request.files = [
        mock.Mock(filename='foo1.txt', data={}),
        mock.Mock(filename='foo2.txt', data={})
    ]
    controller = file_controller.FileController(self.file_factory_mock)

    with self.flask_app.app_context():
      g.session_folder = '/tmp/editor/uid123/sid123'
      response = controller.SaveFiles(files_request)

    self.assertEqual(response.status, common_schema.StatusEnum.SUCCESS)
