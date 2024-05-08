# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

# yapf: enable
# yapf: disable
from flask import Flask  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
from flask import g

from cros.factory.test_list_editor.backend.controller import test_list as test_list_controller
from cros.factory.test_list_editor.backend.models import test_list as test_list_model
from cros.factory.test_list_editor.backend.schema import common as common_schema
from cros.factory.test_list_editor.backend.schema import test_list as test_list_schema


class TestItemsController(unittest.TestCase):

  def setUp(self) -> None:
    self.fake_factory = mock.Mock()
    self.fake_loaded_data = mock.Mock()
    self.fake_test_list = mock.Mock(spec=test_list_model.TestList)
    self.fake_test_list.GetTestDefinitions.return_value = {}
    self.fake_test_list.GetTestItemConfig.return_value = {
        'test_item_id': '',
        'display_name': ''
    }
    self.fake_test_list.GetTestSequence.return_value = [{
        'test_item_id': '',
        'display_name': '',
        'subtests': []
    }]
    self.fake_diff = mock.Mock(spec=test_list_model.DiffUnit)
    self.flask_app = Flask(__name__)

  def testGetItemList(self):
    self.fake_factory.Get.return_value = self.fake_loaded_data
    controller = test_list_controller.TestListController(self.fake_factory)

    with self.flask_app.app_context():
      g.session_folder = '/tmp/editor/uid123/sid123'
      response = controller.GetTestListItemList('fake_test_list',
                                                self.fake_test_list)
    self.assertEqual(response.status, common_schema.StatusEnum.SUCCESS)
    self.assertEqual(response.data, {})

  def testGetItem(self):
    self.fake_loaded_data.data = {}
    self.fake_factory.Get.return_value = self.fake_loaded_data
    controller = test_list_controller.TestListController(self.fake_factory)

    with self.flask_app.app_context():
      g.session_folder = '/tmp/editor/uid123/sid123'
      response = controller.GetItem('fake_test_list', self.fake_test_list,
                                    'test123')
    self.assertEqual(response.status, common_schema.StatusEnum.SUCCESS)
    self.assertEqual(
        response.data, {
            'test_item_id': '',
            'display_name': '',
        })

  def testCreateItem(self):
    self.fake_loaded_data.diff_data = {
        'diff_data': True
    }
    self.fake_loaded_data.data = {}
    self.fake_factory.Get.return_value = self.fake_loaded_data

    fake_item = test_list_schema.TestItem(
        test_item_id='test123', display_name='test123', subtests=['a', 'b'],
        inherit='test321')

    controller = test_list_controller.TestListController(self.fake_factory)

    with self.flask_app.app_context():
      g.session_folder = '/tmp/editor/uid123/sid123'
      response = controller.CreateItem('', mock.Mock(), fake_item)
    self.assertEqual(response.status, common_schema.StatusEnum.SUCCESS)
    self.assertEqual(
        response.data, {
            'test_item_id': 'test123',
            'display_name': 'test123',
            'subtests': ['a', 'b'],
            'inherit': 'test321'
        })

  def testUpdateItem(self):
    self.fake_loaded_data.diff_data = {
        'diff_data': True
    }
    self.fake_loaded_data.data = {}
    self.fake_factory.Get.return_value = self.fake_loaded_data

    fake_item = test_list_schema.TestItem(
        test_item_id='test123', display_name='test123', subtests=['a', 'b'],
        inherit='test321')

    controller = test_list_controller.TestListController(self.fake_factory)
    mock_request_body = mock.Mock()
    mock_request_body.data = fake_item

    with self.flask_app.app_context():
      g.session_folder = '/tmp/editor/uid123/sid123'
      response = controller.UpdateItem('', mock.Mock(), fake_item)
    self.assertEqual(response.status, common_schema.StatusEnum.SUCCESS)
    self.assertEqual(
        response.data, {
            'test_item_id': 'test123',
            'display_name': 'test123',
            'subtests': ['a', 'b'],
            'inherit': 'test321'
        })

  def testGetTestSequence(self):
    controller = test_list_controller.TestListController(self.fake_factory)

    with self.flask_app.app_context():
      g.session_folder = '/tmp/editor/uid123/sid123'
      response = controller.GetTestSequence('fake_list_id', self.fake_test_list)
    self.assertEqual(response.status, common_schema.StatusEnum.SUCCESS)
    self.assertEqual(response.data, [{
        'test_item_id': '',
        'display_name': '',
        'subtests': []
    }])

  def testUpdateTestSequence(self):
    self.fake_loaded_data.diff_data = {
        'diff_data': True
    }
    self.fake_loaded_data.data = {}
    self.fake_factory.Get.return_value = self.fake_loaded_data

    self.fake_test_list.GetTestSequence.return_value = [{
        'test_item_id': 'test123',
        'display_name': 'test123',
        'subtests': []
    }]

    fake_item = test_list_schema.UpdatedTestSequence(test_item_id='test123',
                                                     subtests=[])

    controller = test_list_controller.TestListController(self.fake_factory)

    with self.flask_app.app_context():
      g.session_folder = '/tmp/editor/uid123/sid123'
      response = controller.UpdateTestSequence('', self.fake_test_list,
                                               fake_item)

    self.assertEqual(response.status, common_schema.StatusEnum.SUCCESS)
    self.assertEqual(response.data, [{
        'test_item_id': 'test123',
        'display_name': 'test123',
        'subtests': [],
    }])
