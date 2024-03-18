#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from google.cloud import ndb

from cros.factory.hwid.service.appengine.data import cl_upload_config
from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module


class CLUploadManagerTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._ndb_connector = ndbc_module.NDBConnector()

  def tearDown(self):
    super().tearDown()
    with self._ndb_connector.CreateClientContext():
      ndb.delete_multi(
          cl_upload_config.CLUploadConfig.query().iter(keys_only=True))

  def _SetConfig(self, manager: cl_upload_config.CLUploadManager, **kwargs):
    entity = manager.cl_upload_config
    with self._ndb_connector.CreateClientContext():
      entity.populate(**kwargs)
      entity.put()

  def testDefaultUploadConfig(self):
    manager = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.VERIFICATION_PAYLOAD)

    config = manager.cl_upload_config

    self.assertEqual(config.cl_type,
                     cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self.assertFalse(config.disabled)
    self.assertEqual(config.approval_method,
                     cl_upload_config.ApprovalMethod.MANUAL)
    self.assertCountEqual(config.reviewers, [])
    self.assertIsNone(config.bot_reviewer)
    self.assertCountEqual(config.ccs, [])

  def testUploadConfig(self):
    manager = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    manager2 = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.HWID_SELECTION_PAYLOAD)
    self._SetConfig(
        manager, disabled=True,
        approval_method=cl_upload_config.ApprovalMethod.BOT, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])
    self._SetConfig(manager2, reviewers=['foo@example.com'],
                    ccs=['bar@example.com'])

    config = manager.cl_upload_config

    self.assertEqual(config.cl_type,
                     cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self.assertTrue(config.disabled)
    self.assertEqual(config.approval_method,
                     cl_upload_config.ApprovalMethod.BOT)
    self.assertCountEqual(config.reviewers, ['reviewer@example.com'])
    self.assertEqual(config.bot_reviewer, 'bot-reviewer@example.com')
    self.assertCountEqual(config.ccs, ['cc@example.com'])

  @mock.patch('cros.factory.hwid.service.appengine.git_util.CreateOrPatchCL')
  def testCreateCL_WithBotReviewer(self, mock_create_patch_cl):
    manager = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self._SetConfig(
        manager, disabled=False,
        approval_method=cl_upload_config.ApprovalMethod.BOT, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])
    mock_create_patch_cl.return_value = (123, 456)

    change_id, cl_number = manager.CreateCL(
        False, 'https://chrome-internal.googlesource.com/fake-project',
        'fake-cookie', 'fake-branch', [], 'fake-author', 'fake-committer',
        'fake-commit-msg')

    mock_create_patch_cl.assert_called_once_with(
        'https://chrome-internal.googlesource.com/fake-project', 'fake-cookie',
        'fake-branch', [], 'fake-author', 'fake-committer', 'fake-commit-msg',
        reviewers=['bot-reviewer@example.com'], cc=[
            'reviewer@example.com', 'cc@example.com'
        ], bot_commit=False, commit_queue=False, repo=None, topic=None,
        verified=0, auto_submit=False, rubber_stamper=False, hashtags=None,
        files_to_delete=None)
    self.assertEqual(change_id, 123)
    self.assertEqual(cl_number, 456)

  @mock.patch('cros.factory.hwid.service.appengine.git_util.CreateOrPatchCL')
  def testCreateCL_WithSelfReviewer(self, mock_create_patch_cl):
    manager = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self._SetConfig(
        manager, disabled=False,
        approval_method=cl_upload_config.ApprovalMethod.SELF, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])
    mock_create_patch_cl.return_value = (123, 456)

    change_id, cl_number = manager.CreateCL(
        False, 'https://chrome-internal.googlesource.com/fake-project',
        'fake-cookie', 'fake-branch', [], 'fake-author', 'fake-committer',
        'fake-commit-msg')

    mock_create_patch_cl.assert_called_once_with(
        'https://chrome-internal.googlesource.com/fake-project', 'fake-cookie',
        'fake-branch', [], 'fake-author', 'fake-committer', 'fake-commit-msg',
        reviewers=[], cc=['reviewer@example.com',
                          'cc@example.com'], bot_commit=True, commit_queue=True,
        repo=None, topic=None, verified=0, auto_submit=False,
        rubber_stamper=False, hashtags=None, files_to_delete=None)
    self.assertEqual(change_id, 123)
    self.assertEqual(cl_number, 456)

  @mock.patch('cros.factory.hwid.service.appengine.git_util.CreateOrPatchCL')
  def testCreateCL_WithManualReviewer(self, mock_create_patch_cl):
    manager = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self._SetConfig(
        manager, disabled=False,
        approval_method=cl_upload_config.ApprovalMethod.MANUAL, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])
    mock_create_patch_cl.return_value = (123, 456)

    change_id, cl_number = manager.CreateCL(
        False, 'https://chrome-internal.googlesource.com/fake-project',
        'fake-cookie', 'fake-branch', [], 'fake-author', 'fake-committer',
        'fake-commit-msg')

    mock_create_patch_cl.assert_called_once_with(
        'https://chrome-internal.googlesource.com/fake-project', 'fake-cookie',
        'fake-branch', [], 'fake-author', 'fake-committer',
        'fake-commit-msg', reviewers=['reviewer@example.com'], cc=[
            'cc@example.com'
        ], bot_commit=False, commit_queue=False, repo=None, topic=None,
        verified=0, auto_submit=False, rubber_stamper=False, hashtags=None,
        files_to_delete=None)
    self.assertEqual(change_id, 123)
    self.assertEqual(cl_number, 456)

  @mock.patch('cros.factory.hwid.service.appengine.git_util.CreateOrPatchCL')
  def testCreateCL_WithDisabledConfig_ShouldNotCreateCL(self,
                                                        mock_create_patch_cl):
    manager = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self._SetConfig(
        manager, disabled=True,
        approval_method=cl_upload_config.ApprovalMethod.BOT, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])

    change_id, cl_number = manager.CreateCL(
        False, 'https://chrome-internal.googlesource.com/fake-project',
        'fake-cookie', 'fake-branch', [], 'fake-author', 'fake-committer',
        'fake-commit-msg')

    mock_create_patch_cl.assert_not_called()
    self.assertIsNone(change_id)
    self.assertIsNone(cl_number)

  @mock.patch('cros.factory.hwid.service.appengine.git_util.CreateOrPatchCL')
  def testCreateCL_WithDryRun_ShouldNotCreateCL(self, mock_create_patch_cl):
    manager = cl_upload_config.CLUploadManager(
        self._ndb_connector, cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self._SetConfig(
        manager, disabled=False,
        approval_method=cl_upload_config.ApprovalMethod.BOT, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])

    change_id, cl_number = manager.CreateCL(
        True, 'https://chrome-internal.googlesource.com/fake-project',
        'fake-cookie', 'fake-branch', [], 'fake-author', 'fake-committer',
        'fake-commit-msg')

    mock_create_patch_cl.assert_not_called()
    self.assertIsNone(change_id)
    self.assertIsNone(cl_number)


if __name__ == '__main__':
  unittest.main()
