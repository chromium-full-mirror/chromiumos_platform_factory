#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest
from unittest import mock

from flask import Flask  # type: ignore #TODO(b/338318729) Fixit!

from cros.factory.test_list_editor.backend.api.v1 import items
from cros.factory.test_list_editor.backend.controller import test_list
from cros.factory.test_list_editor.backend.models import files as file_model
from cros.factory.test_list_editor.backend.schema import common as common_schema
from cros.factory.test_list_editor.backend.schema import test_list as test_list_schema


class TestItemsEndpoint(unittest.TestCase):

  def setUp(self) -> None:
    with mock.patch.object(
        items.test_list_controller, 'TestListController',
        spec=test_list.TestListController) as mock_tl_controller:
      self.mock_data = test_list_schema.TestItem(test_item_id='ABC',
                                                 display_name='A B C')
      mock_tl_controller.return_value.GetTestListItemList.return_value = (
          test_list_schema.ItemListResponse(
              status=common_schema.StatusEnum.SUCCESS,
              data={'ABC': self.mock_data}))
      mock_tl_controller.return_value.GetItem.return_value = (
          test_list_schema.TestItemsResponse(
              status=common_schema.StatusEnum.SUCCESS, data=self.mock_data))
      mock_tl_controller.return_value.CreateItem.return_value = (
          test_list_schema.TestItemsResponse(
              status=common_schema.StatusEnum.SUCCESS, data=self.mock_data))
      mock_tl_controller.return_value.UpdateItem.return_value = (
          test_list_schema.TestItemsResponse(
              status=common_schema.StatusEnum.SUCCESS, data=self.mock_data))

      flask_app = Flask(__name__)
      flask_app.register_blueprint(items.CreateBP())
      self.client = flask_app.test_client()

    self.user_session_header = {
        'user_id': 'uid123',
        'session_id': 'sid123',
    }

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testGetItemList(self, _: mock.Mock):
    response = self.client.get('/api/v1/items/fake.test_list',
                               headers=self.user_session_header)
    self.assertEqual(response.status_code, 200)

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testGetItem(self, _: mock.Mock):
    response = self.client.get('/api/v1/items/fake.test_list/ABC',
                               headers=self.user_session_header)
    self.assertEqual(response.status_code, 200)

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testCreateItems(self, _: mock.Mock):
    data = {
        'data': self.mock_data.dict(),
    }
    response = self.client.post('/api/v1/items/fake.test_list', json=data,
                                headers=self.user_session_header)
    self.assertEqual(response.status_code, 200)

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testUpdateItems(self, _: mock.Mock):
    data = {
        'data': self.mock_data.dict(),
    }
    response = self.client.put('/api/v1/items/fake.test_list', json=data,
                               headers=self.user_session_header)
    self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
  unittest.main()
