#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import datetime
import textwrap
from typing import Optional
import unittest
from unittest import mock

from cros.factory.hwid.service.appengine import git_util
from cros.factory.hwid.service.appengine import release_version_utils
from cros.factory.hwid.service.appengine import test_utils


# yapf: enable

_ImageVersionType = release_version_utils.ImageVersionType
_ImageVersion = release_version_utils.ImageVersion


class ReleaseVersionManagerTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._modules = test_utils.FakeModuleCollection()
    self._ndb_connector = self._modules.ndb_connector
    self._release_version_manager = release_version_utils.ReleaseVersionManager(
        bigquery_cloud_project='cloud-project',
        latest_push_sql='push-sql with @project',
        ndb_connector=self._ndb_connector,
    )

  def tearDown(self):
    super().tearDown()
    self._release_version_manager.CleanAllForTest()
    self._modules.ClearAll()

  def _AddPushedReleaseVersionEntries(
      self,
      project: str,
      stable_milestone: Optional[int] = None,
      stable_version: Optional[str] = None,
      lts_milestone: Optional[int] = None,
      lts_version: Optional[str] = None,
      updated_time: Optional[datetime.datetime] = None,
  ):
    with self._ndb_connector.CreateClientContext():
      release_version_utils.PushedReleaseVersion(
          project=project,
          stable_milestone=stable_milestone,
          stable_version=stable_version,
          lts_milestone=lts_milestone,
          lts_version=lts_version,
          updated_time=updated_time,
      ).put()

  def _AddReleaseRepoCommit(
      self,
      repo_name: Optional[str] = None,
      milestone: Optional[int] = None,
      version: Optional[str] = None,
      commit: Optional[str] = None,
  ):
    with self._ndb_connector.CreateClientContext():
      release_version_utils.ReleasedRepoCommit(
          repo_name=repo_name,
          milestone=milestone,
          version=version,
          commit=commit,
      ).put()

  @mock.patch.object(release_version_utils.bigquery, 'Client')
  def testGetLatestPushedVersion_NoCache(self, mock_bq_client_cls):
    mock_bq_client = mock_bq_client_cls.return_value
    mock_bq_client.query.return_value.result.return_value = [
        {
            'milestone': 100,
            'version': '11111.11.1',
            'release_type': 'LTC',
        },
        {
            'milestone': 120,
            'version': '22222.22.2',
            'release_type': 'LTR',
        },
        {
            'milestone': 130,
            'version': '33333.33.3',
            'release_type': 'SCHEDULED_RELEASE',
        },
        {
            'milestone': 140,
            'version': '44444.44.4',
            'release_type': 'SCHEDULED_RELEASE',
        },
    ]

    release_versions = self._release_version_manager.GetLatestPushedVersions(
        'THEPROJ')

    mock_bq_client_cls.assert_called_once_with(project='cloud-project')
    mock_bq_client.query.assert_called_once_with('push-sql with @project',
                                                 job_config=mock.ANY)
    self.assertEqual(
        {
            _ImageVersionType.LATEST_PUSHED_LTS:
                _ImageVersion(
                    milestone=120,
                    version=release_version_utils.ParseVersion('22222.22.2'),
                ),
            _ImageVersionType.LATEST_PUSHED_STABLE:
                _ImageVersion(
                    milestone=140,
                    version=release_version_utils.ParseVersion('44444.44.4'),
                ),
        }, release_versions)
    with self._ndb_connector.CreateClientContext():
      cached_data = release_version_utils.PushedReleaseVersion.query().fetch()
    self.assertEqual(1, len(cached_data))
    cached_release_version = cached_data[0]
    self.assertEqual(cached_release_version.project, 'THEPROJ')
    self.assertEqual(cached_release_version.stable_milestone, 140)
    self.assertEqual(cached_release_version.stable_version, '44444.44.4')
    self.assertEqual(cached_release_version.lts_milestone, 120)
    self.assertEqual(cached_release_version.lts_version, '22222.22.2')

  @mock.patch.object(release_version_utils.bigquery, 'Client')
  def testGetLatestPushedVersion_CompBySemVer(self, mock_bq_client_cls):
    mock_bq_client = mock_bq_client_cls.return_value
    mock_bq_client.query.return_value.result.return_value = [
        {
            'milestone': 100,
            'version': '999.99.9',
            'release_type': 'LTC',
        },
        {
            'milestone': 100,
            'version': '1111.11.1',
            'release_type': 'LTR',
        },
        {
            'milestone': 200,
            'version': '9999.99.9',
            'release_type': 'SCHEDULED_RELEASE',
        },
        {
            'milestone': 200,
            'version': '11111.11.1',
            'release_type': 'SCHEDULED_RELEASE',
        },
    ]

    release_versions = self._release_version_manager.GetLatestPushedVersions(
        'THEPROJ')

    mock_bq_client_cls.assert_called_once_with(project='cloud-project')
    mock_bq_client.query.assert_called_once_with('push-sql with @project',
                                                 job_config=mock.ANY)
    self.assertEqual(
        {
            _ImageVersionType.LATEST_PUSHED_LTS:
                _ImageVersion(
                    milestone=100,
                    version=release_version_utils.ParseVersion('1111.11.1'),
                ),
            _ImageVersionType.LATEST_PUSHED_STABLE:
                _ImageVersion(
                    milestone=200,
                    version=release_version_utils.ParseVersion('11111.11.1'),
                ),
        }, release_versions)

  @mock.patch.object(release_version_utils.bigquery, 'Client')
  def testGetLatestPushedVersion_WithCache(self, mock_bq_client_cls):
    self._AddPushedReleaseVersionEntries(
        project='THEPROJ',
        stable_milestone=140,
        stable_version='44444.44.4',
        lts_milestone=120,
        lts_version='22222.22.2',
        updated_time=datetime.datetime.now(),
    )

    release_versions = self._release_version_manager.GetLatestPushedVersions(
        'THEPROJ')

    mock_bq_client_cls.assert_not_called()
    self.assertEqual(
        {
            _ImageVersionType.LATEST_PUSHED_LTS:
                _ImageVersion(
                    milestone=120,
                    version=release_version_utils.ParseVersion('22222.22.2'),
                ),
            _ImageVersionType.LATEST_PUSHED_STABLE:
                _ImageVersion(
                    milestone=140,
                    version=release_version_utils.ParseVersion('44444.44.4'),
                ),
        }, release_versions)

  @mock.patch.object(release_version_utils.bigquery, 'Client')
  def testGetLatestPushedVersion_WithCacheStableOnly(self, mock_bq_client_cls):
    self._AddPushedReleaseVersionEntries(
        project='THEPROJ',
        stable_milestone=140,
        stable_version='44444.44.4',
        updated_time=datetime.datetime.now(),
    )

    release_versions = self._release_version_manager.GetLatestPushedVersions(
        'THEPROJ')

    mock_bq_client_cls.assert_not_called()
    self.assertEqual(
        {
            _ImageVersionType.LATEST_PUSHED_STABLE:
                _ImageVersion(
                    milestone=140,
                    version=release_version_utils.ParseVersion('44444.44.4'),
                ),
        }, release_versions)

  @mock.patch.object(release_version_utils.bigquery, 'Client')
  def testGetLatestPushedVersion_CacheExpired(self, mock_bq_client_cls):
    self._AddPushedReleaseVersionEntries(
        project='THEPROJ',
        stable_milestone=40,
        stable_version='1000.00.0',
        lts_milestone=20,
        lts_version='999.99.9',
        updated_time=datetime.datetime(1970, 1, 1),
    )
    mock_bq_client = mock_bq_client_cls.return_value
    mock_bq_client.query.return_value.result.return_value = [
        {
            'milestone': 100,
            'version': '11111.11.1',
            'release_type': 'LTC',
        },
        {
            'milestone': 120,
            'version': '22222.22.2',
            'release_type': 'LTR',
        },
        {
            'milestone': 130,
            'version': '33333.33.3',
            'release_type': 'SCHEDULED_RELEASE',
        },
        {
            'milestone': 140,
            'version': '44444.44.4',
            'release_type': 'SCHEDULED_RELEASE',
        },
    ]

    release_versions = self._release_version_manager.GetLatestPushedVersions(
        'THEPROJ')

    mock_bq_client_cls.assert_called_once_with(project='cloud-project')
    mock_bq_client.query.assert_called_once_with('push-sql with @project',
                                                 job_config=mock.ANY)
    self.assertEqual(
        {
            _ImageVersionType.LATEST_PUSHED_LTS:
                _ImageVersion(
                    milestone=120,
                    version=release_version_utils.ParseVersion('22222.22.2'),
                ),
            _ImageVersionType.LATEST_PUSHED_STABLE:
                _ImageVersion(
                    milestone=140,
                    version=release_version_utils.ParseVersion('44444.44.4'),
                ),
        }, release_versions)
    with self._ndb_connector.CreateClientContext():
      cached_data = release_version_utils.PushedReleaseVersion.query().fetch()
    self.assertEqual(1, len(cached_data))
    cached_release_version = cached_data[0]
    self.assertEqual(cached_release_version.project, 'THEPROJ')
    self.assertEqual(cached_release_version.stable_milestone, 140)
    self.assertEqual(cached_release_version.stable_version, '44444.44.4')
    self.assertEqual(cached_release_version.lts_milestone, 120)
    self.assertEqual(cached_release_version.lts_version, '22222.22.2')

  @mock.patch.object(release_version_utils.bigquery, 'Client')
  def testGetLatestPushedVersion_InvalidVersionStr(self, mock_bq_client_cls):
    mock_bq_client = mock_bq_client_cls.return_value
    mock_bq_client.query.return_value.result.return_value = [
        {
            'milestone': 139,
            'version': '12345.1.1',
            'release_type': 'SCHEDULED_RELEASE',
        },
        {
            'milestone': 140,
            'version': 'this-is-an-invalid-version',
            'release_type': 'SCHEDULED_RELEASE',
        },
    ]

    release_versions = self._release_version_manager.GetLatestPushedVersions(
        'THEPROJ')

    self.assertEqual(
        {
            _ImageVersionType.LATEST_PUSHED_STABLE:
                _ImageVersion(
                    milestone=139,
                    version=release_version_utils.ParseVersion('12345.1.1'),
                ),
        }, release_versions)

  @mock.patch.object(release_version_utils.git_util, 'GetGerritAuthCookie')
  @mock.patch.object(release_version_utils.git_util, 'GetFileContent')
  def testGetCommitID_NoCache(
      self,
      mock_get_file_content,
      unused_mock_get_auth_cookie,
  ):
    mock_get_file_content.return_value = textwrap.dedent('''\
        <?xml version="1.0" encoding="UTF-8"?>
        <manifest>
          <project name="another-repo"
            path="path/to/another-repo"
            revision="another-revision"
            upstream="another-upstream"
            dest-branch="another-dest-branch"/>
          <project name="target-repo"
            path="path/to/target"
            revision="target-revision"
            upstream="target-upstream"
            dest-branch="target-dest-branch"/>
          <project name="yet-another-repo"
            path="path/to/yet-another-repo"
            revision="yet-another-revision"
            upstream="yet-another-upstream"
            dest-branch="yet-another-dest-branch"/>
        </manifest>
    ''').encode('utf8')

    commit = self._release_version_manager.GetCommitID(
        repo_name='target-repo',
        image_version=_ImageVersion(
            milestone=100,
            version=release_version_utils.ParseVersion('12345.67.8'),
        ),
    )

    mock_get_file_content.assert_called_once_with(
        gerrit_review_url='https://chrome-internal-review.googlesource.com',
        project='chromeos/manifest-versions',
        path='buildspecs/100/12345.67.8.xml',
        auth_cookie=mock.ANY,
    )
    self.assertEqual('target-revision', commit)
    with self._ndb_connector.CreateClientContext():
      cached_data = release_version_utils.ReleasedRepoCommit.query().fetch()
    self.assertEqual(1, len(cached_data))
    cached_repo_commit = cached_data[0]
    self.assertEqual(cached_repo_commit.repo_name, 'target-repo')
    self.assertEqual(cached_repo_commit.milestone, 100)
    self.assertEqual(cached_repo_commit.version, '12345.67.8')
    self.assertEqual(cached_repo_commit.commit, 'target-revision')

  @mock.patch.object(release_version_utils.git_util, 'GetFileContent')
  def testGetCommitID_WithCache(self, mock_get_file_content):
    self._AddReleaseRepoCommit(
        repo_name='target-repo',
        milestone=100,
        version='12345.67.8',
        commit='target-revision',
    )

    commit = self._release_version_manager.GetCommitID(
        repo_name='target-repo',
        image_version=_ImageVersion(
            milestone=100,
            version=release_version_utils.ParseVersion('12345.67.8'),
        ),
    )

    mock_get_file_content.assert_not_called()
    self.assertEqual('target-revision', commit)
    with self._ndb_connector.CreateClientContext():
      cached_data = release_version_utils.ReleasedRepoCommit.query().fetch()
    self.assertEqual(1, len(cached_data))
    cached_repo_commit = cached_data[0]
    self.assertEqual(cached_repo_commit.repo_name, 'target-repo')
    self.assertEqual(cached_repo_commit.milestone, 100)
    self.assertEqual(cached_repo_commit.version, '12345.67.8')
    self.assertEqual(cached_repo_commit.commit, 'target-revision')

  @mock.patch.object(release_version_utils.git_util, 'GetGerritAuthCookie')
  @mock.patch.object(release_version_utils.git_util, 'GetFileContent')
  def testGetCommitID_NoManifest(
      self,
      mock_get_file_content,
      unused_mock_get_auth_cookie,
  ):
    mock_get_file_content.side_effect = git_util.GitUtilException

    with self.assertRaisesRegex(
        release_version_utils.CommitUnavailableError,
        ('No corresponding manifest found with the given image version: '
         r"ImageVersion\(milestone=100, "
         r"version=<Version\('12345\.67\.8'\)>\)\.")):
      self._release_version_manager.GetCommitID(
          repo_name='target-repo',
          image_version=_ImageVersion(
              milestone=100,
              version=release_version_utils.ParseVersion('12345.67.8'),
          ),
      )

  @mock.patch.object(release_version_utils.git_util, 'GetGerritAuthCookie')
  @mock.patch.object(release_version_utils.git_util, 'GetFileContent')
  def testGetCommitID_NoEntryOfRepoInManifest(
      self,
      mock_get_file_content,
      unused_mock_get_auth_cookie,
  ):
    mock_get_file_content.return_value = textwrap.dedent('''\
        <?xml version="1.0" encoding="UTF-8"?>
        <manifest>
          <project name="another-repo"
            path="path/to/another-repo"
            revision="another-revision"
            upstream="another-upstream"
            dest-branch="another-dest-branch"/>
          <project name="not-target-repo"
            path="path/to/not-target"
            revision="not-target-revision"
            upstream="not-target-upstream"
            dest-branch="not-target-dest-branch"/>
          <project name="yet-another-repo"
            path="path/to/yet-another-repo"
            revision="yet-another-revision"
            upstream="yet-another-upstream"
            dest-branch="yet-another-dest-branch"/>
        </manifest>
    ''').encode('utf8')

    with self.assertRaisesRegex(
        release_version_utils.CommitUnavailableError,
        ("No corresponding repo entry of the 'target-repo' found in the "
         r'manifest\.')):
      self._release_version_manager.GetCommitID(
          repo_name='target-repo',
          image_version=_ImageVersion(
              milestone=100,
              version=release_version_utils.ParseVersion('12345.67.8'),
          ),
      )


if __name__ == '__main__':
  unittest.main()
