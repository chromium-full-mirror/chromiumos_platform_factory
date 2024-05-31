# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import datetime
import json
import os
import re

from google.api_core import exceptions as api_exceptions

from cros.factory.bundle_creator.app_engine_v2 import config
from cros.factory.bundle_creator.connector import firestore_connector
from cros.factory.bundle_creator.connector import pubsub_connector
from cros.factory.bundle_creator.connector import storage_connector
from cros.factory.bundle_creator.proto import factorybundle_v2_pb2  # pylint: disable=no-name-in-module
from cros.factory.bundle_creator.utils import allowlist_utils
from cros.factory.bundle_creator.utils import protorpc_utils


IMAGE_ARCHIVE_BUCKET = 'chromeos-image-archive'


class FactoryBundleV2Service(protorpc_utils.ProtoRPCServiceBase):
  SERVICE_DESCRIPTOR = factorybundle_v2_pb2.DESCRIPTOR.services_by_name[
      'FactoryBundleV2Service']

  _REQUEST_FROM_VALUE = 'v2'

  def __init__(self):
    self._firestore_connector = firestore_connector.FirestoreConnector(
        config.GCLOUD_PROJECT)
    self._pubsub_connector = pubsub_connector.PubSubConnector(
        config.GCLOUD_PROJECT)
    self._storage_connector = storage_connector.FactoryBundleStorageConnector(
        config.GCLOUD_PROJECT, config.BUNDLE_BUCKET)
    self._image_archive_storage_connector = storage_connector.StorageConnector(
        config.GCLOUD_PROJECT, IMAGE_ARCHIVE_BUCKET)

  @allowlist_utils.Allowlist(config.ALLOWED_LOAS_PEER_USERNAMES)
  def CreateBundle(
      self, request: factorybundle_v2_pb2.CreateBundleRequest
  ) -> factorybundle_v2_pb2.CreateBundleResponse:
    message = factorybundle_v2_pb2.CreateBundleMessage()
    message.doc_id = self._firestore_connector.CreateUserRequest(
        firestore_connector.CreateBundleRequestInfo.FromCreateBundleRequest(
            request), self._REQUEST_FROM_VALUE)
    message.request.MergeFrom(request)
    self._pubsub_connector.PublishMessage(config.PUBSUB_TOPIC,
                                          message.SerializeToString())

    response = factorybundle_v2_pb2.CreateBundleResponse()
    response.status = response.Status.NO_ERROR
    return response

  @allowlist_utils.Allowlist(config.ALLOWED_LOAS_PEER_USERNAMES)
  def GetBundleInfo(
      self, request: factorybundle_v2_pb2.GetBundleInfoRequest
  ) -> factorybundle_v2_pb2.GetBundleInfoResponse:
    response = factorybundle_v2_pb2.GetBundleInfoResponse()

    storage_bundle_info_mapping = {
        s.metadata.doc_id: s
        for s in self._storage_connector.GetBundleInfosByProject(
            request.project)
    }

    for snapshot in self._firestore_connector.GetUserRequestsByProject(
        request.project):
      status = snapshot.get('status', '')
      bundle_info = factorybundle_v2_pb2.BundleInfo()
      bundle_info.metadata.board = snapshot.get('board', '')
      bundle_info.metadata.project = snapshot.get('project', '')
      bundle_info.metadata.phase = snapshot.get('phase', '')
      bundle_info.metadata.toolkit_version = snapshot.get('toolkit_version', '')
      bundle_info.metadata.test_image_version = snapshot.get(
          'test_image_version', '')
      bundle_info.metadata.release_image_version = snapshot.get(
          'release_image_version', '')
      bundle_info.metadata.firmware_source = snapshot.get('firmware_source', '')
      bundle_info.doc_id = snapshot.get('id', '')
      bundle_info.creator = snapshot.get('email', '')
      bundle_info.status = status
      # The fields with suffix `_time` are `DatetimeWithNanoseconds` objects.
      if 'request_time' in snapshot:
        bundle_info.request_time_sec = datetime.datetime.timestamp(
            snapshot.get('request_time'))
      if 'start_time' in snapshot:
        bundle_info.request_start_time_sec = datetime.datetime.timestamp(
            snapshot.get('start_time'))
      if 'end_time' in snapshot:
        bundle_info.request_end_time_sec = datetime.datetime.timestamp(
            snapshot.get('end_time'))

      if status == firestore_connector.UserRequestStatus.SUCCEEDED.name:
        if bundle_info.doc_id in storage_bundle_info_mapping:
          bundle_info.bundle_created_timestamp_sec = float(
              storage_bundle_info_mapping[
                  bundle_info.doc_id].created_timestamp_sec)
        if 'gs_path' in snapshot:
          gs_path = snapshot.get('gs_path')
          bundle_info.blob_path = re.sub(r'gs://[^/]+/', '', gs_path)
          bundle_info.filename = os.path.basename(bundle_info.blob_path)

      response.bundle_infos.append(bundle_info)

    response.bundle_infos.sort(
        key=lambda b: b.bundle_created_timestamp_sec
        if b.status == firestore_connector.UserRequestStatus.SUCCEEDED.name else
        b.request_time_sec, reverse=True)
    return response

  @allowlist_utils.Allowlist(config.ALLOWED_LOAS_PEER_USERNAMES)
  def DownloadBundle(
      self, request: factorybundle_v2_pb2.DownloadBundleRequest
  ) -> factorybundle_v2_pb2.DownloadBundleResponse:
    response = factorybundle_v2_pb2.DownloadBundleResponse()
    self._storage_connector.GrantReadPermissionToBlob(request.email,
                                                      request.blob_path)
    response.download_link = (
        f'https://storage.cloud.google.com/{config.BUNDLE_BUCKET}/'
        f'{request.blob_path}')
    return response

  @allowlist_utils.Allowlist(config.ALLOWED_LOAS_PEER_USERNAMES)
  def GetBundleErrorMessage(
      self, request: factorybundle_v2_pb2.GetBundleErrorMessageRequest
  ) -> factorybundle_v2_pb2.GetBundleErrorMessageResponse:
    response = factorybundle_v2_pb2.GetBundleErrorMessageResponse()
    snapshot = self._firestore_connector.GetUserRequestDocument(request.doc_id)
    if not snapshot:
      response.content = 'Document doesn\'t exist.'
    elif snapshot.get('project', '') != request.project:
      response.content = 'Permission denied.'
    else:
      response.content = snapshot.get('error_message', '')
    return response

  @allowlist_utils.Allowlist(config.ALLOWED_LOAS_PEER_USERNAMES)
  def ExtractFirmwareInfo(
      self, request: factorybundle_v2_pb2.ExtractFirmwareInfoRequest
  ) -> factorybundle_v2_pb2.ExtractFirmwareInfoResponse:
    self._pubsub_connector.PublishMessage(config.FW_INFO_EXTRACTOR_TOPIC,
                                          request.SerializeToString())
    response = factorybundle_v2_pb2.ExtractFirmwareInfoResponse()
    response.status = (
        factorybundle_v2_pb2.ExtractFirmwareInfoResponse.Status.NO_ERROR)
    return response

  @allowlist_utils.Allowlist(config.ALLOWED_LOAS_PEER_USERNAMES)
  def GetFirmwareInfoPreview(
      self, request: factorybundle_v2_pb2.GetFirmwareInfoPreviewRequest
  ) -> factorybundle_v2_pb2.GetFirmwareInfoPreviewResponse:
    archive_dir = (f'{request.board}-release/R{request.milestone}'
                   f'-{request.version}')
    fw_info_preview = collections.defaultdict(set)

    try:
      cros_config = self._image_archive_storage_connector.ReadFile(
          os.path.join(archive_dir, 'config.yaml'))
      for conf in json.loads(cros_config)['chromeos']['configs']:
        if conf.get('name') != request.project:
          continue
        if 'fingerprint' in conf and 'board' in conf['fingerprint']:
          fw_info_preview['fp-ro-image'].add(conf['fingerprint']['board'])
        if 'sku-id' in conf['identity']:
          fw_info_preview['sku-id'].add(str(conf['identity']['sku-id']))
    except api_exceptions.NotFound:
      # TODO(b/344448755): read sku/fp from other place
      pass

    build_report = self._image_archive_storage_connector.ReadFile(
        os.path.join(archive_dir, 'build_report.json'))
    for report in json.loads(build_report)['config'].get('models', []):
      if report.get('name') != request.project:
        continue
      fw_info_preview['firmware-key-id'].add(report['firmwareKeyId'])
      for version in report.get('versions', []):
        if version.get('kind') == "MODEL_VERSION_KIND_MAIN_READONLY_FIRMWARE":
          fw_info_preview['main-ro-image'].add(version['value'])
        elif version.get('kind') == 'MODEL_VERSION_KIND_EC_FIRMWARE':
          fw_info_preview['ec-ro-image'].add(version['value'])

    response = factorybundle_v2_pb2.GetFirmwareInfoPreviewResponse()
    response.main_ro_image.extend(fw_info_preview['main-ro-image'])
    response.ec_ro_image.extend(fw_info_preview['ec-ro-image'])
    response.fp_ro_image.extend(fw_info_preview['fp-ro-image'])
    response.firmware_key_id.extend(fw_info_preview['firmware-key-id'])
    response.sku_id.extend(fw_info_preview['sku-id'])
    return response
