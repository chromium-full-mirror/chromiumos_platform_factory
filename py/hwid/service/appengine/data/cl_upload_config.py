# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import abc
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
  RMAD_FEATURE_ENABLED_DEVICES_PAYLOAD = 'rmad_feature_enabled_devices_payload'

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


class CLUploadFactor(ndb.Model):
  """Factors that influences whether to upload the CL or not.

  The factors will be used to decide whether to upload the CL or not. Different
  factors will be used based on the cl_type.

  Attributes:
    cl_type: The type of CL content. See also CLType.
    latest_content_hash: The hash value of the latest CL content.
    board: The board that the CL corresponds to. Used only for
        verification_payload and hwid_selection_payload CL types.
  """

  cl_type = ndb.StringProperty(choices=set(CLType))
  latest_content_hash = ndb.StringProperty()
  board = ndb.StringProperty()


class AbstractCLUploadManager(abc.ABC):
  """Abstract CL upload manager."""
  _cl_type: CLType

  def __init__(self, ndb_connector: ndbc_module.NDBConnector):
    self._ndb_connector = ndb_connector
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
      is_prod_env: bool,
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
        git_url,
        auth_cookie,
        branch,
        new_files,
        author,
        committer,
        commit_msg,
        is_prod_env,
        reviewers=reviewers,
        cc=ccs,
        bot_commit=self_approval,
        commit_queue=self_approval,
        repo=repo,
        topic=topic,
        verified=verified,
        auto_submit=auto_submit,
        rubber_stamper=rubber_stamper,
        hashtags=hashtags,
        files_to_delete=files_to_delete,
    )

  def AbandonCL(self, dryrun: bool, review_host: str, auth_cookie: str,
                change_id: str, reason: Optional[str] = None):
    """Abandons a CL.

    See git_util.AbandonCL() for descriptions of other arguments.

    Args:
      dryrun: Do everything except actually upload the CL.

    Raises:
      See git_util.AbandonCL().
    """
    if dryrun:
      debug_info = textwrap.dedent(f"""\
          Dryrun abandon
          review_host: {review_host}
          change_id: {change_id}
      """)
      self._logger.debug(debug_info)
      return

    git_util.AbandonCL(review_host, auth_cookie, change_id, reason)

  def _GetLatestContentHash(self, board: Optional[str] = None) -> Optional[str]:
    """Gets the latest content hash.

    Args:
      board: See CLUploadFactor.board.

    Returns:
      None if the entity does not exist. Otherwise, the latest content hash
      string.
    """
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      q = CLUploadFactor.query(CLUploadFactor.cl_type == self._cl_type)
      if board is not None:
        q = q.filter(CLUploadFactor.board == board)

      entity = q.get()
      return entity.latest_content_hash if entity is not None else None

  def _SetLatestContentHash(self, content_hash: str,
                            board: Optional[str] = None):
    """Sets the latest content hash.

    Args:
      content_hash: The hash value to set.
      board: See CLUploadFactor.board.
    """
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      q = CLUploadFactor.query(CLUploadFactor.cl_type == self._cl_type)
      if board is not None:
        q = q.filter(CLUploadFactor.board == board)

      entity = q.get()
      if entity is None:
        entity = CLUploadFactor(cl_type=self._cl_type, board=board)
      entity.latest_content_hash = content_hash
      entity.put()

  @abc.abstractmethod
  def ShouldCreateCL(self, content_hash: str, board: Optional[str] = None,
                     force_create: bool = False) -> bool:
    """Checks if the CL should be created.

    This function is called after the generation of contents is completed to
    avoid creating duplicate CLs with the same content.

    Args:
      content_hash: See CLUploadFactor.latest_content_hash.
      board: See CLUploadFactor.board.
      force_create: Set to True when force to create the CL.

    Raises:
      ValueError: If any mandatory parameters are not specified.
    """


class VPGTargetsCLUploadManager(AbstractCLUploadManager):
  """CL upload manager for VPG targets."""
  _cl_type = CLType.VPG_TARGETS

  def ShouldCreateCL(self, content_hash: str, board: Optional[str] = None,
                     force_create: bool = False) -> bool:
    """See base class."""
    del board  # unused.

    if force_create:
      self._logger.info('Force to create CL for %s.',
                        self.cl_upload_config.cl_type)
      return True
    latest_vpg_targets_hash = self.GetLatestVPGTargetsHash()
    if content_hash == latest_vpg_targets_hash:
      self._logger.info('%s hash value is not changed (%s), skip creating CL',
                        self._cl_type, content_hash)
      return False
    return True

  def GetLatestVPGTargetsHash(self) -> Optional[str]:
    """Gets the latest VPG targets content hash.

    Returns:
      See AbstractCLUploadManager._GetLatestContentHash().
    """
    return self._GetLatestContentHash(board=None)

  def SetLatestVPGTargetsHash(self, vpg_targets_hash: str):
    """Sets the latest VPG targets content hash.

    Args:
      vpg_targets_hash: The hash value to set.
    """
    self._SetLatestContentHash(content_hash=vpg_targets_hash, board=None)


class LatestHWIDMainCommit(ndb.Model):
  """The latest processed commit of the HWID repo.

  This is used to check if the payload content should be regenerated.

  Attributes:
    payload_type: The type of CL content. See also CLType.
    commit: The latest processed commit of the HWID repo.
    board: The board that the commit corresponds to.
  """

  payload_type = ndb.StringProperty()
  commit = ndb.StringProperty()
  board = ndb.StringProperty()


class PayloadCLUploadManager(AbstractCLUploadManager):
  """Base CL upload manager for payloads."""

  def __init__(self, ndb_connector: ndbc_module.NDBConnector):
    if self._cl_type not in [
        CLType.HWID_SELECTION_PAYLOAD,
        CLType.VERIFICATION_PAYLOAD,
        CLType.RMAD_FEATURE_ENABLED_DEVICES_PAYLOAD,
    ]:
      raise ValueError(
          f'Invalid CL type for PayloadCLUploadManager, got: {self._cl_type}')
    super().__init__(ndb_connector)

  def ShouldGenerateContent(self, hwid_live_commit: str, board: str,
                            force_generate: bool = False) -> bool:
    """Checks if the content should be generated.

    This function is called before the generation of contents begins to avoid
    unnecessary generation as the process may take a long time.

    Args:
      hwid_live_commit: The latest commit of the HWID repo.
      board: See LatestHWIDMainCommit.board.
      force_generate: Set to True when force to generate the content.
    """
    config = self.cl_upload_config
    if force_generate:
      self._logger.info('Force to generate content for %s.', config.cl_type)
      return True
    if config.disabled:
      self._logger.info(
          'The generation for %s is disabled, skip generating '
          'the content.', config.cl_type)
      return False
    hwid_prev_commit = self.GetLatestHWIDMainCommit(board)
    if hwid_live_commit == hwid_prev_commit:
      self._logger.info(
          'The HWID live commit %s for board %s is already processed, skipped',
          hwid_live_commit, board)
      return False
    return True

  def ShouldCreateCL(self, content_hash: str, board: Optional[str] = None,
                     force_create: bool = False) -> bool:
    """See base class."""
    if board is None:
      raise ValueError('board must be specified')

    if force_create:
      self._logger.info('Force to create CL for %s.',
                        self.cl_upload_config.cl_type)
      return True
    latest_payload_hash = self.GetLatestPayloadHash(board)
    if content_hash == latest_payload_hash:
      self._logger.info('%s hash value is not changed (%s), skip creating CL',
                        self._cl_type, content_hash)
      return False
    return True

  def GetLatestHWIDMainCommit(self, board: str) -> Optional[str]:
    """Gets the latest processed commit of HWID repo.

    Args:
      board: See LatestHWIDMainCommit.board.

    Returns:
      None if the entity does not exist. Otherwise, the latest processed commit
      of HWID repo.
    """
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      entity = LatestHWIDMainCommit.query(
          LatestHWIDMainCommit.payload_type == self._cl_type,
          LatestHWIDMainCommit.board == board).get()
      return entity.commit if entity is not None else None

  def SetLatestHWIDMainCommit(self, commit: str, board: str):
    """Sets the latest processed commit of HWID repo.

    Args:
      commit: See LatestHWIDMainCommit.commit.
      board: See LatestHWIDMainCommit.board.
    """
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      entity = LatestHWIDMainCommit.query(
          LatestHWIDMainCommit.payload_type == self._cl_type,
          LatestHWIDMainCommit.board == board).get()
      if entity is None:
        entity = LatestHWIDMainCommit(payload_type=self._cl_type, board=board)
      entity.commit = commit
      entity.put()

  def GetLatestPayloadHash(self, board: str) -> Optional[str]:
    """Gets the latest payload content hash.

    Args:
      board: See CLUploadFactor.board.

    Returns:
      See AbstractCLUploadManager._GetLatestContentHash().
    """
    return self._GetLatestContentHash(board=board)

  def SetLatestPayloadHash(self, payload_hash: str, board: str):
    """Sets the latest payload content hash.

    Args:
      payload_hash: The hash value to set.
      board: See CLUploadFactor.board.

    Returns:
      See AbstractCLUploadManager._GetLatestContentHash().
    """
    self._SetLatestContentHash(content_hash=payload_hash, board=board)


class VerificationPayloadCLUploadManager(PayloadCLUploadManager):
  """CL upload manager for verification payloads."""
  _cl_type = CLType.VERIFICATION_PAYLOAD


class HWIDSelectionPayloadCLUploadManager(PayloadCLUploadManager):
  """CL upload manager for HWID selection payloads."""
  _cl_type = CLType.HWID_SELECTION_PAYLOAD


class RMADFeatureEnabledDevicesPayloadCLUploadManager(PayloadCLUploadManager):
  """CL upload manager for HWID selection payloads."""
  _cl_type = CLType.RMAD_FEATURE_ENABLED_DEVICES_PAYLOAD
