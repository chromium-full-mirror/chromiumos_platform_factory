#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest
from unittest import mock

from flask import Flask  # type: ignore #TODO(b/338318729) Fixit!

from cros.factory.test_list_editor.backend.api.v1 import tests
from cros.factory.test_list_editor.backend.controller import test_list
from cros.factory.test_list_editor.backend.models import files as file_model
from cros.factory.test_list_editor.backend.schema import common as common_schema
from cros.factory.test_list_editor.backend.schema import test_list as test_list_schema


class TestTestsEndpoint(unittest.TestCase):

  def setUp(self) -> None:
    with mock.patch.object(
        tests.test_list_controller, 'TestListController',
        spec=test_list.TestListController) as mock_tl_controller:
      mock_controller = mock.Mock()
      mock_controller.GetTestSequence.return_value = (
          test_list_schema.TestSequenceResponse(
              status=common_schema.StatusEnum.SUCCESS, data=[]))
      mock_controller.UpdateTestSequence.return_value = (
          test_list_schema.TestSequenceResponse(
              status=common_schema.StatusEnum.SUCCESS, data=[]))
      mock_tl_controller.return_value = mock_controller
      flask_app = Flask(__name__)
      flask_app.register_blueprint(tests.CreateBP())
      self.client = flask_app.test_client()
      self.user_session_header = {
          'user_id': 'uid123',
          'session_id': 'sid123',
      }

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testGetTestSequence(self, _: mock.Mock):
    response = self.client.get('/api/v1/tests/fake.test_list',
                               headers=self.user_session_header)
    self.assertEqual(response.status_code, 200)

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testUpdateTestSequence(self, _: mock.Mock):

    data = {
        'data': {
            'test_item_id': 'A',
            'subtests': []
        },
    }
    response = self.client.put('/api/v1/tests/fake.test_list', json=data,
                               headers=self.user_session_header)
    self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
  unittest.main()
