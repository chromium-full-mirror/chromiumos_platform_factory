# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import os

from cros.factory.device import device_utils
from cros.factory.gooftool import common as gooftool_common
from cros.factory.probe.lib import probe_function
from cros.factory.probe.runtime_probe import runtime_probe_adapter
from cros.factory.utils import arg_utils
from cros.factory.utils import json_utils
from cros.factory.utils import sys_utils

from cros.factory.external.chromeos_cli import cros_config as cros_config_module


LOCAL_CME_PATH = '/usr/local/factory/cme/'
RELEASE_CME_PATH = 'usr/share/cme/'
MANIFEST_NAME = 'component_manifest.json'


class ECVersionNotMatchError(Exception):
  pass


def _CheckManifestVersion(manifest_path: str):
  active_version = device_utils.CreateDUTInterface().ec.GetActiveVersion()
  manifest = json_utils.LoadFile(manifest_path)
  manifest_version = manifest.get('ec_version')
  if active_version != manifest_version:
    raise ECVersionNotMatchError(f'Active EC version {active_version!r} '
                                 'doesn\'t match manifest version: '
                                 f'{manifest_version!r}.')


def _ProbeECComponent(args: dict, manifest_path: str):
  _CheckManifestVersion(manifest_path)
  args['manifest_path'] = manifest_path
  return runtime_probe_adapter.RunProbeFunction('ec_component', args)


class ECComponent(probe_function.AbstractProbeFunction):
  FUNCTION_NAME = 'ec_component'
  ARGS = [
      arg_utils.Arg('type', str, 'EC component type to be probed',
                    default=None),
      arg_utils.Arg('name', str, 'EC component name to be probed',
                    default=None),
  ]

  def Probe(self):
    cros_config = cros_config_module.CrosConfig()
    image_name = cros_config.GetFirmwareImageName()

    manifest_path = os.path.join(LOCAL_CME_PATH, image_name, MANIFEST_NAME)
    if os.path.exists(manifest_path):
      logging.info('Loading local component manifest: %s', manifest_path)
      return _ProbeECComponent(self.args.ToDict(), manifest_path)

    release_rootfs = gooftool_common.Util().GetReleaseRootPartitionPath()
    with sys_utils.MountPartition(release_rootfs) as root:
      manifest_path = os.path.join(root, RELEASE_CME_PATH, image_name,
                                   MANIFEST_NAME)
      return _ProbeECComponent(self.args.ToDict(), manifest_path)
