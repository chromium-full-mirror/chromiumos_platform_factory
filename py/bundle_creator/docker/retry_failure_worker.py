# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from dataclasses import dataclass
from typing import Dict


# isort: split

from cros.factory.bundle_creator.connector import firestore_connector
from cros.factory.bundle_creator.connector import pubsub_connector
from cros.factory.bundle_creator.docker import config
from cros.factory.bundle_creator.docker import worker
from cros.factory.bundle_creator.proto import factorybundle_v2_pb2  # pylint: disable=no-name-in-module


class RetryFailureException(Exception):
  """An Exception raised when fail to retry failure requests."""


@dataclass
class UserRequest:
  """A placeholder stores a user request snapshot.

  This is mainly used to convert a user request snapshot to a new create bundle
  request.

  Properties:
    snapshot: A dictionary which represents a user request.
  """
  snapshot: Dict

  def ToCreateBundleRequest(
      self, requester: str) -> factorybundle_v2_pb2.CreateBundleRequest:
    """Converts to v2 create bundle request.

    Args:
      requester: The retry failure requester's email to be added into the carbon
          copy list.

    Returns:
      A `factorybundle_v2_pb2.CreateBundleRequest` proto message.
    """
    request = factorybundle_v2_pb2.CreateBundleRequest()
    request.email = self.snapshot.get('email')

    request.cc_emails.extend(self.snapshot.get('cc_emails', []))
    request.cc_emails.append(config.RETRY_FAILURE_EMAIL)
    if requester not in request.cc_emails and requester != request.email:
      request.cc_emails.append(requester)

    metadata = request.bundle_metadata
    metadata.board = self.snapshot.get('board')
    metadata.project = self.snapshot.get('project')
    metadata.phase = self.snapshot.get('phase')
    metadata.toolkit_version = self.snapshot.get('toolkit_version')
    metadata.test_image_version = self.snapshot.get('test_image_version')
    metadata.release_image_version = self.snapshot.get('release_image_version')
    firmware_source = self.snapshot.get('firmware_source', '')
    if firmware_source:
      metadata.firmware_source = firmware_source
    metadata.no_firmware = self.snapshot.get('no_firmware', False)

    hwid_option = request.hwid_option
    hwid_option.update_db_firmware_info = self.snapshot.get(
        'update_hwid_db_firmware_info', False)
    if hwid_option.update_db_firmware_info:
      hwid_option.related_bug_number = self.snapshot.get(
          'hwid_related_bug_number')
    return request


@dataclass
class RetryFailureTask(worker.IWorkerTask):
  within_days: int
  requester: str

  @classmethod
  def FromPubSubMessage(cls, pubsub_message: pubsub_connector.PubSubMessage):
    try:
      within_days_str, requester = pubsub_message.data.decode().split(',')
    except ValueError as e:
      raise RetryFailureException(
          f'Receive invalid message: {pubsub_message.data!r}') from e
    return cls(within_days=int(within_days_str), requester=requester)

  def ToOriginalRequest(self):
    pass


class RetryFailureWorker(worker.AbstractWorker):

  WORKER_TASK = RetryFailureTask
  SUBSCRIPTION_ID = config.RETRY_PUBSUB_SUBSCRIPTION

  def __init__(self):
    super().__init__()
    self._firestore_connector = firestore_connector.FirestoreConnector(
        config.GCLOUD_PROJECT)
    self._pubsub_connector = pubsub_connector.PubSubConnector(
        config.GCLOUD_PROJECT)

  def TryProcessRequest(self):
    try:
      task = self._PullTask()
      if task:
        self._logger.info(task)
        for snapshot in reversed(
            self._firestore_connector.GetLatestUserRequestsByStatus(
                firestore_connector.UserRequestStatus.FAILED,
                task.within_days)):
          # The first statement is for backward compatibility.
          if (snapshot.get('email') == config.RETRY_FAILURE_EMAIL or
              config.RETRY_FAILURE_EMAIL in snapshot.get('cc_emails', [])):
            continue
          self._ProcessSnapshot(snapshot, task.requester)
    except RetryFailureException as e:
      self._logger.error(e)

  def _ProcessSnapshot(self, snapshot: Dict, requester: str):
    request = UserRequest(snapshot).ToCreateBundleRequest(requester)
    message = factorybundle_v2_pb2.CreateBundleMessage()
    message.doc_id = self._firestore_connector.CreateUserRequest(
        firestore_connector.CreateBundleRequestInfo.FromCreateBundleRequest(
            request), 'v2')
    message.request.MergeFrom(request)
    self._pubsub_connector.PublishMessage(config.PUBSUB_TOPIC,
                                          message.SerializeToString())

    self._logger.info('Processed the failed request:\n%s', str(request))
