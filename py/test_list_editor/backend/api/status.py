# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# yapf: disable
from flask import Blueprint  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

# yapf: enable


bp = Blueprint('status', __name__)


@bp.route('/status')
def HealthCheck():
  return {
      'status': 'ok'
  }
