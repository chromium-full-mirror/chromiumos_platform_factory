# Copyright 2026 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import contextlib
import os
import threading
from typing import Generator, Mapping
import uuid


class _ReportIndex(threading.local):

  def __init__(self):
    self.value = 1  # the report index starts from 1


_SERVER_PROCESS_ID = str(uuid.uuid4())


# TODO: b/518652632 - Discuss how we should catch missing logs with report
#   indexes, and further discuss our main purposes and if these codes are
#   worthful.
class ReportIndexManager():

  def __init__(self):
    self._report_index = _ReportIndex()

  @contextlib.contextmanager
  def AllocateNextIndex(self) -> Generator[Mapping[str, str], None, None]:
    """Thread-safe report index allocation.

    This is designed for the umpire gRPC service.

    Allocates a unique server ID and index. If the yielded task completes
    normally, the index increments; otherwise unchanged.

    Follow the design of the main umpire XML RPC service report index
    allocation, but without using a lock. The server UUID in this design is a
    unique UUID concatenating a worker thread ID; thus not really of the UUID
    format.

    Returns:
      A server UUID and report index entry for saving into the factory report.
    """

    thread_id = threading.get_ident()
    server_uuid = f'{_SERVER_PROCESS_ID}#{thread_id}'
    next_report_index = self._report_index.value
    yield {
        'type': 'metadata',
        'serverUuid': server_uuid,
        'reportIndex': f'{next_report_index:010d}',
        'domeVersion': os.environ.get('DOCKER_IMAGE_TIMESTAMP', '')
    }
    self._report_index.value += 1
