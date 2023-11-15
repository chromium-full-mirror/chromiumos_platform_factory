# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import json
import os
import unittest
from unittest import mock

from cros.factory.test.env import paths
from cros.factory.test.test_lists import test_list_common
from cros.factory.test_list_editor.backend.models import files
from cros.factory.utils import process_utils


class TestTestListFileFactory(unittest.TestCase):

  def setUp(self):
    self.test_list_factory = files.GetFactoryInstance()

  def testGetJSON(self):
    json_test_list = self.test_list_factory.Get(data={}, filename='',
                                                diff_data={})
    self.assertIsInstance(json_test_list, files.TestListFile)


class TestTestListFile(unittest.TestCase):

  def setUp(self):
    self.data = {
        'foo': 'bar'
    }
    self.filename = 'fake.test_list'
    self.test_list_file = files.TestListFile(self.data, self.filename, {})

  @mock.patch.object(json, 'dump')
  def testSaveDiffToDisk(self, mock_write: mock.Mock):
    with mock.patch('builtins.open'):
      self.test_list_file.SaveDiff()
      mock_write.assert_called_once()

  @mock.patch.object(test_list_common, 'SaveTestList')
  def testSaveToDisk(self, mock_save: mock.Mock):
    self.test_list_file.Save()

    mock_save.assert_called_once_with(self.data,
                                      self.filename.removesuffix('.test_list'))

  @mock.patch.object(os, 'path')
  @mock.patch.object(json, 'load')
  @mock.patch.object(test_list_common, 'LoadTestList')
  def testLoadFromDisk(self, mock_load_test_list: mock.Mock,
                       mock_json_load: mock.Mock, mock_path_exists: mock.Mock):
    fake_data = {
        'test': True
    }
    fake_diff_data = {
        'diff_data': True
    }
    mock_load_test_list.return_value = fake_data
    mock_path_exists.exists.return_value = True
    mock_json_load.return_value = fake_diff_data
    self.test_list_file = files.TestListFile({}, self.filename, {})

    with mock.patch('builtins.open'):
      self.test_list_file.Load()
      self.assertEqual(self.test_list_file.data, fake_data)
      self.assertEqual(self.test_list_file.diff_data, fake_diff_data)

    mock_path_exists.exists.return_value = False

    self.test_list_file.Load()
    self.assertEqual(self.test_list_file.diff_data, {})

  @mock.patch.object(json, 'load')
  @mock.patch.object(test_list_common, 'LoadTestList')
  def testRaisesExceptionIfPathNotSet(
      self,
      mock_load_test_list: mock.Mock,  # pylint: disable=unused-argument
      mock_json_load: mock.Mock):  # pylint: disable=unused-argument
    file = files.TestListFile()
    with self.assertRaises(files.FilepathNotSetException):
      file.Save()

    with self.assertRaises(files.FilepathNotSetException):
      file.SaveDiff()


class TestUtilFunctions(unittest.TestCase):

  def setUp(self) -> None:
    self.factory_path = os.path.join(paths.FACTORY_PYTHON_DIR, 'test',
                                     'test_lists')
    self.target_folder = '/tmp/editor-testing-123'

  @mock.patch.object(os, 'makedirs')
  @mock.patch.object(process_utils, 'CheckCall')
  def testCopyAndUpdateTestLists(self, mock_check_call: mock.Mock,
                                 mock_makedirs: mock.Mock):
    files.CopyAndUpdateTestLists(self.target_folder)
    source_folder = os.path.join(self.factory_path, '')
    expected_rsync_args = [
        'rsync',
        '-acm',
        '--include=*.test_list.json',
        '--include=*.schema.json',
        '--exclude=*/',
        '--exclude=*',
        source_folder,
        self.target_folder,
    ]
    mock_check_call.assert_called_with(expected_rsync_args)
    mock_makedirs.assert_called_with(self.target_folder)
