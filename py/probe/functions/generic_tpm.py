# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

from cros.factory.probe.lib import cached_probe_function
from cros.factory.utils import process_utils


class GenericTPMFunction(cached_probe_function.CachedProbeFunction):
  """Probe the generic TPM information."""

  def GetCategoryFromArgs(self):
    return None

  @classmethod
  def _ProbeLegacyTPM(cls):
    tpm_data = [line.split(':') for line in
                process_utils.CheckOutput('tpm_version').splitlines()]
    tpm_dict = {key.strip(): value.strip() for key, value in tpm_data}
    mfg = tpm_dict.get('Manufacturer Info', None)
    version = tpm_dict.get('Chip Version', None)
    if mfg is not None and version is not None:
      return [{'manufacturer_info': mfg, 'version': version}]
    return None

  @classmethod
  def ProbeAllDevices(cls):

    gsc_fwver = process_utils.CheckOutput(['gsctool', '-a', '-f'])
    match = re.search(r'device: (?P<device_type>\w+)', gsc_fwver)
    if not match:
      return None
    gsc_device = match.group('device_type')

    if gsc_device in ('H1', 'DT'):
      return cls._ProbeLegacyTPM()

    tpm_data = [
        line.split(':') for line in process_utils.CheckOutput(
            ['tpm_manager_client', 'get_version_info']).strip().splitlines()
    ]
    tpm_dict = {
        key.strip(): value.strip().split(maxsplit=1)[0]
        for key, value in tpm_data[1:-1]
    }
    mfg = tpm_dict.get('manufacturer')
    spec_level = tpm_dict.get('spec_level')
    vendor_specific = tpm_dict.get('vendor_specific')

    if mfg is None or spec_level is None or vendor_specific is None:
      return None
    return [{
        'manufacturer': hex(int(mfg)),
        'spec_level': spec_level,
        'vendor_specific': bytes.fromhex(vendor_specific).decode(),
        'gsc_device': gsc_device
    }]
