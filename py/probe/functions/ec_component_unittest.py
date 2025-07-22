#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import subprocess
import textwrap
import unittest
from unittest import mock

from cros.factory.device import device_utils
from cros.factory.gooftool import common as gooftool_common
from cros.factory.probe.functions import ec_component
from cros.factory.probe.runtime_probe import runtime_probe_adapter
from cros.factory.utils import json_utils
from cros.factory.utils import process_utils
from cros.factory.utils import sys_utils

from cros.factory.external.chromeos_cli import cros_config as cros_config_module


class ECComponentTest(unittest.TestCase):

  MOUNT_POINT = '/tmp/mnt'
  IMAGE_NAME = 'foo'
  ACTIVE_VERSION = 'model-0.0.0-abcdefa'
  ACTIVE_ISH_VERSION = 'model-ish-1_2_3-12345.0.0'
  ISH_PROJECT_NAME = 'model-ish'
  ISH_VERSION_RESP = textwrap.dedent('''\
      RO version:    model-ish-1_2_3-12345.0.0
      RW version:    model-ish-1_2_3-67890.0.0
      Firmware copy: RO
      Build info:    model-ish-1_2_3-12345.0.0 2015-07-16 11:31:57 @build291-m2
      Tool version:  v2.0.20247-b863c6d01b 2015-07-16 11:31:57''')

  def setUp(self):
    super().setUp()

    mock.patch.object(gooftool_common, 'Util', autospec=True).start()

    patcher = mock.patch.object(runtime_probe_adapter, 'RunProbeFunction',
                                autospec=True)
    self._mock_runtime_probe_func = patcher.start()

    patcher = mock.patch.object(cros_config_module.CrosConfig,
                                'GetFirmwareImageName', autospec=True)
    patcher.start().return_value = self.IMAGE_NAME

    patcher = mock.patch.object(device_utils, 'CreateDUTInterface',
                                autospec=True)
    patcher.start().return_value.ec.GetActiveVersion.return_value = (
        self.ACTIVE_VERSION)

    patcher = mock.patch.object(json_utils, 'LoadFile', autospec=True)
    self._mock_load_file = patcher.start()

    patcher = mock.patch.object(os.path, 'exists', autospec=True)
    self._mock_exists = patcher.start()

    patcher = mock.patch.object(process_utils, 'CheckOutput', autospec=True)
    self._mock_check_output = patcher.start()

    self.addCleanup(mock.patch.stopall)

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_SuccessWithReleaseManifest(self, mock_mount):
    self._mock_check_output.side_effect = subprocess.CalledProcessError(
        1, 'unused error info')
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_load_file.return_value = {
        'ec_version': self.ACTIVE_VERSION
    }
    self._mock_exists.side_effect = [False, True]

    ec_component.ECComponent().Probe()

    called_args = self._mock_runtime_probe_func.call_args.args[1]
    self.assertEqual(
        called_args.get('manifest_path'),
        f'{self.MOUNT_POINT}/usr/share/cme/{self.IMAGE_NAME}'
        '/component_manifest.json')
    self.assertIsNone(called_args.get('ish_manifest_path'))

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_ECVersionNotMatch(self, mock_mount):
    self._mock_check_output.side_effect = subprocess.CalledProcessError(
        1, 'unused error info')
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_load_file.return_value = {
        'ec_version': 'another-version'
    }
    self._mock_exists.side_effect = [False, True]
    with self.assertRaises(ec_component.ECVersionNotMatchError):
      ec_component.ECComponent().Probe()

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_ECManifestNotFound(self, mock_mount):
    self._mock_check_output.side_effect = subprocess.CalledProcessError(
        1, 'unused error info')
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_exists.side_effect = [False, False]
    with self.assertRaises(ec_component.ECManifestNotFoundError):
      ec_component.ECComponent().Probe()

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_SuccessWithLocalManifest(self, mock_mount):
    self._mock_check_output.side_effect = subprocess.CalledProcessError(
        1, 'unused error info')
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_load_file.return_value = {
        'ec_version': self.ACTIVE_VERSION
    }
    self._mock_exists.side_effect = [True, True]

    ec_component.ECComponent().Probe()

    called_args = self._mock_runtime_probe_func.call_args.args[1]
    self.assertEqual(
        called_args.get('manifest_path'),
        f'/usr/local/factory/cme/{self.IMAGE_NAME}/component_manifest.json')
    self.assertIsNone(called_args.get('ish_manifest_path'))

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_ISH_SuccessWithReleaseManifest(self, mock_mount):
    self._mock_check_output.return_value = self.ISH_VERSION_RESP
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_load_file.side_effect = [{
        'ec_version': self.ACTIVE_VERSION
    }, {
        'ec_version': self.ACTIVE_ISH_VERSION
    }]
    self._mock_exists.side_effect = [False, False, True, True]

    ec_component.ECComponent().Probe()

    called_args = self._mock_runtime_probe_func.call_args.args[1]
    self.assertEqual(
        called_args.get('manifest_path'),
        f'{self.MOUNT_POINT}/usr/share/cme/{self.IMAGE_NAME}'
        '/component_manifest.json')
    self.assertEqual(
        called_args.get('ish_manifest_path'),
        f'{self.MOUNT_POINT}/usr/share/cme/ish/{self.ISH_PROJECT_NAME}'
        '/component_manifest.json')

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_ISH_ISHVersionNotMatch(self, mock_mount):
    self._mock_check_output.return_value = self.ISH_VERSION_RESP
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_load_file.side_effect = [{
        'ec_version': self.ACTIVE_VERSION
    }, {
        'ec_version': 'another-version'
    }]
    self._mock_exists.side_effect = [False, False, True, True]

    with self.assertRaises(ec_component.ECVersionNotMatchError):
      ec_component.ECComponent().Probe()

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_ISH_ISHManifestNotFound(self, mock_mount):
    self._mock_check_output.return_value = self.ISH_VERSION_RESP
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_load_file.side_effect = [{
        'ec_version': self.ACTIVE_VERSION
    }, {
        'ec_version': 'another-version'
    }]
    self._mock_exists.side_effect = [False, False, True, False]

    with self.assertRaises(ec_component.ECManifestNotFoundError):
      ec_component.ECComponent().Probe()

  @mock.patch.object(sys_utils, 'MountPartition', autospec=True)
  def testProbe_EC_ISH_SuccessWithLocalISHManifest(self, mock_mount):
    self._mock_check_output.return_value = self.ISH_VERSION_RESP
    mock_mount.return_value.__enter__.return_value = self.MOUNT_POINT
    self._mock_load_file.side_effect = [{
        'ec_version': self.ACTIVE_VERSION
    }, {
        'ec_version': self.ACTIVE_ISH_VERSION
    }]
    self._mock_exists.side_effect = [False, True, True, True]

    ec_component.ECComponent().Probe()

    called_args = self._mock_runtime_probe_func.call_args.args[1]
    self.assertEqual(
        called_args.get('manifest_path'),
        f'{self.MOUNT_POINT}/usr/share/cme/{self.IMAGE_NAME}'
        '/component_manifest.json')
    self.assertEqual(
        called_args.get('ish_manifest_path'),
        f'/usr/local/factory/cme/ish/{self.ISH_PROJECT_NAME}'
        '/component_manifest.json')


if __name__ == '__main__':
  unittest.main()
