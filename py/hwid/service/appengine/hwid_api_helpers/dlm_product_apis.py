# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from typing import Sequence

from google.cloud import ndb

from cros.factory.hwid.service.appengine import auth
from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine.hwid_api_helpers import common_helper
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.probe_info_service.app_engine import protorpc_utils


_BatchUpdateDlmProductRequest = (
    hwid_api_messages_pb2.BatchUpdateDlmProductRequest)
_BatchUpdateDlmProductResponse = (
    hwid_api_messages_pb2.BatchUpdateDlmProductResponse)
_UpdateDlmDeviceRequest = hwid_api_messages_pb2.UpdateDlmDeviceRequest
_UpdateDlmDeviceResponse = hwid_api_messages_pb2.UpdateDlmDeviceResponse
_UpdateDlmProductRequest = hwid_api_messages_pb2.UpdateDlmProductRequest
_UpdateDlmProductResponse = hwid_api_messages_pb2.UpdateDlmProductResponse


# yapf: disable
class DLMProductShard(common_helper.HWIDServiceShardBase):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable

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
    updated_product_ids = self._UpdateDLMProducts([product])
    return _UpdateDlmProductResponse(product_id=updated_product_ids[0])

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def BatchUpdateDlmProduct(
      self,
      request: _BatchUpdateDlmProductRequest) -> _BatchUpdateDlmProductResponse:
    """Create or update the product data with DLM product list."""
    products = request.products
    updated_product_ids = self._UpdateDLMProducts(products)
    return _BatchUpdateDlmProductResponse(product_ids=updated_product_ids)

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

    try:
      self._dlm_product_manager.UpdateDLMProductsByDeviceId(
          device.id, device.board.upper(),
          # yapf: disable
          device.model.upper() or None)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    except ndb.exceptions.Error as e:
      raise protorpc_utils.ProtoRPCException(
          protorpc_utils.RPCCanonicalErrorCode.INTERNAL,
          f'Failed to update product data with exception: {e}') from e

    return _UpdateDlmDeviceResponse(device_id=device.id)

  def _UpdateDLMProducts(
      self,
      products: Sequence[hwid_api_messages_pb2.DlmProduct]) -> Sequence[int]:
    """Create or update the product data with DLM product list.

    Args:
      products: The list of product to update or create.

    Returns:
      A list containing id of updated products.

    Raises:
      protorpc_utils.ProtoRPCException: If any of the given products is missing
          required fields.
    """
    dlm_products = []
    for product in products:
      for field in ['id', 'board', 'device_id']:
        if not getattr(product, field):
          raise protorpc_utils.ProtoRPCException(
              protorpc_utils.RPCCanonicalErrorCode.INVALID_ARGUMENT,
              f'Got invalid product data: missing required field {field!r}')
      dlm_products.append(
          dlm_product_data.DLMProduct(id=product.id,
                                      board=product.board.upper(),
                                      model=product.model.upper() or None,
                                      product_status=product.product_status,
                                      device_id=product.device_id))

    try:
      self._dlm_product_manager.UpdateDLMProducts(dlm_products)
    except ndb.exceptions.Error as e:
      raise protorpc_utils.ProtoRPCException(
          protorpc_utils.RPCCanonicalErrorCode.INTERNAL,
          f'Failed to update product data with exception: {e}') from e

    return sorted(product.id for product in dlm_products)
