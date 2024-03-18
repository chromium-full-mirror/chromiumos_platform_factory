# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import enum
import logging
import textwrap
from typing import Optional, Sequence, Tuple, Union

from google.cloud import ndb

from cros.factory.hwid.service.appengine import git_util
from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module


class CLType(str, enum.Enum):
  """The known CL content types."""

  UNKNOWN = ''
  VERIFICATION_PAYLOAD = 'verification_payload'
  HWID_SELECTION_PAYLOAD = 'hwid_selection_payload'
  VPG_TARGETS = 'vpg_targets'

  def __str__(self):
    return self.value


class ApprovalMethod(str, enum.Enum):
  """The CL approval methods.

  Attributes:
    MANUAL: Reviewed by assigned reviewers.
    SELF: Reviewed by the service itself with the service account.
    BOT: Reviewed by a configured bot reviewer.
  """

  MANUAL = 'manual'
  SELF = 'self'
  BOT = 'bot'

  def __str__(self):
    return self.value


class CLUploadConfig(ndb.Model):
  """A config for uploading CL which can be modified on Datastore.

  Attributes:
    cl_type: The type of CL content. See also CLType.
    disabled: Disable the generation of content corresponding to cl_type.
    approval_method: Approval method of CL. See also ApprovalMethod.
        Default: "manual".
    reviewers: E-mail addresses to be added to reviewer of CL. The reviewers
        will be added to cc if approval_method is not "manual".
    bot_reviewer: The bot service account to be added to reviewer of CL. It's
        valid only if approval_method is "bot".
    ccs: E-mail addresses to be added to cc of CL.
  """

  cl_type = ndb.StringProperty(choices=set(CLType))
  disabled = ndb.BooleanProperty(default=False)
  approval_method = ndb.StringProperty(default=ApprovalMethod.MANUAL,
                                       choices=set(ApprovalMethod))
  reviewers = ndb.StringProperty(repeated=True)
  bot_reviewer = ndb.StringProperty()
  ccs = ndb.StringProperty(repeated=True)


class CLUploadManager:

  def __init__(self, ndb_connector: ndbc_module.NDBConnector, cl_type: CLType):
    self._ndb_connector = ndb_connector
    self._cl_type = cl_type
    self._logger = logging.getLogger(
        f'{self.__class__.__name__}.{self._cl_type}')

  @property
  def cl_type(self) -> CLType:
    return self._cl_type

  @property
  def cl_upload_config(self) -> CLUploadConfig:
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      entity = CLUploadConfig.query(
          CLUploadConfig.cl_type == self._cl_type).get()
      if entity is None:
        return CLUploadConfig(cl_type=self._cl_type)
      return entity

  def CreateCL(
      self,
      dryrun: bool,
      git_url: str,
      auth_cookie: str,
      branch: str,
      new_files: Sequence[Tuple[str, int, Union[str, bytes]]],
      author: str,
      committer: str,
      commit_msg: str,
      *,
      repo: Optional[git_util.MemoryRepo] = None,
      topic: Optional[str] = None,
      verified: int = 0,
      auto_submit: bool = False,
      rubber_stamper: bool = False,
      hashtags: Optional[Sequence[str]] = None,
      files_to_delete: Optional[Sequence[str]] = None,
  ) -> Tuple[Optional[str], Optional[int]]:
    """Creates a CL with given options.

    See git_util.CreateOrPatchCL() for descriptions of other arguments.

    Args:
      dryrun: Do everything except actually upload the CL.

    Returns:
      A tuple of (change ID, CL number).
      Both will be None if the CL is not created.

    Raises:
      ValueError: If the config format is invalid.
      See also git_util.CreateOrPatchCL().
    """
    config = self.cl_upload_config
    if config.disabled:
      self._logger.info(
          'The generation for %s is disabled, skip generating '
          'CL.', config.cl_type)
      return None, None

    if config.approval_method == ApprovalMethod.BOT:
      if not config.bot_reviewer:
        self._logger.warning('"bot_reviewer" config is empty')
      reviewers = [config.bot_reviewer]
      ccs = config.reviewers + config.ccs
      self_approval = False
    elif config.approval_method == ApprovalMethod.SELF:
      reviewers = []
      ccs = config.reviewers + config.ccs
      self_approval = True
    elif config.approval_method == ApprovalMethod.MANUAL:
      reviewers = config.reviewers
      ccs = config.ccs
      self_approval = False
    else:
      raise ValueError('Invalid approval_method: ', config.approval_method)

    if dryrun:
      # file_info = (file_path, mode, content)
      updated_file_paths = '\n'.join(
          '  ' + file_info[0] for file_info in new_files)
      deleted_file_paths = ''
      if files_to_delete:
        deleted_file_paths = '\n'.join('  ' + path for path in files_to_delete)

      debug_info = textwrap.dedent(f"""\
          Dryrun create
          git_url: {git_url}
          branch: {branch}
          author: {author}
          reviewers: {reviewers}
          cc: {ccs}
          bot_commit: {self_approval}
          commit_queue: {self_approval}
          auto_submit: {auto_submit}
          commit msg: \n{textwrap.indent(commit_msg, '          ')}
          update file paths: \n{
              textwrap.indent(updated_file_paths, '            - ')
          }
          delete file paths: \n{
              textwrap.indent(deleted_file_paths, '            - ')
          }
      """)
      self._logger.debug(debug_info)
      return None, None
    return git_util.CreateOrPatchCL(
        git_url, auth_cookie, branch, new_files, author, committer, commit_msg,
        reviewers=reviewers, cc=ccs, bot_commit=self_approval,
        commit_queue=self_approval, repo=repo, topic=topic, verified=verified,
        auto_submit=auto_submit, rubber_stamper=rubber_stamper,
        hashtags=hashtags, files_to_delete=files_to_delete)
