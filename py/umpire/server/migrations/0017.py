# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os

# Private constants.
_FASTBOOT_DIR = '/var/db/factory/umpire/fastboot_img_src'


def Migrate():
  if not os.path.exists(_FASTBOOT_DIR):
    os.mkdir(_FASTBOOT_DIR)
