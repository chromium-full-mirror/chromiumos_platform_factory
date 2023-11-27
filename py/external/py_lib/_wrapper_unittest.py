#!/usr/bin/env python3
#
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unittest for the wrapper for loading external module."""

import importlib
import os
import pathlib
import unittest
from unittest import mock

from cros.factory.external.py_lib import _wrapper


def MockImportFailAlternativeSuccess(name: str):
  if name == 'dbus':
    raise ImportError('MockImportError')
  mocked_module = mock.Mock()
  mocked_module.__dict__ = {
      'FAKE_MODULE_LEVEL_CONSTANT': 'FAKE_VALUE'
  }
  return mocked_module


class ExternalWrapperLoadModuleTest(unittest.TestCase):

  _normal_module_path = pathlib.Path(
      '/usr/local/factory/cros/factory/external/py_lib/dbus')

  def setUp(self):
    self.import_module = mock.patch.object(importlib, 'import_module').start()
    self.getenv = mock.patch.object(os, 'getenv').start()
    self.getenv.return_value = False
    self.mocked_locals = mock.Mock(spec=dict)
    self.addCleanup(mock.patch.stopall)

  def testImportNormal_Success(self):
    module_ready = _wrapper.ExternalWrapperLoadModule(self._normal_module_path,
                                                      self.mocked_locals)

    self.assertEqual(self.import_module.call_args_list, [
        mock.call('dbus'),
    ])
    self.mocked_locals.update.assert_called()
    self.assertTrue(module_ready)

  def testImportOutOfPyLib_ValueError(self):
    module_path = pathlib.Path('/usr/local/factory/dbus')

    with self.assertRaises(ValueError):
      _wrapper.ExternalWrapperLoadModule(module_path, self.mocked_locals)

    self.import_module.assert_not_called()
    self.mocked_locals.update.assert_not_called()

  def testImportSubDirectoryModule_Success(self):
    module_path = pathlib.Path(
        '/usr/local/factory/cros/factory/external/py_lib/gi/repository')

    module_ready = _wrapper.ExternalWrapperLoadModule(module_path,
                                                      self.mocked_locals)

    self.assertEqual(self.import_module.call_args_list, [
        mock.call('gi.repository'),
    ])
    self.mocked_locals.update.assert_called()
    self.assertTrue(module_ready)

  def testImportFailDebugSet_Raise(self):
    self.import_module.side_effect = MockImportFailAlternativeSuccess
    self.getenv.return_value = True

    with self.assertRaisesRegex(ImportError, 'MockImportError'):
      _wrapper.ExternalWrapperLoadModule(self._normal_module_path,
                                         self.mocked_locals)

    self.assertEqual(self.import_module.call_args_list, [
        mock.call('dbus'),
    ])
    self.mocked_locals.update.assert_not_called()

  def testImportFailAlternativeSuccess_UseAlternative(self):
    self.import_module.side_effect = MockImportFailAlternativeSuccess

    module_ready = _wrapper.ExternalWrapperLoadModule(self._normal_module_path,
                                                      self.mocked_locals)

    self.assertEqual(self.import_module.call_args_list, [
        mock.call('dbus'),
        mock.call('cros.factory.external.py_lib._dummy.dbus'),
    ])
    self.mocked_locals.update.assert_called_once_with(
        {'FAKE_MODULE_LEVEL_CONSTANT': 'FAKE_VALUE'})
    self.assertFalse(module_ready)

  def testImportFailAlternativeFail_ImportNothing(self):
    self.import_module.side_effect = ImportError()

    module_ready = _wrapper.ExternalWrapperLoadModule(self._normal_module_path,
                                                      self.mocked_locals)

    self.assertEqual(self.import_module.call_args_list, [
        mock.call('dbus'),
        mock.call('cros.factory.external.py_lib._dummy.dbus'),
    ])
    self.mocked_locals.update.assert_not_called()
    self.assertFalse(module_ready)


if __name__ == '__main__':
  unittest.main()
