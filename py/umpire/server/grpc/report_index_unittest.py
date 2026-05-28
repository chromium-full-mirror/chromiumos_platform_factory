#!/usr/bin/env python3
#
# Copyright 2026 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
from concurrent import futures
from typing import List
import unittest

from cros.factory.umpire.server.grpc import report_index


class ReportIndexManagerTest(unittest.TestCase):

  def setUp(self):
    self._report_index_manager = report_index.ReportIndexManager()

  def testAllocateNextIndexEntrySchema(self):
    with self._report_index_manager.AllocateNextIndex() as e:
      self.assertListEqual(
          sorted(list(e.keys())),
          sorted(['type', 'serverUuid', 'reportIndex', 'domeVersion']))
      self.assertEqual(e['type'], 'metadata')
      self.assertEqual(len(e['serverUuid'].split('#')), 2)
      self.assertEqual(e['reportIndex'], '0000000001')

  def testAllocateNextIndexThrowException(self):
    with self._report_index_manager.AllocateNextIndex() as e:
      self.assertEqual(int(e['reportIndex']), 1)

    with self.assertRaises(ValueError):
      with self._report_index_manager.AllocateNextIndex() as e:
        raise ValueError()

    with self._report_index_manager.AllocateNextIndex() as e:
      self.assertEqual(int(e['reportIndex']), 2)

  def testAllocateNextIndexMultiThreads(self):

    def f():
      with self._report_index_manager.AllocateNextIndex() as e:
        return e

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
      results = list(executor.map(lambda _: f(), range(1000)))

      d = collections.defaultdict(list)
      for r in results:
        d[r['serverUuid']].append(int(r['reportIndex']))

      # Check that all server process IDs are the same
      server_uuids: List[str] = list(d.keys())
      server_process_ids = set(s.split('#')[0] for s in server_uuids)
      self.assertEqual(len(server_process_ids), 1)

      for indexes in d.values():
        indexes.sort()
        expected_indexes = list(range(1, len(indexes) + 1))
        self.assertListEqual(indexes, expected_indexes)

  def testAllocateNextIndexMultiThreadsThrowExceptions(self):

    def f(n: int):
      try:
        with self._report_index_manager.AllocateNextIndex() as e:
          if n % 2 == 0:
            raise ValueError()
          return e
      except ValueError:
        return None

    inputs = list(range(1000))
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
      results = list(executor.map(f, inputs))
      results = [e for e in results if e is not None]
      self.assertEqual(500, len(results))

      d = collections.defaultdict(list)
      for r in results:
        d[r['serverUuid']].append(int(r['reportIndex']))

      for indexes in d.values():
        indexes.sort()
        expected_indexes = list(range(1, len(indexes) + 1))
        self.assertListEqual(indexes, expected_indexes)


if __name__ == '__main__':
  unittest.main()
