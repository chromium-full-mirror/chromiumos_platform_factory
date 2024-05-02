# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from cros.factory.hwid.service.appengine import auth
from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine.hwid_api_helpers import common_helper
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.probe_info_service.app_engine import protorpc_utils


_UpdateDlmDeviceRequest = hwid_api_messages_pb2.UpdateDlmDeviceRequest
_UpdateDlmDeviceResponse = hwid_api_messages_pb2.UpdateDlmDeviceResponse
_UpdateDlmProductRequest = hwid_api_messages_pb2.UpdateDlmProductRequest
_UpdateDlmProductResponse = hwid_api_messages_pb2.UpdateDlmProductResponse


class DLMProductShard(common_helper.HWIDServiceShardBase):  # type: ignore #TODO(b/338318729) Fixit!

  def __init__(
      self,
      dlm_product_manager: dlm_product_data.DLMProductManager,
  ):
    self._dlm_product_manager = dlm_product_manager

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def UpdateDlmProduct(
      self, request: _UpdateDlmProductRequest) -> _UpdateDlmProductResponse:
    """Create or update the product data with DLM product data."""
    product = request.product
    for field in ['id', 'board', 'device_id']:
      if not getattr(product, field):
        raise protorpc_utils.ProtoRPCException(
            protorpc_utils.RPCCanonicalErrorCode.INVALID_ARGUMENT,
            f'Got invalid product data: missing required field {field!r}')

    try:
      self._dlm_product_manager.UpdateDLMProduct(
          product.id, board=product.board.upper(),
          model=product.model.upper() or None,
          product_status=product.product_status, device_id=product.device_id)
    except dlm_product_data.InvalidProductError as e:
      raise protorpc_utils.ProtoRPCException(
          protorpc_utils.RPCCanonicalErrorCode.INVALID_ARGUMENT, str(e)) from e

    return _UpdateDlmProductResponse(product_id=product.id)

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def UpdateDlmDevice(
      self, request: _UpdateDlmDeviceRequest) -> _UpdateDlmDeviceResponse:
    """Update the product data with DLM device data."""
    device = request.device
    for field in ['id', 'board']:
      if not getattr(device, field):
        raise protorpc_utils.ProtoRPCException(
            protorpc_utils.RPCCanonicalErrorCode.INVALID_ARGUMENT,
            f'Got invalid device data: missing required field {field!r}')

    self._dlm_product_manager.UpdateDLMProductByDeviceId(
        device.id, device.board.upper(),
        device.model.upper() or None)  # type: ignore #TODO(b/338318729) Fixit!

    return _UpdateDlmDeviceResponse(device_id=device.id)
