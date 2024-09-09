# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
from typing import Sequence

from google.api_core import exceptions as google_api_exceptions
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
_DlmProductUpdateResult = hwid_api_messages_pb2.DlmProductUpdateResult
_DlmDeviceUpdateResult = hwid_api_messages_pb2.DlmDeviceUpdateResult
_UpdateDlmDeviceRequest = hwid_api_messages_pb2.UpdateDlmDeviceRequest
_UpdateDlmDeviceResponse = hwid_api_messages_pb2.UpdateDlmDeviceResponse


class DLMProductShard(common_helper.HWIDServiceShardBase):

  def __init__(
      self,
      dlm_product_manager: dlm_product_data.DLMProductManager,
  ):
    self._dlm_product_manager = dlm_product_manager

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def BatchUpdateDlmProduct(
      self,
      request: _BatchUpdateDlmProductRequest) -> _BatchUpdateDlmProductResponse:
    """Create or update the product data with DLM product list."""
    products = request.products
    update_results = self._UpdateDLMProducts(products)
    return _BatchUpdateDlmProductResponse(
        product_ids=[res.product_id for res in update_results],
        update_results=update_results)

  @protorpc_utils.ProtoRPCServiceMethod
  @auth.RpcCheck
  def UpdateDlmDevice(
      self, request: _UpdateDlmDeviceRequest) -> _UpdateDlmDeviceResponse:
    """Update the product data with DLM device data."""
    device = request.device
    for field in ['id', 'board']:
      if not getattr(device, field):
        return _UpdateDlmDeviceResponse(
            device_id=device.id, update_result=_DlmDeviceUpdateResult(
                device_id=device.id,
                result_type=_DlmDeviceUpdateResult.ResultType.INVALID_DATA,
                error_msg=f'Missing required field {field!r}'))
    dlm_device = dlm_product_data.DLMDevice(
        id=device.id,
        board=device.board.upper(),
        model=device.model.upper() or None,
        device_type=device.type,
        factory_branch=device.factory_branch or None,
    )

    try:
      self._dlm_product_manager.UpdateDLMDevice(dlm_device)
      self._dlm_product_manager.UpdateDLMProductsByDeviceId(
          device.id, device.board.upper(),
          device.model.upper() or None, device.type)
    except ndb.exceptions.Error as e:
      logging.error('Failed to update product data with exception: %s', e)
      return _UpdateDlmDeviceResponse(
          device_id=device.id, update_result=_DlmDeviceUpdateResult(
              device_id=device.id,
              result_type=_DlmDeviceUpdateResult.ResultType.UNKNOWN_ERROR,
              error_msg=str(e)))
    except google_api_exceptions.GoogleAPIError as e:
      # Raise an exception to trigger the client to retry.
      raise protorpc_utils.ProtoRPCException(
          protorpc_utils.RPCCanonicalErrorCode.INTERNAL,
          f'Failed to update product data with exception: {e}') from e

    return _UpdateDlmDeviceResponse(
        device_id=device.id, update_result=_DlmDeviceUpdateResult(
            device_id=device.id,
            result_type=_DlmDeviceUpdateResult.ResultType.SUCCESS))

  def _UpdateDLMProducts(
      self, products: Sequence[hwid_api_messages_pb2.DlmProduct]
  ) -> Sequence[_DlmProductUpdateResult]:
    """Create or update the product data with DLM product list.

    Args:
      products: The list of product to update or create.

    Returns:
      A list of update result.

    Raises:
      protorpc_utils.ProtoRPCException: If the Datastore query fails.
    """
    dlm_products = []
    update_results = []
    for product in products:
      for field in ['id', 'board', 'device_id']:
        if not getattr(product, field):
          update_results.append(
              _DlmProductUpdateResult(
                  product_id=product.id,
                  result_type=_DlmProductUpdateResult.ResultType.INVALID_DATA,
                  error_msg=f'Missing required field {field!r}'))
          break
      else:
        dlm_products.append(
            dlm_product_data.DLMProduct(
                id=product.id, board=product.board.upper(),
                model=product.model.upper() or None,
                product_status=product.product_status,
                device_id=product.device_id, device_type=product.device_type))
        update_results.append(
            _DlmProductUpdateResult(
                product_id=product.id,
                result_type=_DlmProductUpdateResult.ResultType.SUCCESS))

    if dlm_products:
      try:
        self._dlm_product_manager.UpdateDLMProducts(dlm_products)
      except ndb.exceptions.Error as e:
        logging.error('Failed to update product data with exception: %s', e)
        update_results = [
            _DlmProductUpdateResult(
                product_id=product.id,
                result_type=_DlmProductUpdateResult.ResultType.UNKNOWN_ERROR,
                error_msg=str(e)) for product in products
        ]
      except google_api_exceptions.GoogleAPIError as e:
        # Raise an exception to trigger the client to retry.
        raise protorpc_utils.ProtoRPCException(
            protorpc_utils.RPCCanonicalErrorCode.INTERNAL,
            f'Failed to update product data with exception: {e}') from e

    update_results.sort(key=lambda x: x.product_id or 0)
    return update_results
