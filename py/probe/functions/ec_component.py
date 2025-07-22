# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import os
import re
import subprocess
from typing import Optional

from cros.factory.device import device_utils
from cros.factory.gooftool import common as gooftool_common
from cros.factory.probe import function
from cros.factory.probe.lib import probe_function
from cros.factory.probe.runtime_probe import runtime_probe_adapter
from cros.factory.utils import arg_utils
from cros.factory.utils import json_utils
from cros.factory.utils import process_utils
from cros.factory.utils import sys_utils

from cros.factory.external.chromeos_cli import cros_config as cros_config_module


LOCAL_CME_PATH = '/usr/local/factory/cme/'
LOCAL_CME_ISH_PATH = '/usr/local/factory/cme/ish/'
RELEASE_CME_PATH = 'usr/share/cme/'
RELEASE_CME_ISH_PATH = 'usr/share/cme/ish/'
MANIFEST_NAME = 'component_manifest.json'

FIRMWARE_COPY_RE = re.compile(r'^Firmware copy:\s*(\S+)\s*$', re.MULTILINE)
RO_VERSION_RE = re.compile(r'^RO version:\s*(\S+)\s*$', re.MULTILINE)
RW_VERSION_RE = re.compile(r'^RW version:\s*(\S+)\s*$', re.MULTILINE)
ISH_PROJECT_RE = re.compile(r'([^-]+(?:-ish)?)-.*')


class ECVersionNotMatchError(function.FunctionException):
  pass


class ECManifestNotFoundError(function.FunctionException):
  pass


def _CheckManifestVersion(manifest_path: str,
                          active_version: Optional[str] = None):
  if active_version is None:
    active_version = device_utils.CreateDUTInterface().ec.GetActiveVersion()
  if not os.path.exists(manifest_path):
    raise ECManifestNotFoundError(f'{manifest_path} not exist.')
  manifest = json_utils.LoadFile(manifest_path)
  manifest_version = manifest.get('ec_version')
  if active_version != manifest_version:
    raise ECVersionNotMatchError(f'Active EC version {active_version!r} '
                                 'doesn\'t match manifest version: '
                                 f'{manifest_version!r} for manifest: '
                                 f'{manifest_path!r}.')


def _GetISHVersion() -> Optional[str]:
  try:
    version_info = process_utils.CheckOutput(
        ['ectool', '--name=cros_ish', 'version'], log=True, encoding='utf-8')
    firmware_copy_match = FIRMWARE_COPY_RE.search(version_info)
    if not firmware_copy_match:
      return None

    firmware_copy = firmware_copy_match.group(1)
    if firmware_copy == 'RO':
      ish_vesrion_match = RO_VERSION_RE.search(version_info)
    else:
      ish_vesrion_match = RW_VERSION_RE.search(version_info)

    if ish_vesrion_match:
      return ish_vesrion_match.group(1)
  except subprocess.CalledProcessError:
    return None

  return None


def _GetISHProject(ish_version: Optional[str]) -> Optional[str]:
  if ish_version is None:
    return None

  ish_project_match = ISH_PROJECT_RE.fullmatch(ish_version)
  if not ish_project_match:
    return None

  return ish_project_match.group(1)


def _GetManifestPath(release_image_root: str, local_cme_path: str,
                     release_cme_path: str, cme_project_name: str) -> str:
  manifest_path = os.path.join(local_cme_path, cme_project_name, MANIFEST_NAME)
  if os.path.exists(manifest_path):
    logging.info('Loading local component manifest: %s', manifest_path)
  else:
    manifest_path = os.path.join(release_image_root, release_cme_path,
                                 cme_project_name, MANIFEST_NAME)
  return manifest_path


_NUM_RETRY = 5


def _ProbeECComponent(args: dict, ec_manifest_path: str,
                      ish_manifest_path: Optional[str],
                      ish_version: Optional[str]):
  _CheckManifestVersion(ec_manifest_path)
  args['manifest_path'] = ec_manifest_path
  if ish_manifest_path:
    _CheckManifestVersion(ish_manifest_path, ish_version)
    args['ish_manifest_path'] = ish_manifest_path

  best_probed_result: list = []
  # Retry the probe multiple times to avoid flakiness.
  for i in range(_NUM_RETRY):
    probed_result: list = runtime_probe_adapter.RunProbeFunction(
        'ec_component', args)
    logging.info('Retry #%d, probed %d components: %r', i + 1,
                 len(probed_result), probed_result)
    best_probed_result = max(best_probed_result, probed_result, key=len)
  return best_probed_result


class ECComponent(probe_function.AbstractProbeFunction):
  """Probe EC Component.

  Probe EC components recorded in the EC component manifest, and ISH components
  recorded in the ISH component manifest. By default, this probe function will
  load the EC manifest from
  `/usr/share/cme/{image_name}/component_manifest.json`, and the ISH manifest
  from `/usr/share/cme/ish/{ish_project_name}/component_manifest.json` in the
  release image partition, where `image_name` can be obtained from
  `cros_config /firmware image-name`, and `ish_project_name` can be obtained
  from `ectool --name=cros_ish version`.

  If you are probing EC/ISH component with a local build EC firmware that the
  release component manifest doesn't match the active EC firmware, you can
  override the manifest by setting
  `/usr/local/factory/cme/{image_name}/component_manifest.json` for EC, or
  `/usr/local/factory/cme/ish/{ish_project_name}/component_manifest.json` for
  ISH. The probe function will load the override manifests if these paths exist.
  """
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
    ish_version = _GetISHVersion()
    ish_project = _GetISHProject(ish_version)

    release_rootfs = gooftool_common.Util().GetReleaseRootPartitionPath()
    with sys_utils.MountPartition(release_rootfs) as root:
      ec_manifest_path = _GetManifestPath(root, LOCAL_CME_PATH,
                                          RELEASE_CME_PATH, image_name)
      ish_manifest_path = None
      if ish_project is not None:
        ish_manifest_path = _GetManifestPath(root, LOCAL_CME_ISH_PATH,
                                             RELEASE_CME_ISH_PATH, ish_project)
      return _ProbeECComponent(self.args.ToDict(), ec_manifest_path,
                               ish_manifest_path, ish_version)
