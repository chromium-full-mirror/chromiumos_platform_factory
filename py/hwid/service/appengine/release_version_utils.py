# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import datetime
import enum
import logging
from typing import Mapping, NamedTuple, Optional
from xml.dom import minidom

from google.cloud import bigquery
from google.cloud import ndb
# yapf: disable
from packaging import version as version_module  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

from cros.factory.hwid.service.appengine import git_util
from cros.factory.hwid.service.appengine import hwid_repo
from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module


# yapf: enable

_MANIFEST_VERSIONS_PROJECT = 'chromeos/manifest-versions'
_BUILDSPEC_PATH = 'buildspecs/{milestone}/{version}.xml'


class ImageVersionType(enum.Enum):
  LATEST_PUSHED_STABLE = enum.auto()
  LATEST_PUSHED_LTS = enum.auto()


class ImageVersion(NamedTuple):
  milestone: int
  version: version_module.Version


class PushedReleaseVersion(ndb.Model):
  _CACHE_TIMEOUT = 60 * 60
  project = ndb.StringProperty()
  stable_milestone = ndb.IntegerProperty()
  stable_version = ndb.StringProperty()
  lts_milestone = ndb.IntegerProperty()
  lts_version = ndb.StringProperty()
  updated_time = ndb.DateTimeProperty()

  @property
  def is_expired(self):
    return self.updated_time + datetime.timedelta(
        seconds=self._CACHE_TIMEOUT) < datetime.datetime.now()


class ReleasedRepoCommit(ndb.Model):
  repo_name = ndb.StringProperty()
  milestone = ndb.IntegerProperty()
  version = ndb.StringProperty()
  commit = ndb.StringProperty()


def _ExtractRevisionFromManifest(dom, repo_name: str) -> Optional[str]:
  for project_node in dom.getElementsByTagName('project'):
    if project_node.getAttribute('name') == repo_name:
      return project_node.getAttribute('revision')
  return None


class CommitUnavailableError(Exception):
  """An exception raised when the commit ID is unavailable given the config."""


class InvalidVersionError(ValueError):
  """An exception raised when the version string is invalid."""


def ParseVersion(version_str: str) -> version_module.Version:
  """Parses version to a Version instance.

  Args:
    version_str: A version string.

  Returns:
    A Version instance.

  Raises:
    InvalidVersionError when the version string is invalid.
  """

  try:
    version = version_module.parse(version_str)
  except version_module.InvalidVersion:
    raise InvalidVersionError(f'Invalid version: {version_str}') from None

  if not isinstance(version, version_module.Version):
    raise InvalidVersionError(f'Invalid version: {version_str}')

  return version


class ReleaseVersionManager:
  """The class responsible for handling release version query and caching."""

  def __init__(
      self,
      bigquery_cloud_project: str,
      latest_push_sql: str,
      ndb_connector: ndbc_module.NDBConnector,
  ):
    self._bigquery_cloud_project = bigquery_cloud_project
    self._latest_push_sql = latest_push_sql
    self._ndb_connector = ndb_connector

  def GetLatestPushedVersions(
      self, project: str) -> Mapping[ImageVersionType, ImageVersion]:
    """Gets the latests pushed version by given project name.

    This method also caches the fetched image versions with 1 hour expiration in
    datastore as different projects might share a board even same image release.

    Args:
      project: The project as a string.

    Returns:
      A mapping of ImageVersionType to ImageVersion instances.
    """
    pushed_versions = {}
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      entity = PushedReleaseVersion.query(
          PushedReleaseVersion.project == project,
      ).get()
      if entity is not None:
        if entity.is_expired:
          entity.key.delete()
        else:
          if entity.stable_milestone:
            try:
              version = ParseVersion(entity.stable_version)
            except InvalidVersionError:
              logging.info('Skip invalid version: %s', entity.stable_version)
            else:
              pushed_versions[ImageVersionType.LATEST_PUSHED_STABLE] = (
                  ImageVersion(entity.stable_milestone, version))
          if entity.lts_milestone:
            try:
              version = ParseVersion(entity.lts_version)
            except InvalidVersionError:
              logging.info('Skip invalid version: %s', entity.lts_version)
            else:
              pushed_versions[ImageVersionType.LATEST_PUSHED_LTS] = (
                  ImageVersion(entity.lts_milestone, version))
          return pushed_versions

    client = bigquery.Client(project=self._bigquery_cloud_project)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('project', 'STRING', project.lower())
        ],
    )
    query = client.query(self._latest_push_sql, job_config=job_config)
    rows = query.result()
    for row in rows:
      try:
        version = ParseVersion(row['version'])
      except InvalidVersionError:
        logging.info('Skip invalid version: %s', row['version'])
        continue
      candidate = ImageVersion(row['milestone'], version)
      if row['release_type'] in ('LTC', 'LTR'):
        pushed_versions[ImageVersionType.LATEST_PUSHED_LTS] = max(
            candidate,
            pushed_versions.get(ImageVersionType.LATEST_PUSHED_LTS, candidate))
      else:
        pushed_versions[ImageVersionType.LATEST_PUSHED_STABLE] = max(
            candidate,
            pushed_versions.get(ImageVersionType.LATEST_PUSHED_STABLE,
                                candidate))
    entity = PushedReleaseVersion(project=project,
                                  updated_time=datetime.datetime.now())

    stable = pushed_versions.get(ImageVersionType.LATEST_PUSHED_STABLE)
    if stable is not None:
      entity.stable_milestone = stable.milestone
      entity.stable_version = str(stable.version)

    lts = pushed_versions.get(ImageVersionType.LATEST_PUSHED_LTS)
    if lts is not None:
      entity.lts_milestone = lts.milestone
      entity.lts_version = str(lts.version)

    with self._ndb_connector.CreateClientContextWithGlobalCache():
      entity.put()
    return pushed_versions

  def GetCommitID(self, repo_name: str, image_version: ImageVersion) -> str:
    """Gets the commit ID of a certain repo name and image version.

    Args:
      repo_name: The repo name.
      image_version: The ImageVersion to query.

    Returns:
      A string as the commit id.

    Raises:
      CommitUnavailableError: Raised if the commit ID is unavailable from the
        manifest repo.
    """
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      entity = ReleasedRepoCommit.query(
          ReleasedRepoCommit.repo_name == repo_name,
          ReleasedRepoCommit.milestone == image_version.milestone,
          ReleasedRepoCommit.version == str(image_version.version),
      ).get()
      if entity is not None:
        return entity.commit
    try:
      buildspec_content = git_util.GetFileContent(
          gerrit_review_url=hwid_repo.INTERNAL_REPO_REVIEW_URL,
          project=_MANIFEST_VERSIONS_PROJECT,
          path=_BUILDSPEC_PATH.format(
              milestone=image_version.milestone,
              version=str(image_version.version),
          ),
          auth_cookie=git_util.GetGerritAuthCookie(),
      ).decode('utf8')
    except git_util.GitUtilException:
      raise CommitUnavailableError(
          'No corresponding manifest found with the given image version: '
          f'{image_version}.') from None
    with minidom.parseString(buildspec_content) as dom:
      commit = _ExtractRevisionFromManifest(dom, repo_name)
    if commit is None:
      raise CommitUnavailableError(
          f'No corresponding repo entry of the {repo_name!r} found in the '
          'manifest.')
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      ReleasedRepoCommit(
          repo_name=repo_name,
          milestone=image_version.milestone,
          version=str(image_version.version),
          commit=commit,
      ).put()
    return commit

  def CleanAllForTest(self):
    with self._ndb_connector.CreateClientContext():
      for key in PushedReleaseVersion.query().iter(keys_only=True):
        key.delete()
      for key in ReleasedRepoCommit.query().iter(keys_only=True):
        key.delete()
