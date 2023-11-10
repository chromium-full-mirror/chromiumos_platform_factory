# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Provides an interface to access / use Google Cloud NDB."""

import functools

from google.cloud import ndb


class NDBConnector:

  @functools.cached_property
  def _ndb_client(self):
    return ndb.Client()

  @functools.cached_property
  def _global_cache(self):
    return ndb.RedisCache.from_environment()

  def CreateClientContextWithGlobalCache(self):
    return self._ndb_client.context(global_cache=self._global_cache)

  def CreateClientContext(self):
    return self._ndb_client.context()
