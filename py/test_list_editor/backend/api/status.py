# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from flask import Blueprint  # type: ignore #TODO(b/338318729) Fixit!


bp = Blueprint('status', __name__)


@bp.route('/status')
def HealthCheck():
  return {
      'status': 'ok'
  }
