# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import abc
import json
import os
import threading
from typing import Optional

from cros.factory.test.env import paths
from cros.factory.test.test_lists import test_list_common
from cros.factory.utils import process_utils


TEST_LIST_CONFIG_DIR = os.path.join(paths.FACTORY_PYTHON_DIR, 'test',
                                    'test_lists')

TEST_LIST_FILE_GLOB = '*.test_list.json'
TEST_LIST_SCHEMA_FILE_GLOB = '*.schema.json'

TEST_LIST_STORAGE_DIR = '/tmp/editor'
# TODO(louischiu): Set up different storage location for GCP env.

JSON_FILE_SUFFIX = '.json'
DIFF_FILE_PREFIX = 'diff.'


class ITestListFile(abc.ABC):
  """Abstract base class for test list files.

  This class defines the interface for saving and loading test list files.

  The `diff_data` for now only stores one change. All of the changes are
  squashed into one dictionary. In the future, if we want to support undo/redo
  operations, we can expand this into an array of changes (deltas).

  Attribute:
    data (dict): A dictionary of test items.
    diff_data (dict): A dictionary containing diff data.
  """

  def __init__(self, data: dict, diff_data: dict) -> None:
    self.data = data
    self.diff_data = diff_data

  @abc.abstractmethod
  def Save(self) -> None:
    """Saves the test list file."""

  @abc.abstractmethod
  def SaveDiff(self) -> None:
    """Saves the diff test list file."""

  @abc.abstractmethod
  def Load(self) -> None:
    """Loads the test list file and diff data."""


class FolderPathInvalid(Exception):
  """Exception to raise when folder path is not set to the right location."""


class TestListFile(ITestListFile):
  """The container for JSON test list file.

  This class represents a container for JSON test list file. It will load the
  corresponding base test list and its diff file.

  Args:
    folder_path (str): The path to the folder that stores test lists.
    filename (str): The name of the test list. The `filename` does not need
      to include ".json".
    data (dict): A dictionary of test items.
    diff_data (dict): A dictionary containing diff data.
  """

  def __init__(self, folder_path: str, filename: str,
               data: Optional[dict] = None, diff_data: Optional[dict] = None):
    data = data or {}
    diff_data = diff_data or {}
    super().__init__(data, diff_data)
    self.folder_path = folder_path
    if not folder_path.startswith(TEST_LIST_STORAGE_DIR):
      raise FolderPathInvalid(f'Expected to start with {TEST_LIST_STORAGE_DIR}'
                              f'received: {folder_path}')
    self.filename = filename
    self.diff_file_path = os.path.join(
        self.folder_path, DIFF_FILE_PREFIX + filename + JSON_FILE_SUFFIX)

  def Save(self):
    """Saves test list to JSON file.

    Refer to the underlying function for detailed exceptions.
    """
    test_list_common.SaveTestList(self.data,
                                  self.filename.removesuffix('.test_list'),
                                  self.folder_path)

  def SaveDiff(self) -> None:
    """Save the diff to test list diff file."""
    with open(self.diff_file_path, 'w', encoding='UTF-8') as file:
      json.dump(self.diff_data, file)

  def Load(self):
    """Loads the test list file and diff data.

    This method loads the test list JSON file and its diff data into
    `self.data` and `self.diff_data`.
    """
    self.data = test_list_common.LoadTestList(self.filename, self.folder_path)

    if not os.path.exists(self.diff_file_path):
      self.diff_data = {}
      return

    with open(self.diff_file_path, 'r', encoding='UTF-8') as file:
      self.diff_data = json.load(file)


class ITestListFileFactory(abc.ABC):
  """Factory interface of the test list."""

  @abc.abstractmethod
  def Get(self, folder_path: str, filename: str, **kwargs) -> ITestListFile:
    """Abstract method for getting file interface."""


class TestListFileFactory(ITestListFileFactory):
  """Factory interface of the test list."""

  def __init__(self) -> None:
    # TODO: We limit the use case to only consider using JSON file. Revisit this
    # part if we have other use case than JSON.
    self._store = TestListFile

  def Get(self, folder_path: str, filename: str, **kwargs) -> ITestListFile:
    """Return an instance of the test list file.

    Args:
      **kwargs: Additional keyword arguments to pass to the constructor.

    Returns:
      TestListFile: An instance of the test list file.
    """
    return self._store(folder_path, filename, **kwargs)


_file_factory = None
_file_factory_lock = threading.Lock()


def GetFactoryInstance() -> TestListFileFactory:
  global _file_factory  # pylint: disable=global-statement
  with _file_factory_lock:
    if _file_factory is None:
      _file_factory = TestListFileFactory()
  return _file_factory


def CopyAndUpdateTestLists(target_folder: str):
  """Compares and updates test list files inside `target_folder`.

  This function uses `rsync` to synchronize the files between
  `py/test/test_lists` and the `target_folder`.

  Args:
    target_folder (str): The path of the folder to compare against the
      factory test list folder.
  """

  # Add trialing slash to sync the contents inside the folder.
  source_folder = os.path.join(TEST_LIST_CONFIG_DIR, '')

  if not os.path.exists(target_folder):
    os.makedirs(target_folder)

  process_utils.CheckCall([
      'rsync', '-acm', f'--include={TEST_LIST_FILE_GLOB}',
      f'--include={TEST_LIST_SCHEMA_FILE_GLOB}', '--exclude=*/', '--exclude=*',
      source_folder, target_folder
  ])
