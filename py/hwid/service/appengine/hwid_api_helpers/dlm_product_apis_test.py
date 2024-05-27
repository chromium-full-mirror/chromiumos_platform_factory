# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from google.api_core import exceptions as google_api_exceptions
from google.cloud import ndb

from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine.hwid_api_helpers import dlm_product_apis
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import test_utils
from cros.factory.probe_info_service.app_engine import protorpc_utils


_BatchUpdateDlmProductRequest = (
    hwid_api_messages_pb2.BatchUpdateDlmProductRequest)
_BatchUpdateDlmProductResponse = (
    hwid_api_messages_pb2.BatchUpdateDlmProductResponse)
_DeviceType = hwid_api_messages_pb2.DeviceType
_DlmDevice = hwid_api_messages_pb2.DlmDevice
_DlmProduct = hwid_api_messages_pb2.DlmProduct
_DlmDeviceUpdateResult = hwid_api_messages_pb2.DlmDeviceUpdateResult
_DlmProductUpdateResult = hwid_api_messages_pb2.DlmProductUpdateResult
_UpdateDlmDeviceRequest = hwid_api_messages_pb2.UpdateDlmDeviceRequest
_UpdateDlmDeviceResponse = hwid_api_messages_pb2.UpdateDlmDeviceResponse


class DLMProductShardTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._modules = test_utils.FakeModuleCollection()
    self._ndb_connector = self._modules.ndb_connector
    self.service = dlm_product_apis.DLMProductShard(
        self._modules.fake_dlm_product_manager)

  def tearDown(self):
    super().tearDown()
    self._modules.ClearAll()

  def _CreateDLMProduct(self, **kwargs) -> dlm_product_data.DLMProduct:
    entity = dlm_product_data.DLMProduct()

    with self._ndb_connector.CreateClientContext():
      entity.populate(**kwargs)
      entity.put()
    return entity

  def testBatchUpdateDlmProduct_CreateNewProducts(self):
    p1 = _DlmProduct(id=1, board='test_board_1', model='test_model_1',
                     product_status=_DlmProduct.SHIPPED, device_id=1,
                     device_type=_DeviceType.DEVICE)
    p2 = _DlmProduct(id=2, board='test_board_2', model='test_model_2',
                     product_status=_DlmProduct.DEVELOPMENT, device_id=2,
                     device_type=_DeviceType.DEVICE)
    req = _BatchUpdateDlmProductRequest(products=[p1, p2])

    res = self.service.BatchUpdateDlmProduct(req)

    self.assertEqual(
        res,
        _BatchUpdateDlmProductResponse(
            product_ids=[1, 2], update_results=[
                _DlmProductUpdateResult(
                    product_id=1, result_type=_DlmProductUpdateResult.SUCCESS),
                _DlmProductUpdateResult(
                    product_id=2, result_type=_DlmProductUpdateResult.SUCCESS)
            ]))
    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(len(products), 2)

    p1 = products[0]
    p2 = products[1]
    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'TEST_BOARD_1')
    self.assertEqual(p1.model, 'TEST_MODEL_1')
    self.assertEqual(p1.product_status, _DlmProduct.SHIPPED)
    self.assertEqual(p1.device_id, 1)
    self.assertEqual(p1.device_type, _DeviceType.DEVICE)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'TEST_BOARD_2')
    self.assertEqual(p2.model, 'TEST_MODEL_2')
    self.assertEqual(p2.product_status, _DlmProduct.DEVELOPMENT)
    self.assertEqual(p2.device_id, 2)
    self.assertEqual(p2.device_type, _DeviceType.DEVICE)

  def testBatchUpdateDlmProduct_UpdateExistingProducts(self):
    p1 = self._CreateDLMProduct(id=1, board='TEST_BOARD_1',
                                model='TEST_MODEL_1',
                                product_status=_DlmProduct.APPROVED,
                                device_id=1, device_type=_DeviceType.DEVICE)
    p2 = self._CreateDLMProduct(id=2, board='TEST_BOARD_2',
                                model='TEST_MODEL_2',
                                product_status=_DlmProduct.SHIPPED, device_id=2,
                                device_type=_DeviceType.DEVICE)
    self._CreateDLMProduct(id=3, board='TEST_BOARD_3', model='TEST_MODEL_3',
                           product_status=_DlmProduct.DEVELOPMENT, device_id=3,
                           device_type=_DeviceType.DEVICE)
    updated_p1 = _DlmProduct(id=1, board='test_board_1', model='test_model_1',
                             product_status=_DlmProduct.DEVELOPMENT,
                             device_id=1,
                             device_type=_DeviceType.REFERENCE_BOARD)
    updated_p3 = _DlmProduct(id=3, board='test_board_4', model='test_model_4',
                             product_status=_DlmProduct.ON_HOLD, device_id=4,
                             device_type=_DeviceType.REFERENCE_BOARD)
    req = _BatchUpdateDlmProductRequest(products=[updated_p1, updated_p3])

    res = self.service.BatchUpdateDlmProduct(req)

    self.assertEqual(
        res,
        _BatchUpdateDlmProductResponse(
            product_ids=[1, 3], update_results=[
                _DlmProductUpdateResult(
                    product_id=1, result_type=_DlmProductUpdateResult.SUCCESS),
                _DlmProductUpdateResult(
                    product_id=3, result_type=_DlmProductUpdateResult.SUCCESS)
            ]))
    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(len(products), 3)

    p1 = products[0]
    p2 = products[1]
    p3 = products[2]
    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'TEST_BOARD_1')
    self.assertEqual(p1.model, 'TEST_MODEL_1')
    self.assertEqual(p1.product_status, _DlmProduct.DEVELOPMENT)
    self.assertEqual(p1.device_id, 1)
    self.assertEqual(p1.device_type, _DeviceType.REFERENCE_BOARD)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'TEST_BOARD_2')
    self.assertEqual(p2.model, 'TEST_MODEL_2')
    self.assertEqual(p2.product_status, _DlmProduct.SHIPPED)
    self.assertEqual(p2.device_id, 2)
    self.assertEqual(p2.device_type, _DeviceType.DEVICE)

    self.assertEqual(p3.id, 3)
    self.assertEqual(p3.board, 'TEST_BOARD_4')
    self.assertEqual(p3.model, 'TEST_MODEL_4')
    self.assertEqual(p3.product_status, _DlmProduct.ON_HOLD)
    self.assertEqual(p3.device_id, 4)
    self.assertEqual(p3.device_type, _DeviceType.REFERENCE_BOARD)

  def testBatchUpdateDlmProduct_UpdateExistingAndCreateNewProducts(self):
    self._CreateDLMProduct(id=1, board='TEST_BOARD_1', model='TEST_MODEL_1',
                           product_status=_DlmProduct.APPROVED, device_id=1,
                           device_type=_DeviceType.DEVICE)
    self._CreateDLMProduct(id=2, board='TEST_BOARD_2', model='TEST_MODEL_2',
                           product_status=_DlmProduct.SHIPPED, device_id=2,
                           device_type=_DeviceType.DEVICE)
    self._CreateDLMProduct(id=3, board='TEST_BOARD_3', model='TEST_MODEL_3',
                           product_status=_DlmProduct.DEVELOPMENT, device_id=3,
                           device_type=_DeviceType.DEVICE)
    updated_p1 = _DlmProduct(id=1, board='test_board_1', model='test_model_1',
                             product_status=_DlmProduct.DEVELOPMENT,
                             device_id=1,
                             device_type=_DeviceType.REFERENCE_BOARD)
    updated_p3 = _DlmProduct(id=3, board='test_board_4', model='test_model_4',
                             product_status=_DlmProduct.ON_HOLD, device_id=4,
                             device_type=_DeviceType.REFERENCE_BOARD)
    p4 = _DlmProduct(id=4, board='test_board_4', model='test_model_4',
                     product_status=_DlmProduct.APPROVED, device_id=4,
                     device_type=_DeviceType.DEVICE)
    req = _BatchUpdateDlmProductRequest(products=[updated_p1, updated_p3, p4])

    res = self.service.BatchUpdateDlmProduct(req)

    self.assertEqual(
        res,
        _BatchUpdateDlmProductResponse(
            product_ids=[1, 3, 4], update_results=[
                _DlmProductUpdateResult(
                    product_id=1, result_type=_DlmProductUpdateResult.SUCCESS),
                _DlmProductUpdateResult(
                    product_id=3, result_type=_DlmProductUpdateResult.SUCCESS),
                _DlmProductUpdateResult(
                    product_id=4, result_type=_DlmProductUpdateResult.SUCCESS)
            ]))
    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(len(products), 4)

    p1 = products[0]
    p2 = products[1]
    p3 = products[2]
    p4 = products[3]
    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'TEST_BOARD_1')
    self.assertEqual(p1.model, 'TEST_MODEL_1')
    self.assertEqual(p1.product_status, _DlmProduct.DEVELOPMENT)
    self.assertEqual(p1.device_id, 1)
    self.assertEqual(p1.device_type, _DeviceType.REFERENCE_BOARD)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'TEST_BOARD_2')
    self.assertEqual(p2.model, 'TEST_MODEL_2')
    self.assertEqual(p2.product_status, _DlmProduct.SHIPPED)
    self.assertEqual(p2.device_id, 2)
    self.assertEqual(p2.device_type, _DeviceType.DEVICE)

    self.assertEqual(p3.id, 3)
    self.assertEqual(p3.board, 'TEST_BOARD_4')
    self.assertEqual(p3.model, 'TEST_MODEL_4')
    self.assertEqual(p3.product_status, _DlmProduct.ON_HOLD)
    self.assertEqual(p3.device_id, 4)
    self.assertEqual(p3.device_type, _DeviceType.REFERENCE_BOARD)

    self.assertEqual(p4.id, 4)
    self.assertEqual(p4.board, 'TEST_BOARD_4')
    self.assertEqual(p4.model, 'TEST_MODEL_4')
    self.assertEqual(p4.product_status, _DlmProduct.APPROVED)
    self.assertEqual(p4.device_id, 4)
    self.assertEqual(p4.device_type, _DeviceType.DEVICE)

  def testBatchUpdateDlmProduct_MissingRequiredFields(self):
    p1 = _DlmProduct(id=1, board='test_board_1', model='test_model_1',
                     product_status=_DlmProduct.SHIPPED, device_id=1,
                     device_type=_DeviceType.DEVICE)
    p2 = _DlmProduct()
    req = _BatchUpdateDlmProductRequest(products=[p1, p2])

    res = self.service.BatchUpdateDlmProduct(req)
    self.assertEqual(
        res,
        _BatchUpdateDlmProductResponse(
            product_ids=[0, 1], update_results=[
                _DlmProductUpdateResult(
                    result_type=_DlmProductUpdateResult.INVALID_DATA,
                    error_msg="Missing required field 'id'"),
                _DlmProductUpdateResult(
                    product_id=1, result_type=_DlmProductUpdateResult.SUCCESS)
            ]))

    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(len(products), 1)
    p1 = products[0]
    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'TEST_BOARD_1')
    self.assertEqual(p1.model, 'TEST_MODEL_1')
    self.assertEqual(p1.product_status, _DlmProduct.SHIPPED)
    self.assertEqual(p1.device_id, 1)
    self.assertEqual(p1.device_type, _DeviceType.DEVICE)

  @mock.patch.object(dlm_product_data.DLMProductManager, 'UpdateDLMProducts')
  def testBatchUpdateDlmProduct_NDBError(self, mock_update_dlm_products):
    p1 = _DlmProduct(id=1, board='test_board_1', model='test_model_1',
                     product_status=_DlmProduct.SHIPPED, device_id=1,
                     device_type=_DeviceType.DEVICE)
    p2 = _DlmProduct(id=2, board='test_board_2', model='test_model_2',
                     product_status=_DlmProduct.DEVELOPMENT, device_id=2,
                     device_type=_DeviceType.DEVICE)
    req = _BatchUpdateDlmProductRequest(products=[p1, p2])
    mock_update_dlm_products.side_effect = ndb.exceptions.BadValueError(
        'Bad Value Error')

    res = self.service.BatchUpdateDlmProduct(req)
    self.assertEqual(
        res,
        _BatchUpdateDlmProductResponse(
            product_ids=[1, 2], update_results=[
                _DlmProductUpdateResult(
                    product_id=1,
                    result_type=_DlmProductUpdateResult.UNKNOWN_ERROR,
                    error_msg='Bad Value Error'),
                _DlmProductUpdateResult(
                    product_id=2,
                    result_type=_DlmProductUpdateResult.UNKNOWN_ERROR,
                    error_msg='Bad Value Error')
            ]))

    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(products, [])

  @mock.patch.object(dlm_product_data.DLMProductManager, 'UpdateDLMProducts')
  def testBatchUpdateDlmProduct_GoogleAPIError(self, mock_update_dlm_products):
    p1 = _DlmProduct(id=1, board='test_board_1', model='test_model_1',
                     product_status=_DlmProduct.SHIPPED, device_id=1,
                     device_type=_DeviceType.DEVICE)
    req = _BatchUpdateDlmProductRequest(products=[p1])
    mock_update_dlm_products.side_effect = google_api_exceptions.GoogleAPIError(
        'Google API Error')

    with self.assertRaisesRegex(
        protorpc_utils.ProtoRPCException,
        "Failed to update product data with exception: Google API Error") as ex:
      self.service.BatchUpdateDlmProduct(req)

    self.assertEqual(ex.exception.code,
                     protorpc_utils.RPCCanonicalErrorCode.INTERNAL)

    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(products, [])

  def testUpdateDlmDevice(self):
    p1 = self._CreateDLMProduct(id=1, board='TEST_BOARD_1',
                                model='TEST_MODEL_1', product_status=1,
                                device_id=1, device_type=_DeviceType.DEVICE)
    p2 = self._CreateDLMProduct(id=2, board='TEST_BOARD_2',
                                model='TEST_MODEL_2', product_status=2,
                                device_id=2, device_type=_DeviceType.DEVICE)
    p3 = self._CreateDLMProduct(id=3, board='TEST_BOARD_2',
                                model='TEST_MODEL_2', product_status=3,
                                device_id=2, device_type=_DeviceType.DEVICE)
    device = _DlmDevice(id=2, board='test_board_3', model='test_model_3',
                        type=_DeviceType.REFERENCE_BOARD)
    req = _UpdateDlmDeviceRequest(device=device)

    res = self.service.UpdateDlmDevice(req)

    self.assertEqual(
        res,
        _UpdateDlmDeviceResponse(
            device_id=2, update_result=_DlmDeviceUpdateResult(
                device_id=2, result_type=_DlmDeviceUpdateResult.SUCCESS)))

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
      # Entity keys can only be accessed in context.
      p1 = p1.key.get()
      p2 = p2.key.get()
      p3 = p3.key.get()
      self.assertCountEqual(res, [p1, p2, p3])

    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'TEST_BOARD_1')
    self.assertEqual(p1.model, 'TEST_MODEL_1')
    self.assertEqual(p1.product_status, 1)
    self.assertEqual(p1.device_id, 1)
    self.assertEqual(p1.device_type, _DeviceType.DEVICE)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'TEST_BOARD_3')
    self.assertEqual(p2.model, 'TEST_MODEL_3')
    self.assertEqual(p2.product_status, 2)
    self.assertEqual(p2.device_id, 2)
    self.assertEqual(p2.device_type, _DeviceType.REFERENCE_BOARD)

    self.assertEqual(p3.id, 3)
    self.assertEqual(p3.board, 'TEST_BOARD_3')
    self.assertEqual(p3.model, 'TEST_MODEL_3')
    self.assertEqual(p3.product_status, 3)
    self.assertEqual(p3.device_id, 2)
    self.assertEqual(p3.device_type, _DeviceType.REFERENCE_BOARD)

  def testUpdateDlmDevice_MissingRequiredFields(self):
    device = _DlmDevice(id=1, model='test_model')
    req = _UpdateDlmDeviceRequest(device=device)

    res = self.service.UpdateDlmDevice(req)

    self.assertEqual(
        res,
        _UpdateDlmDeviceResponse(
            device_id=1, update_result=_DlmDeviceUpdateResult(
                device_id=1, result_type=_DlmDeviceUpdateResult.INVALID_DATA,
                error_msg="Missing required field 'board'")))

  @mock.patch.object(dlm_product_data.DLMProductManager,
                     'UpdateDLMProductsByDeviceId')
  def testUpdateDlmDevice_NDBError(self, mock_update_dlm_products_by_device_id):
    p1 = self._CreateDLMProduct(id=1, board='TEST_BOARD_1',
                                model='TEST_MODEL_1', product_status=1,
                                device_id=1, device_type=_DeviceType.DEVICE)
    device = _DlmDevice(id=1, board='test_board_2', model='test_model_2')
    req = _UpdateDlmDeviceRequest(device=device)
    mock_update_dlm_products_by_device_id.side_effect = (
        ndb.exceptions.BadValueError('Bad Value Error'))

    res = self.service.UpdateDlmDevice(req)

    self.assertEqual(
        res,
        _UpdateDlmDeviceResponse(
            device_id=1, update_result=_DlmDeviceUpdateResult(
                device_id=1, result_type=_DlmDeviceUpdateResult.UNKNOWN_ERROR,
                error_msg='Bad Value Error')))

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
      # Entity keys can only be accessed in context.
      p1 = p1.key.get()
      self.assertCountEqual(res, [p1])

    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'TEST_BOARD_1')
    self.assertEqual(p1.model, 'TEST_MODEL_1')
    self.assertEqual(p1.product_status, 1)
    self.assertEqual(p1.device_id, 1)

  @mock.patch.object(dlm_product_data.DLMProductManager,
                     'UpdateDLMProductsByDeviceId')
  def testUpdateDlmDevice_GoogleAPIError(self,
                                         mock_update_dlm_products_by_device_id):
    p1 = self._CreateDLMProduct(id=1, board='TEST_BOARD_1',
                                model='TEST_MODEL_1', product_status=1,
                                device_id=1, device_type=_DeviceType.DEVICE)
    device = _DlmDevice(id=1, board='test_board_2', model='test_model_2')
    req = _UpdateDlmDeviceRequest(device=device)
    mock_update_dlm_products_by_device_id.side_effect = (
        google_api_exceptions.GoogleAPIError('Google API Error'))

    with self.assertRaisesRegex(
        protorpc_utils.ProtoRPCException,
        "Failed to update product data with exception: Google API Error") as ex:
      self.service.UpdateDlmDevice(req)

    self.assertEqual(ex.exception.code,
                     protorpc_utils.RPCCanonicalErrorCode.INTERNAL)

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
      # Entity keys can only be accessed in context.
      p1 = p1.key.get()
      self.assertCountEqual(res, [p1])

    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'TEST_BOARD_1')
    self.assertEqual(p1.model, 'TEST_MODEL_1')
    self.assertEqual(p1.product_status, 1)
    self.assertEqual(p1.device_id, 1)


if __name__ == '__main__':
  unittest.main()
