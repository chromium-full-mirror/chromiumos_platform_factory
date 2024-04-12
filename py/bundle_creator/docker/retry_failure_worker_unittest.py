# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import datetime
from time import sleep
from typing import Dict
import unittest
from unittest import mock

from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from google.cloud import firestore
import pytz


# isort: split

from cros.factory.bundle_creator.connector import firestore_connector
from cros.factory.bundle_creator.connector import pubsub_connector
from cros.factory.bundle_creator.docker import config
from cros.factory.bundle_creator.docker import retry_failure_worker
from cros.factory.bundle_creator.proto import factorybundle_v2_pb2  # pylint: disable=no-name-in-module


RetryFailureException = retry_failure_worker.RetryFailureException
UserRequest = retry_failure_worker.UserRequest
RetryFailureTask = retry_failure_worker.RetryFailureTask


class UserRequestTest(unittest.TestCase):

  def setUp(self):
    self._requester = 'requester@google.com'
    self._snapshot = {
        'email': 'foo@bar',
        'cc_emails': ['foo2@bar'],
        'board': 'board',
        'project': 'project',
        'phase': 'phase',
        'toolkit_version': '11111.0.0',
        'test_image_version': '22222.0.0',
        'release_image_version': '33333.0.0',
        'update_hwid_db_firmware_info': False,
    }

  def testToCreateBundleRequest_succeed_returnsExpectedValue(self):
    request = UserRequest(self._snapshot).ToCreateBundleRequest(self._requester)

    expected_request = factorybundle_v2_pb2.CreateBundleRequest()
    expected_request.email = self._snapshot['email']
    expected_request.cc_emails.extend(self._snapshot['cc_emails'])
    expected_request.cc_emails.append(config.RETRY_FAILURE_EMAIL)
    expected_request.cc_emails.append(self._requester)
    bundle_metadata = expected_request.bundle_metadata
    bundle_metadata.board = self._snapshot['board']
    bundle_metadata.project = self._snapshot['project']
    bundle_metadata.phase = self._snapshot['phase']
    bundle_metadata.toolkit_version = self._snapshot['toolkit_version']
    bundle_metadata.test_image_version = self._snapshot['test_image_version']
    bundle_metadata.release_image_version = self._snapshot[
        'release_image_version']
    expected_request.hwid_option.update_db_firmware_info = False
    self.assertEqual(request, expected_request)

  def testToCreateBundleRequest_duplicatedCcEmails_verifiesCcEmails(self):
    request = UserRequest(self._snapshot).ToCreateBundleRequest('foo2@bar')

    self.assertEqual(request.cc_emails,
                     ['foo2@bar', config.RETRY_FAILURE_EMAIL])

  def testToCreateBundleRequest_duplicatedEmail_verifiesCcEmails(self):
    request = UserRequest(self._snapshot).ToCreateBundleRequest('foo@bar')

    self.assertEqual(request.cc_emails,
                     ['foo2@bar', config.RETRY_FAILURE_EMAIL])

  def testToCreateBundleRequest_withOptionalFields_verifiesOptionalFields(self):
    self._snapshot['firmware_source'] = '44444.0.0'
    self._snapshot['update_hwid_db_firmware_info'] = True
    self._snapshot['hwid_related_bug_number'] = 123456789

    request = UserRequest(self._snapshot).ToCreateBundleRequest(self._requester)

    self.assertEqual(request.bundle_metadata.firmware_source, '44444.0.0')
    self.assertEqual(request.hwid_option.update_db_firmware_info, True)
    self.assertEqual(request.hwid_option.related_bug_number, 123456789)


class RetryFailureTaskTest(unittest.TestCase):

  def testFromPubSubMessage_succeed_returnsExpectedValue(self):
    within_days = 10
    requester = 'foo@bar'

    task = RetryFailureTask.FromPubSubMessage(
        pubsub_connector.PubSubMessage(
            data=f'{within_days},{requester}'.encode(), attributes={}))

    self.assertEqual(
        task, RetryFailureTask(within_days=within_days, requester=requester))

  def testFromPubSubMessage_wrongFormatMessage_raisesWrappedException(self):
    data = 'wrong_format_message'.encode()
    with self.assertRaisesRegex(RetryFailureException,
                                f'Receive invalid message: {data!r}'):
      RetryFailureTask.FromPubSubMessage(
          pubsub_connector.PubSubMessage(data=data, attributes={}))


class RetryFailureWorkerTest(unittest.TestCase):

  _RETRY_PUBSUB_TOPIC = 'fake-retry-topic'
  _CREATE_BUNDLE_REQUEST_TOPIC = 'fake-topic'
  _CREATE_BUNDLE_REQUEST_SUBSCRIPTION = 'fake-sub'

  @classmethod
  def setUpClass(cls):
    cls._firestore_connector = firestore_connector.FirestoreConnector(
        config.GCLOUD_PROJECT)
    cls._pubsub_connector = pubsub_connector.PubSubConnector(
        config.GCLOUD_PROJECT)
    cls._pubsub_connector.CreateTopic(cls._RETRY_PUBSUB_TOPIC)
    cls._pubsub_connector.CreateTopic(cls._CREATE_BUNDLE_REQUEST_TOPIC)

  @classmethod
  def tearDownClass(cls):
    cls._pubsub_connector.DeleteTopic(cls._RETRY_PUBSUB_TOPIC)
    cls._pubsub_connector.DeleteTopic(cls._CREATE_BUNDLE_REQUEST_TOPIC)

  def setUp(self):
    self._datetime_now = datetime.datetime(2023, 4, 11, 0, 0)
    mock_datetime_patcher = mock.patch(
        'cros.factory.bundle_creator.connector.firestore_connector.datetime')
    mock_datetime_patcher.start().now.return_value = self._datetime_now
    self.addCleanup(mock_datetime_patcher.stop)

    self._firestore_connector.ClearCollection('user_requests')
    client = firestore.Client(project=config.GCLOUD_PROJECT)
    self._user_requests_col = client.collection('user_requests')

    self._pubsub_connector.CreateSubscription(self._RETRY_PUBSUB_TOPIC,
                                              config.RETRY_PUBSUB_SUBSCRIPTION)
    self._pubsub_connector.CreateSubscription(
        self._CREATE_BUNDLE_REQUEST_TOPIC,
        self._CREATE_BUNDLE_REQUEST_SUBSCRIPTION)

    self._worker = retry_failure_worker.RetryFailureWorker()
    self._within_days = 10
    self._requester = 'fake-caller@google.com'

    self.setUpExpectedValues()

  def tearDown(self):
    self._pubsub_connector.DeleteSubscription(config.RETRY_PUBSUB_SUBSCRIPTION)
    self._pubsub_connector.DeleteSubscription(
        self._CREATE_BUNDLE_REQUEST_SUBSCRIPTION)

  def setUpExpectedValues(self):
    self._expected_request = factorybundle_v2_pb2.CreateBundleRequest()
    self._expected_request.email = 'foo@bar'
    self._expected_request.cc_emails.extend(
        [config.RETRY_FAILURE_EMAIL, self._requester])
    bundle_metadata = self._expected_request.bundle_metadata
    bundle_metadata.board = 'board'
    bundle_metadata.project = 'project'
    bundle_metadata.phase = 'proto'
    bundle_metadata.toolkit_version = '11111.0.0'
    bundle_metadata.test_image_version = '22222.0.0'
    bundle_metadata.release_image_version = '33333.0.0'
    self._expected_request.hwid_option.update_db_firmware_info = False
    self._expected_snapshot = {
        'email':
            'foo@bar',
        'cc_emails': [config.RETRY_FAILURE_EMAIL, self._requester],
        'board':
            'board',
        'project':
            'project',
        'phase':
            'proto',
        'toolkit_version':
            '11111.0.0',
        'test_image_version':
            '22222.0.0',
        'release_image_version':
            '33333.0.0',
        'update_hwid_db_firmware_info':
            False,
        'status':
            firestore_connector.UserRequestStatus.NOT_STARTED.name,
        'request_time':
            DatetimeWithNanoseconds(2023, 4, 11, 0, 0, tzinfo=pytz.UTC),
        'request_from':
            'v2',
    }

  def testTryProcessRequest_succeed_verifiesNewlyCreatedRequests(self):
    self._user_requests_col.document('doc_failed').set(
        self._CreateUserRequest({
            'status': firestore_connector.UserRequestStatus.FAILED.name,
            'request_time': self._datetime_now - datetime.timedelta(days=3),
        }))
    self._PublishRetryFailureMessage()

    self._worker.TryProcessRequest()
    sleep(1)  # Ensure the messages are published.

    pubsub_message = self._pubsub_connector.PullFirstMessage(
        self._CREATE_BUNDLE_REQUEST_SUBSCRIPTION)
    create_bundle_message = (
        factorybundle_v2_pb2.CreateBundleMessage.FromString(
            pubsub_message.data))
    snapshot = self._firestore_connector.GetUserRequestDocument(
        create_bundle_message.doc_id)
    self.assertEqual(pubsub_message.attributes, {})
    self.assertEqual(create_bundle_message.request, self._expected_request)
    # Verify the existence of `id` field in `snapshot`, but exclude its value
    # from further comparison since it is dynamically generated by the emulator.
    self.assertIn('id', snapshot)
    del snapshot['id']
    self.assertEqual(snapshot, self._expected_snapshot)

  def testTryProcessRequest_failureRequestedFromThisWorker_verifiesNoMessages(
      self):
    self._user_requests_col.document('doc_should_not_be_retried_agian').set(
        self._CreateUserRequest({
            'status': firestore_connector.UserRequestStatus.FAILED.name,
            'email': config.RETRY_FAILURE_EMAIL,
            'request_time': self._datetime_now - datetime.timedelta(days=1),
        }))
    self._user_requests_col.document('doc_should_not_be_retried_agian_2').set(
        self._CreateUserRequest({
            'status': firestore_connector.UserRequestStatus.FAILED.name,
            'email': 'foo@bar',
            'request_time': self._datetime_now - datetime.timedelta(days=1),
            'cc_emails': [config.RETRY_FAILURE_EMAIL],
        }))
    self._PublishRetryFailureMessage()

    self._worker.TryProcessRequest()
    sleep(1)  # Ensure the message is published if there is any.

    self.assertIsNone(
        self._pubsub_connector.PullFirstMessage(
            self._CREATE_BUNDLE_REQUEST_SUBSCRIPTION))

  def testTryProcessRequest_requestStatusIsNotFailed_verifiesNoMessages(self):
    self._user_requests_col.document('doc_succeeded').set(
        self._CreateUserRequest({
            'status': firestore_connector.UserRequestStatus.SUCCEEDED.name,
            'request_time': self._datetime_now - datetime.timedelta(days=5),
        }))
    self._PublishRetryFailureMessage()

    self._worker.TryProcessRequest()
    sleep(1)  # Ensure the message is published if there is any.

    self.assertIsNone(
        self._pubsub_connector.PullFirstMessage(
            self._CREATE_BUNDLE_REQUEST_SUBSCRIPTION))

  def testTryProcessRequest_failedRequestIsNotInWithinDays_verifiesNoMessages(
      self):
    self._user_requests_col.document('doc_failed_but_not_within_days').set(
        self._CreateUserRequest({
            'status': firestore_connector.UserRequestStatus.FAILED.name,
            'request_time': self._datetime_now - datetime.timedelta(days=11),
        }))
    self._PublishRetryFailureMessage()

    self._worker.TryProcessRequest()
    sleep(1)  # Ensure the message is published if there is any.

    self.assertIsNone(
        self._pubsub_connector.PullFirstMessage(
            self._CREATE_BUNDLE_REQUEST_SUBSCRIPTION))

  def _PublishRetryFailureMessage(self):
    self._pubsub_connector.PublishMessage(
        self._RETRY_PUBSUB_TOPIC,
        f'{self._within_days},{self._requester}'.encode())
    sleep(1)  # Ensure the message is published.

  def _CreateUserRequest(self, required_data: Dict):
    base_doc = {
        'email': 'foo@bar',
        'board': 'board',
        'project': 'project',
        'phase': 'proto',
        'toolkit_version': '11111.0.0',
        'test_image_version': '22222.0.0',
        'release_image_version': '33333.0.0',
        'update_hwid_db_firmware_info': False,
    }
    base_doc.update(required_data)
    return base_doc


if __name__ == '__main__':
  unittest.main()
