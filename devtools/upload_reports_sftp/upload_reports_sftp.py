#!/usr/bin/env python3
#
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
A template Python3 script to compress factory reports, upload report archives
from Factory Server (Umpire) to Google's SFTP server, and check integrity.
"""

import abc
import argparse
import base64
from collections.abc import Sequence
import datetime
import enum
import hashlib
import logging
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
from typing import NoReturn, Optional, Union


# Constants
_DEFAULT_LOG_PATH = 'upload_reports_sftp'
_LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'


class _Status(enum.Enum):
  NO_FILE = enum.auto()
  SUCCESS = enum.auto()
  FAIL = enum.auto()


def _InitLogging(log_file: str) -> None:
  _TryMakeDirs(os.path.dirname(log_file))
  file_handler = logging.FileHandler(log_file)
  file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  logger.handlers = [file_handler, stream_handler]
  logging.info('Initialized logging system')


def _ParseArgument():
  """Parses arguments from the user."""
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description='Upload factory reports to Google\'s SFTP server.')
  parser.add_argument(
      'factory_report_dir', help='The path of factory report directory. '
      'Example: /cros_docker/umpire/<Dome project name>/umpire_data/report')
  parser.add_argument('hostname', help='The SFTP server hostname.')
  parser.add_argument('port', help='The port for the SFTP server.')
  parser.add_argument('account', help='The SFTP server account. Example: '
                      'cpfe-<ODM>')
  parser.add_argument(
      'key_path',
      help='The path to the private key of the SFTP server account. Example: '
      '/home/.ssh/sftp_key')
  parser.add_argument(
      '--target_dir',
      help='The path for the uploaded archives on SFTP server. The path have '
      'to be existed before using this script. Default is None and it '
      'represents root path. Example: /<project name>', default='.')
  parser.add_argument(
      '--log_dir', '-l',
      help='The path to the log directory which will save archives, logs and '
      f'metadata. Default: {_DEFAULT_LOG_PATH}', default=_DEFAULT_LOG_PATH)
  parser.add_argument(
      '--no_hash_check', dest='hash_check', action='store_false',
      help='To reduce network usage or speed up the process, do not download '
      'uploaded files and check the hash value')
  return parser.parse_args()


def _TryMakeDirs(path: str) -> None:
  os.makedirs(path, exist_ok=True)


def _MD5InBase64(file_path: str) -> str:
  """Returns the MD5 hash value of the file in base64.

  Command `gsutil ls -L` shows MD5 hash value in base64 encoding. To debug
  easier, this function aligns with that format.
  """
  md5_hash = hashlib.md5()
  with open(file_path, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
      md5_hash.update(chunk)
  return base64.b64encode(md5_hash.digest()).decode()


class _ReportFinder:
  _DATE_FORMAT = '%Y%m%d'

  def __init__(self, factory_report_dir: str):
    self._factory_report_dir = factory_report_dir

  def FindOneReportDir(self) -> Optional[str]:
    """Detects valid and readied daily reports from the report directory.

    When there are multiple valid daily report directories, only the first one
    is returned.

    Returns:
      The path to the valid directory with factory reports. If there's no valid
      path, return `None`.
    """
    dirs = sorted(os.listdir(self._factory_report_dir))
    for daily_report_dir in dirs:
      if self._IsValidReportDir(daily_report_dir):
        return os.path.join(self._factory_report_dir, daily_report_dir)
    return None

  def _IsValidReportDir(self, daily_report_dir: str) -> bool:
    """Checks if the daily report directory is valid and ready to process.

    The report directory which is created by umpire should follow the format
    'YYYYmmdd'. A report directory is ready if it is created at least 2 days
    prior to the current date.
    """
    if len(daily_report_dir) != 8:
      return False
    try:
      date = datetime.datetime.strptime(daily_report_dir,
                                        self._DATE_FORMAT).date()
    except ValueError:
      return False
    return date <= datetime.date.today() - datetime.timedelta(days=2)


class _IConnection(abc.ABC):

  @abc.abstractmethod
  def SendFile(self, local_path: str, target_path: str) -> bool:
    """Uploads a file to the destination path."""
    return NotImplemented

  @abc.abstractmethod
  def CheckIntegrity(self, local_path: str, target_path: str) -> bool:
    """Checks the file integrity."""
    return NotImplemented


class _SFTP(_IConnection):

  _TARGET_NOT_EXIST_RE = re.compile(r'dest .* No such file or directory', re.M)

  def __init__(self, hostname: str, port: Union[str, int], account: str,
               key_path: str):
    self._hostname = hostname
    self._port = str(port)
    self._account = account
    self._key_path = key_path

  def SendFile(self, local_path, target_path) -> bool:
    logging.info('Uploading %s to %s', local_path, target_path)
    returncode, unused_outs, errs = self._SFTPCommand(
        f'put {local_path} {target_path}')
    if returncode != 0:
      return False
    if self._TARGET_NOT_EXIST_RE.match(errs):
      logging.error(
          'Please use `mkdir` to create target_dir before running this script')
      raise ValueError('No such directory on SFTP server')
    # We can't check if file uploaded successfully, so we need to check the
    # file size on the server.
    returncode, outs, unused_errs = self._SFTPCommand(f'ls -l {target_path}')
    file_size = os.path.getsize(local_path)
    if returncode != 0 or str(file_size) not in outs:
      return False
    logging.info('Uploaded successfully')
    return True

  def CheckIntegrity(self, local_path, target_path) -> bool:
    with tempfile.NamedTemporaryFile(delete=False) as f:
      temp_file = f.name
    try:
      logging.info(
          'Downloading the file %s from server and checking the hash value',
          target_path)
      returncode, unused_outs, unused_errs = self._SFTPCommand(
          f'get {target_path} {temp_file}')
      if returncode != 0:
        return False
      local_hash = _MD5InBase64(local_path)
      target_hash = _MD5InBase64(temp_file)
      logging.info('local hash = %s, target hash = %s', local_hash, target_hash)
      if local_hash != target_hash:
        logging.warning('Does not match!')
        return False
    finally:
      if os.path.exists(temp_file):
        os.unlink(temp_file)
    return True

  def _SFTPCommand(self, command: str) -> tuple[int, str, str]:
    with subprocess.Popen([
        'sftp', '-oStrictHostKeyChecking=no', '-i', self._key_path, '-P',
        self._port, f'{self._account}@{self._hostname}'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding='utf-8') as p:
      outs, errs = p.communicate(command)
    return p.returncode, outs, errs


class _BaseUploader(abc.ABC):

  def __init__(self, connection: _IConnection, log_dir: str, hash_check: bool):
    self._connection = connection
    self._hash_check = hash_check
    self._finished_report_dir = os.path.join(log_dir, 'finished', 'report')

  def SetUp(self) -> None:
    _TryMakeDirs(self._finished_report_dir)

  @abc.abstractmethod
  def Upload(self) -> _Status:
    return NotImplemented

  def _UploadFile(self, local_path: str, remote_path: str) -> bool:
    """Uploads a file to the remote server and does hash check (if needed).

    Returns:
      `False` if failed to upload the file to the remote server, or if hash
      check is needed but failed; otherwise `True`.
    """
    if not self._connection.SendFile(local_path, remote_path):
      return False

    if not self._hash_check:
      return True

    return self._connection.CheckIntegrity(local_path, remote_path)


class _ArchiveUploader(_BaseUploader):
  """Uploader implementation with factory report archiving.

  This uploader compacts factory reports into archives before uploading.
  """

  _ARCHIVE_SIZE_THRESHOLD = 2 * 1024 * 1024 * 1024  # 2 GiB

  def __init__(self, report_finder: _ReportFinder, connection: _IConnection,
               target_dir: str, log_dir: str, hash_check: bool):
    super().__init__(connection, log_dir, hash_check)
    self._target_dir = target_dir
    self._archive_dir = os.path.join(log_dir, 'archive')
    self._finished_archive_dir = os.path.join(log_dir, 'finished', 'archive')
    self._report_finder = report_finder

  def SetUp(self) -> None:
    super().SetUp()
    _TryMakeDirs(self._archive_dir)
    _TryMakeDirs(self._finished_archive_dir)

  def Upload(self) -> _Status:
    produce_status = self._ProduceArchives()
    upload_status = self._UploadArchive()

    if _Status.FAIL in (produce_status, upload_status):
      return _Status.FAIL

    if produce_status == upload_status == _Status.NO_FILE:
      return _Status.NO_FILE

    return _Status.SUCCESS

  def _ProduceArchives(self) -> _Status:
    """Detects valid report directory and archives it.

    This function creates a list of archives for just one day (one directory).
    If an archive is larger than `_ARCHIVE_SIZE_THRESHOLD`, it will produce
    another archive for the remaining files in the directory.

    Returns:
      A `_Status` enum.
    """
    report_dir_found = self._report_finder.FindOneReportDir()
    if not report_dir_found:
      return _Status.NO_FILE
    logging.info('Found valid report directory %s', report_dir_found)
    if self._ArchiveAll(report_dir_found):
      self._CleanUpAfterProduceArchive(report_dir_found)
      return _Status.SUCCESS
    return _Status.FAIL

  def _ArchiveAll(self, dir_to_archive: str) -> bool:
    """Archives a directory to archives and checks their file integrity.

    If the directory is empty, it will not produce any archive. If the directory
    has many reports, it may produce one or more archives.

    Returns:
      `True` if it archives a directory correctly; otherwise `False`.
    """
    archived_list: list[str] = []
    index = 0
    report_day = os.path.basename(dir_to_archive)

    while True:
      archive_path = os.path.join(self._archive_dir,
                                  f'{report_day}-{index}.tar')
      tmp_path = f'{archive_path}.tmp'
      files_added = self._ArchiveOne(dir_to_archive, tmp_path, archived_list)
      if files_added is None:
        os.unlink(tmp_path)
        logging.error('Failed to archive %s', dir_to_archive)
        return False
      if not files_added:
        os.unlink(tmp_path)
        logging.info('Produced %d archives successfully from %s', index,
                     dir_to_archive)
        return True
      # Atomic function if the source and the destination file are on the same
      # file system.
      shutil.move(tmp_path, archive_path)
      logging.info('Produced an archive %s with %d factory reports',
                   archive_path, len(files_added))
      archived_list += files_added
      index += 1

  def _ArchiveOne(self, dir_to_archive: str, archive_path: str,
                  archived_list: Sequence[str]) -> Optional[list[str]]:
    """Archives files to one archive and checks the integrity.

    The archive only allows directories and regular files. If a file is already
    archived previously or the archive already reaches the
    `_ARCHIVE_SIZE_THRESHOLD`, it will skip the file.

    Returns:
      A list of files if they are archived correctly; otherwise `None`.
    """
    archive_size = 0
    files_added: list[str] = []

    def _Filter(tarinfo: tarfile.TarInfo) -> Optional[tarfile.TarInfo]:
      nonlocal archive_size
      if tarinfo.isdir():
        return tarinfo
      # Only allows directory and regular file.
      if not tarinfo.isfile():
        return None
      if tarinfo.name in archived_list:
        return None
      if archive_size >= self._ARCHIVE_SIZE_THRESHOLD:
        return None
      archive_size += tarinfo.size
      files_added.append(tarinfo.name)
      return tarinfo

    try:
      with tarfile.open(archive_path, 'w') as tar:
        tar.add(dir_to_archive, filter=_Filter)

      # Check the tar file integrity. `tarfile.is_tarfile()` cannot detect
      # corrupted content, so here we use `getmembers()` and discard the return
      # value.
      with tarfile.open(archive_path, 'r') as tar:
        tar.getmembers()

      return files_added
    except Exception:
      logging.exception('Failed to archive factory reports')
      return None

  def _CleanUpAfterProduceArchive(self, dir_to_clean: str) -> None:
    dst_dir = os.path.join(self._finished_report_dir,
                           os.path.basename(dir_to_clean))
    shutil.copytree(dir_to_clean, dst_dir, dirs_exist_ok=True)
    shutil.rmtree(dir_to_clean)

  def _UploadArchive(self) -> _Status:
    """Uploads a report archive in the directory to the SFTP server.

    Returns:
      A `_Status` enum.
    """
    files = sorted(os.listdir(self._archive_dir))
    file_name_to_upload = next((f for f in files if not f.endswith('.tmp')),
                               None)
    if not file_name_to_upload:
      return _Status.NO_FILE

    local_path = os.path.join(self._archive_dir, file_name_to_upload)
    target_path = os.path.join(self._target_dir, file_name_to_upload)
    if not self._UploadFile(local_path, target_path):
      return _Status.FAIL

    self._CleanUpAfterUploadArchive(local_path)
    return _Status.SUCCESS

  def _CleanUpAfterUploadArchive(self, archive_to_clean: str) -> None:
    shutil.move(archive_to_clean, self._finished_archive_dir)


def _main() -> NoReturn:
  args = _ParseArgument()

  if not os.access(args.key_path, os.R_OK):
    raise PermissionError(f'Cannot read the private key file: {args.key_path}')
  if not os.access(args.factory_report_dir, os.R_OK | os.W_OK):
    raise PermissionError('Cannot access factory_report_dir: '
                          f'{args.factory_report_dir}')

  log_path = os.path.join(args.log_dir, 'upload_reports_sftp.log')
  _InitLogging(log_path)

  report_finder = _ReportFinder(args.factory_report_dir)
  sftp = _SFTP(args.hostname, args.port, args.account, args.key_path)
  uploader: _BaseUploader = _ArchiveUploader(
      report_finder, sftp, args.target_dir, args.log_dir, args.hash_check)

  uploader.SetUp()
  while True:
    while (upload_result := uploader.Upload()) == _Status.SUCCESS:
      pass

    # If there is no valid report directory and no archive, sleep for a while.
    if upload_result == _Status.NO_FILE:
      sleep_in_sec = 6 * 60 * 60  # 6 hours
      logging.info('There\'s no report/archive to process, sleep %s seconds',
                   sleep_in_sec)
      time.sleep(sleep_in_sec)
    # If it failed to upload, sleep for a minute.
    else:
      sleep_in_sec = 60
      logging.info('Process failed, sleep %s seconds', sleep_in_sec)
      time.sleep(sleep_in_sec)


if __name__ == '__main__':
  _main()
