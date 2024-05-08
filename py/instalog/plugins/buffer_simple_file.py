#!/usr/bin/env python3
#
# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple file-based buffer.

A simple buffer plugin which writes its events to a single file on disk, and
separately maintains metadata. See buffer_file_common.py for details.
"""

import os
import shutil

from cros.factory.instalog import plugin_base
from cros.factory.instalog.plugins import buffer_file_common
from cros.factory.utils.arg_utils import Arg
from cros.factory.utils import file_utils


_TEMPORARY_ATTACHMENT_DIR = 'attachments_tmp_dir'
_DEFAULT_TRUNCATE_INTERVAL = 0  # truncating disabled
_DEFAULT_COPY_ATTACHMENTS = False  # use move instead of copy by default
_DEFAULT_ENABLE_FSYNC = True  # fsync when it receives events


class BufferSimpleFile(plugin_base.IBufferPlugin):

  ARGS = [
      Arg('truncate_interval', (int, float),
          'How often truncating the buffer file should be attempted.  '
          'If set to 0, truncating functionality will be disabled (default).',
          default=_DEFAULT_TRUNCATE_INTERVAL),
      Arg('copy_attachments', bool,
          'Instead of moving an attachment into the buffer, perform a copy '
          'operation, and leave the source file intact.',
          default=_DEFAULT_COPY_ATTACHMENTS),
      Arg('enable_fsync', bool,
          'Synchronize the buffer file when it receives events.  '
          'Default is True.',
          default=_DEFAULT_ENABLE_FSYNC)
  ]

  def __init__(self, *args, **kwargs):
    self.buffer_file = None
    self.attachments_tmp_dir = None
    self.non_consumable_event_manager = \
        buffer_file_common.NonConsumableEventsManager()
    super().__init__(*args, **kwargs)

  def SetUp(self):
    """Sets up the plugin."""
    self.buffer_file = buffer_file_common.BufferFile(
        self.args, self.logger.name, self.GetDataDir())

    self.attachments_tmp_dir = os.path.join(self.GetDataDir(),
                                            _TEMPORARY_ATTACHMENT_DIR)
    self.non_consumable_event_manager.SetUp(self.GetDataDir(), self.logger.name)
    # Remove the attachments tmp dir, if Instalog terminated last time.
    if os.path.exists(self.attachments_tmp_dir):
      shutil.rmtree(self.attachments_tmp_dir)
    file_utils.TryMakeDirs(self.attachments_tmp_dir)

  def Main(self):
    """Main thread of the plugin."""
    while not self.IsStopping():
      if not self.args.truncate_interval:
        # Truncating is disabled.  But we should keep the main thread running,
        # or else PluginSandbox will assume the plugin has crashed, and will
        # take the plugin down.
        # TODO(kitching): Consider altering PluginSandbox to allow Main to
        #                 return some particular value which signifies "I am
        #                 exiting of my own free will and I should be allowed to
        #                 continue running normally."
        self.Sleep(100)
        continue

      self.info('Truncating database...')
      # yapf: disable
      self.buffer_file.Truncate()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      self.info('Truncating complete.  Sleeping %d secs...',
                self.args.truncate_interval)
      self.Sleep(self.args.truncate_interval)

  def Produce(self, producer, events, consumable):
    """See IBufferPlugin.Produce."""
    non_consumable_file = \
        self.non_consumable_event_manager.GetNonConsumableFile(producer)
    if not consumable:
      non_consumable_file.StoreEvents(events)
      return True

    with non_consumable_file.MoveFile() as pre_emit_file_path:
      event_iter_factory = buffer_file_common.EventIterFactory(
          self.logger.name, pre_emit_file_path, events,
          self.attachments_tmp_dir, self.args.copy_attachments)
      return self._ProduceConsumableEvents(event_iter_factory)

  def _ProduceConsumableEvents(self, event_iter_factory):
    """Processes attachment files in the events.

    Note the careful edge cases with attachment files.  We want them *all* to
    be either moved or copied into the buffer's database, or *none* at all.
    """
    try:
      # yapf: disable
      self.buffer_file.ProduceEvents(event_iter_factory)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
      return True
    except buffer_file_common.NoAttachmentForCopying:
      return False
    except Exception:
      self.exception('Exception encountered when producing events')
      return False

  def AddConsumer(self, consumer_id):
    """See IBufferPlugin.AddConsumer."""
    # yapf: disable
    self.buffer_file.AddConsumer(consumer_id)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def RemoveConsumer(self, consumer_id):
    """See IBufferPlugin.RemoveConsumer."""
    # yapf: disable
    self.buffer_file.RemoveConsumer(consumer_id)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def ListConsumers(self, details=0):
    """See IBufferPlugin.ListConsumers."""
    del details
    # yapf: disable
    return self.buffer_file.ListConsumers()  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def Consume(self, consumer_id):
    """See IBufferPlugin.Consume."""
    # yapf: disable
    return self.buffer_file.Consume(consumer_id)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable


if __name__ == '__main__':
  plugin_base.main()
