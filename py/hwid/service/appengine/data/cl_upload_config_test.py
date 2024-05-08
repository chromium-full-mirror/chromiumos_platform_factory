#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from google.cloud import ndb

from cros.factory.hwid.service.appengine.data import cl_upload_config
from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module


class CLUploadManagerTestCase(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._ndb_connector = ndbc_module.NDBConnector()

  def tearDown(self):
    super().tearDown()
    with self._ndb_connector.CreateClientContext():
      ndb.delete_multi(
          cl_upload_config.CLUploadConfig.query().iter(keys_only=True))
      ndb.delete_multi(
          cl_upload_config.CLUploadFactor.query().iter(keys_only=True))
      ndb.delete_multi(
          cl_upload_config.LatestHWIDMainCommit.query().iter(keys_only=True))

  def _SetConfig(self, manager: cl_upload_config.VPGTargetsCLUploadManager,
                 **kwargs):
    entity = manager.cl_upload_config
    with self._ndb_connector.CreateClientContext():
      entity.populate(**kwargs)
      entity.put()

  def _SetCLUploadFactor(self,
                         manager: cl_upload_config.VPGTargetsCLUploadManager,
                         **kwargs) -> cl_upload_config.CLUploadFactor:
    cl_type = manager.cl_type
    with self._ndb_connector.CreateClientContext():
      entity = cl_upload_config.CLUploadFactor(cl_type=cl_type, **kwargs)
      entity.put()

    return entity

  def _SetLatestHWIDMainCommit(
      self,
      manager: cl_upload_config.PayloadCLUploadManager,
      commit: str,
  ) -> cl_upload_config.LatestHWIDMainCommit:
    cl_type = manager.cl_type
    with self._ndb_connector.CreateClientContext():
      entity = cl_upload_config.LatestHWIDMainCommit(payload_type=cl_type,
                                                     commit=commit)
      entity.put()

    return entity


class VPGTargetsCLUploadManagerTest(CLUploadManagerTestCase):

  def testDefaultUploadConfig(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)

    config = manager.cl_upload_config

    self.assertEqual(config.cl_type, cl_upload_config.CLType.VPG_TARGETS)
    self.assertFalse(config.disabled)
    self.assertEqual(config.approval_method,
                     cl_upload_config.ApprovalMethod.MANUAL)
    self.assertCountEqual(config.reviewers, [])
    self.assertIsNone(config.bot_reviewer)
    self.assertCountEqual(config.ccs, [])

  def testUploadConfig(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    manager2 = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    self._SetConfig(
        manager, disabled=True,
        approval_method=cl_upload_config.ApprovalMethod.BOT, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])
    # yapf: disable
    self._SetConfig(manager2, reviewers=['foo@example.com'],  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                    ccs=['bar@example.com'])

    config = manager.cl_upload_config

    self.assertEqual(config.cl_type, cl_upload_config.CLType.VPG_TARGETS)
    self.assertTrue(config.disabled)
    self.assertEqual(config.approval_method,
                     cl_upload_config.ApprovalMethod.BOT)
    self.assertCountEqual(config.reviewers, ['reviewer@example.com'])
    self.assertEqual(config.bot_reviewer, 'bot-reviewer@example.com')
    self.assertCountEqual(config.ccs, ['cc@example.com'])

  def testShouldGenerateContent(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    self._SetConfig(manager, disabled=False)

    res = manager.ShouldGenerateContent()

    self.assertTrue(res)

  def testShouldGenerateContent_WithDisabledConfig_ShouldReturnFalse(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    self._SetConfig(manager, disabled=True)

    res = manager.ShouldGenerateContent()

    self.assertFalse(res)

  def testShouldGenerateContent_WithForceGenerate_ShouldReturnTrue(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    self._SetConfig(manager, disabled=True)

    res = manager.ShouldGenerateContent(force_generate=True)

    self.assertTrue(res)

  def testGetLatestVPGTargetsHash(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash')

    res = manager.GetLatestVPGTargetsHash()

    self.assertEqual(res, 'fake-hash')

  def testSetLatestVPGTargetsHash(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    factor = self._SetCLUploadFactor(manager, latest_content_hash='fake-hash')

    manager.SetLatestVPGTargetsHash('new-hash')

    with self._ndb_connector.CreateClientContext():
      factor = factor.key.get()

    self.assertEqual(factor.latest_content_hash, 'new-hash')

  def testShouldCreateCL_HashChanged_ShouldReturnTrue(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash')

    res = manager.ShouldCreateCL('new-hash')

    self.assertTrue(res)

  def testShouldCreateCL_HashNotChanged_ShouldReturnFalse(self):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash')

    res = manager.ShouldCreateCL('fake-hash')

    self.assertFalse(res)

  @mock.patch('cros.factory.hwid.service.appengine.git_util.CreateOrPatchCL')
  def testCreateCL_WithBotReviewer(self, mock_create_patch_cl):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
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
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
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
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
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
  def testCreateCL_WithDryRun_ShouldNotCreateCL(self, mock_create_patch_cl):
    manager = cl_upload_config.VPGTargetsCLUploadManager(self._ndb_connector)
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


class PayloadCLUploadManagerTest(CLUploadManagerTestCase):

  def testDefaultVerificationPayloadUploadConfig(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)

    config = manager.cl_upload_config

    self.assertEqual(config.cl_type,
                     cl_upload_config.CLType.VERIFICATION_PAYLOAD)
    self.assertFalse(config.disabled)
    self.assertEqual(config.approval_method,
                     cl_upload_config.ApprovalMethod.MANUAL)
    self.assertCountEqual(config.reviewers, [])
    self.assertIsNone(config.bot_reviewer)
    self.assertCountEqual(config.ccs, [])

  def testDefaultHWIDSelectionPayloadUploadConfig(self):
    manager = cl_upload_config.HWIDSelectionPayloadCLUploadManager(
        self._ndb_connector)

    config = manager.cl_upload_config

    self.assertEqual(config.cl_type,
                     cl_upload_config.CLType.HWID_SELECTION_PAYLOAD)
    self.assertFalse(config.disabled)
    self.assertEqual(config.approval_method,
                     cl_upload_config.ApprovalMethod.MANUAL)
    self.assertCountEqual(config.reviewers, [])
    self.assertIsNone(config.bot_reviewer)
    self.assertCountEqual(config.ccs, [])

  def testGetLatestHWIDMainCommit(self):
    vp_manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    selection_manager = cl_upload_config.HWIDSelectionPayloadCLUploadManager(
        self._ndb_connector)
    self._SetLatestHWIDMainCommit(vp_manager, commit='fake-commit')
    self._SetLatestHWIDMainCommit(selection_manager, commit='fake-commit2')

    vp_commit = vp_manager.GetLatestHWIDMainCommit()
    selection_commit = selection_manager.GetLatestHWIDMainCommit()

    self.assertEqual(vp_commit, 'fake-commit')
    self.assertEqual(selection_commit, 'fake-commit2')

  def testSetLatestHWIDMainCommit(self):
    vp_manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    selection_manager = cl_upload_config.HWIDSelectionPayloadCLUploadManager(
        self._ndb_connector)
    vp_commit = self._SetLatestHWIDMainCommit(vp_manager, commit='fake-commit')
    selection_commit = self._SetLatestHWIDMainCommit(selection_manager,
                                                     commit='fake-commit2')

    vp_manager.SetLatestHWIDMainCommit('new-commit')
    selection_manager.SetLatestHWIDMainCommit('new-commit2')

    with self._ndb_connector.CreateClientContext():
      vp_commit = vp_commit.key.get()
      selection_commit = selection_commit.key.get()

    self.assertEqual(vp_commit.commit, 'new-commit')
    self.assertEqual(selection_commit.commit, 'new-commit2')

  def testGetLatestPayloadHash(self):
    vp_manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    selection_manager = cl_upload_config.HWIDSelectionPayloadCLUploadManager(
        self._ndb_connector)
    # yapf: disable
    self._SetCLUploadFactor(vp_manager, latest_content_hash='fake-hash1',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board1')
    # yapf: disable
    self._SetCLUploadFactor(vp_manager, latest_content_hash='fake-hash2',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board2')
    # yapf: disable
    self._SetCLUploadFactor(selection_manager, latest_content_hash='fake-hash3',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board1')
    # yapf: disable
    self._SetCLUploadFactor(selection_manager, latest_content_hash='fake-hash4',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board2')

    res1 = vp_manager.GetLatestPayloadHash(board='fake-board1')
    res2 = vp_manager.GetLatestPayloadHash(board='fake-board2')
    res3 = selection_manager.GetLatestPayloadHash(board='fake-board1')
    res4 = selection_manager.GetLatestPayloadHash(board='fake-board2')

    self.assertEqual(res1, 'fake-hash1')
    self.assertEqual(res2, 'fake-hash2')
    self.assertEqual(res3, 'fake-hash3')
    self.assertEqual(res4, 'fake-hash4')

  def testSetLatestPayloadHash(self):
    vp_manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    selection_manager = cl_upload_config.HWIDSelectionPayloadCLUploadManager(
        self._ndb_connector)
    factor1 = self._SetCLUploadFactor(
        # yapf: disable
        vp_manager, latest_content_hash='fake-hash1', board='fake-board1')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    factor2 = self._SetCLUploadFactor(
        # yapf: disable
        vp_manager, latest_content_hash='fake-hash2', board='fake-board2')  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    # yapf: disable
    factor3 = self._SetCLUploadFactor(selection_manager,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                                      latest_content_hash='fake-hash3',
                                      board='fake-board1')
    # yapf: disable
    factor4 = self._SetCLUploadFactor(selection_manager,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                                      latest_content_hash='fake-hash4',
                                      board='fake-board2')

    vp_manager.SetLatestPayloadHash('new-hash1', board='fake-board1')
    selection_manager.SetLatestPayloadHash('new-hash2', board='fake-board2')

    with self._ndb_connector.CreateClientContext():
      factor1 = factor1.key.get()
      factor2 = factor2.key.get()
      factor3 = factor3.key.get()
      factor4 = factor4.key.get()

    self.assertEqual(factor1.latest_content_hash, 'new-hash1')
    self.assertEqual(factor2.latest_content_hash, 'fake-hash2')
    self.assertEqual(factor3.latest_content_hash, 'fake-hash3')
    self.assertEqual(factor4.latest_content_hash, 'new-hash2')

  def testShouldGenerateContent(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    # yapf: disable
    self._SetConfig(manager, disabled=False)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self._SetLatestHWIDMainCommit(manager, commit='fake-commit')

    res = manager.ShouldGenerateContent("fake-commit2", False)

    self.assertTrue(res)

  def testShouldGenerateContent_WithDisabledConfig_ShouldReturnFalse(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    # yapf: disable
    self._SetConfig(manager, disabled=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    res = manager.ShouldGenerateContent("fake-commit", False)

    self.assertFalse(res)

  def testShouldGenerateContent_WithUnchangedHwidCommit_ShouldReturnFalse(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    # yapf: disable
    self._SetConfig(manager, disabled=False)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    self._SetLatestHWIDMainCommit(manager, commit='fake-commit')

    res = manager.ShouldGenerateContent("fake-commit", False)

    self.assertFalse(res)

  def testShouldGenerateContent_WithForceGenerate_ShouldReturnTrue(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    # yapf: disable
    self._SetConfig(manager, disabled=True)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    res = manager.ShouldGenerateContent("fake-commit", True)

    self.assertTrue(res)

  def testShouldGenerateContent_MissingMandatoryArg_ShouldRaiseError(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)

    self.assertRaisesRegex(ValueError, 'hwid_live_commit must be specified',
                           manager.ShouldGenerateContent)

  def testShouldCreateCL_HashChanged_ShouldReturnTrue(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    # yapf: disable
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash1',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board1')
    # yapf: disable
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash2',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board2')

    res = manager.ShouldCreateCL('fake-hash2', board='fake-board1')

    self.assertTrue(res)

  def testShouldCreateCL_HashNotChanged_ShouldReturnFalse(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    # yapf: disable
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash1',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board1')
    # yapf: disable
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash2',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board2')

    res = manager.ShouldCreateCL('fake-hash1', board='fake-board1')

    self.assertFalse(res)

  def testShouldCreateCL_MissingMandatoryArg_ShouldRaiseError(self):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)

    self.assertRaisesRegex(ValueError, 'board must be specified',
                           manager.ShouldCreateCL, content_hash='fake-hash')

  @mock.patch('cros.factory.hwid.service.appengine.git_util.CreateOrPatchCL')
  def testCreateCL(self, mock_create_patch_cl):
    manager = cl_upload_config.VerificationPayloadCLUploadManager(
        self._ndb_connector)
    self._SetConfig(
        # yapf: disable
        manager, disabled=False,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        approval_method=cl_upload_config.ApprovalMethod.BOT, reviewers=[
            'reviewer@example.com'
        ], bot_reviewer='bot-reviewer@example.com', ccs=['cc@example.com'])
    # yapf: disable
    self._SetCLUploadFactor(manager, latest_content_hash='fake-hash',  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
                            board='fake-board')
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


if __name__ == '__main__':
  unittest.main()
