#!/usr/bin/env python3
# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import unittest
from unittest import mock

from cros.factory.test.env import paths
from cros.factory.utils import sys_utils


_GET_PATH = 'GetRunningFactoryPythonArchivePath'


class GetFactoryPythonArchivePathUnittest(unittest.TestCase):

  @mock.patch.object(sys_utils, _GET_PATH, mock.Mock(return_value=None))
  @mock.patch.object(os.path, 'exists', autospec=True)
  def testLocalFactoryPythonArchiveRegularParExists(self, mock_exists):
    mock_exists.side_effect = lambda p: p.endswith('factory.par')
    expected = os.path.join(paths.FACTORY_DIR, 'factory.par')

    self.assertEqual(paths.GetFactoryPythonArchivePath(), expected)

  @mock.patch.object(sys_utils, _GET_PATH, mock.Mock(return_value=None))
  @mock.patch.object(os.path, 'exists', autospec=True)
  def testLocalFactoryPythonArchiveMiniParExists(self, mock_exists):
    expected = os.path.join(paths.FACTORY_DIR, 'factory-mini.par')
    mock_exists.side_effect = lambda p: p == expected

    self.assertEqual(paths.GetFactoryPythonArchivePath(), expected)

  @mock.patch.object(sys_utils, _GET_PATH, mock.Mock(return_value=None))
  @mock.patch.object(os.path, 'exists', autospec=True)
  def testLocalFactoryPythonArchiveTestImageMiniParExists(self, mock_exists):
    expected = '/usr/local/factory-mini/factory-mini.par'
    mock_exists.side_effect = lambda p: p == expected

    self.assertEqual(paths.GetFactoryPythonArchivePath(), expected)

  @mock.patch.object(sys_utils, _GET_PATH, mock.Mock(return_value=None))
  @mock.patch.object(os.path, 'exists', mock.Mock(return_value=False))
  def testLocalFactoryPythonArchiveParNotExists(self):
    with self.assertRaisesRegex(EnvironmentError,
                                'cannot find factory python archive'):
      unused_var = paths.GetFactoryPythonArchivePath()

  @mock.patch.object(sys_utils, _GET_PATH, autospec=True)
  def testLocalFactoryPythonArchiveRunningPar(self, mock_get_path):
    expected = '/path/to/running/factory/par'
    mock_get_path.return_value = expected
    self.assertEqual(paths.GetFactoryPythonArchivePath(), expected)


class PathExistenceUnittest(unittest.TestCase):

  def _CheckDirectoryAndContent(self, dir_path, expected_content):
    self.assertTrue(os.path.exists(dir_path))
    self.assertTrue(os.path.isdir(dir_path))
    # check some files under |dir_path| to gain confidence that we are looking
    # at the right path.
    for filename in expected_content:
      filepath = os.path.join(dir_path, filename)
      with self.subTest(filename=filename, filepath=filepath):
        self.assertTrue(os.path.exists(filepath))

  def testFactoryDir(self):
    self._CheckDirectoryAndContent(paths.FACTORY_DIR, ['py', 'CODING_STYLE.md'])

  def testFactoryPythonDir(self):
    self._CheckDirectoryAndContent(paths.FACTORY_PYTHON_DIR,
                                   ['utils', 'test', 'probe', 'hwid'])


if __name__ == '__main__':
  unittest.main()
