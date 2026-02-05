# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Export a specific resource from a bundle

It reads active config, download the specific resource of a bundle,
and install it at the specified file_path.

See PayloadExporter comments for usage.
"""

import os
import textwrap

from cros.factory.umpire import common
from cros.factory.umpire.server import config as umpire_config
from cros.factory.utils import file_utils
from cros.factory.utils import process_utils


class FastbootImagePayloadExporter:

  def __init__(self, env):
    """Constructor.

    Args:
      env: UmpireEnv object.
    """
    self._env = env

  def Export(self, bundle_id):
    """Export raw image partition files to fastboot_img_src

    Args:
      bundle_id: The ID of the bundle.
    """
    config = umpire_config.UmpireConfig(self._env.config)
    bundle = config.GetBundle(bundle_id)

    if not bundle:
      raise common.UmpireError(f'bundle {bundle_id!r} does not exist')

    img_src_dir = self._env.fastboot_img_dir

    # remove old resources
    for item in os.listdir(img_src_dir):
      full_path = os.path.join(img_src_dir, item)
      file_utils.TryUnlink(full_path)

    # Touch android-info.txt for `flashall`
    file_utils.WriteFile(os.path.join(img_src_dir, 'android-info.txt'), '')

    # Add fastboot-info.txt for `flashall`
    # TODO(pohengchen) Allowing user to upload fastboot images zip, which
    # include separated partition images and fastboot-info.txt, instead of
    # hardcoding the partitions needed to be flashed.
    file_utils.WriteFile(
        os.path.join(img_src_dir, 'fastboot-info.txt'),
        textwrap.dedent('''\
        # fastboot-info
        version 1
        flash boot
        flash init_boot
        flash pvmfw
        flash vendor_boot
        flash --apply-vbmeta vbmeta
        flash super
        erase metadata
        erase userdata
        '''))

    files = self._env.GetFastbootImagePayloads(bundle['payloads'])
    for base_name, res_name in files:
      file_path = os.path.join(self._env.resources_dir, res_name)
      dest_file_name = base_name + '.gz'  # The file is actually in gz format.
      file_utils.AtomicCopy(file_path, os.path.join(img_src_dir,
                                                    dest_file_name))
      process_utils.Spawn(['pigz', '-d', '-qn', dest_file_name],
                          check_call=True, log=True, cwd=img_src_dir)
