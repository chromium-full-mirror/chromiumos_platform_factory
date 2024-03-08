# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine.hwid_api_helpers import dlm_product_apis
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.service.appengine import test_utils
from cros.factory.probe_info_service.app_engine import protorpc_utils


_DlmDevice = hwid_api_messages_pb2.DlmDevice
_DlmProduct = hwid_api_messages_pb2.DlmProduct
_UpdateDlmDeviceRequest = hwid_api_messages_pb2.UpdateDlmDeviceRequest
_UpdateDlmDeviceResponse = hwid_api_messages_pb2.UpdateDlmDeviceResponse
_UpdateDlmProductRequest = hwid_api_messages_pb2.UpdateDlmProductRequest
_UpdateDlmProductResponse = hwid_api_messages_pb2.UpdateDlmProductResponse


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

  def testUpdateDlmProduct_CreateNewProduct(self):
    product = _DlmProduct(id=1, board='test_board', model='test_model',
                          product_status=_DlmProduct.SHIPPED, device_id=1)
    req = _UpdateDlmProductRequest(product=product)

    res = self.service.UpdateDlmProduct(req)

    self.assertEqual(res, _UpdateDlmProductResponse(product_id=1))
    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(len(products), 1)

    product = products[0]
    self.assertEqual(product.id, 1)
    self.assertEqual(product.board, 'test_board')
    self.assertEqual(product.model, 'test_model')
    self.assertEqual(product.product_status, _DlmProduct.SHIPPED)
    self.assertEqual(product.device_id, 1)

  def testUpdateDlmProduct_UpdateExistingProduct(self):
    p1 = self._CreateDLMProduct(
        id=1, board='test_board_1', model='test_model_1',
        product_status=_DlmProduct.APPROVED, device_id=1)
    p2 = self._CreateDLMProduct(id=2, board='test_board_2',
                                model='test_model_2',
                                product_status=_DlmProduct.SHIPPED, device_id=2)
    product = _DlmProduct(id=1, board='test_board_3', model='test_model_3',
                          product_status=_DlmProduct.DEVELOPMENT, device_id=3)
    req = _UpdateDlmProductRequest(product=product)

    res = self.service.UpdateDlmProduct(req)

    self.assertEqual(res, _UpdateDlmProductResponse(product_id=1))
    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
      # Entity keys can only be accessed in context.
      p1 = p1.key.get()
      p2 = p2.key.get()
      self.assertCountEqual(res, [p1, p2])

    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'test_board_3')
    self.assertEqual(p1.model, 'test_model_3')
    self.assertEqual(p1.product_status, _DlmProduct.DEVELOPMENT)
    self.assertEqual(p1.device_id, 3)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'test_board_2')
    self.assertEqual(p2.model, 'test_model_2')
    self.assertEqual(p2.product_status, _DlmProduct.SHIPPED)
    self.assertEqual(p2.device_id, 2)

  def testUpdateDlmProduct_MissingRequiredFields(self):
    product = _DlmProduct(id=1)
    req = _UpdateDlmProductRequest(product=product)

    with self.assertRaisesRegex(
        protorpc_utils.ProtoRPCException,
        "Got invalid product data: missing required field 'board'") as ex:
      self.service.UpdateDlmProduct(req)

    self.assertEqual(ex.exception.code,
                     protorpc_utils.RPCCanonicalErrorCode.INVALID_ARGUMENT)

    with self._ndb_connector.CreateClientContext():
      products = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(products, [])

  def testUpdateDlmDevice(self):
    p1 = self._CreateDLMProduct(id=1, board='test_board_1',
                                model='test_model_1', product_status=1,
                                device_id=1)
    p2 = self._CreateDLMProduct(id=2, board='test_board_2',
                                model='test_model_2', product_status=2,
                                device_id=2)
    p3 = self._CreateDLMProduct(id=3, board='test_board_2',
                                model='test_model_2', product_status=3,
                                device_id=2)
    device = _DlmDevice(id=2, board='test_board_3', model='test_model_3')
    req = _UpdateDlmDeviceRequest(device=device)

    res = self.service.UpdateDlmDevice(req)

    self.assertEqual(res, _UpdateDlmDeviceResponse(device_id=2))

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
      # Entity keys can only be accessed in context.
      p1 = p1.key.get()
      p2 = p2.key.get()
      p3 = p3.key.get()
      self.assertCountEqual(res, [p1, p2, p3])

    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'test_board_1')
    self.assertEqual(p1.model, 'test_model_1')
    self.assertEqual(p1.product_status, 1)
    self.assertEqual(p1.device_id, 1)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'test_board_3')
    self.assertEqual(p2.model, 'test_model_3')
    self.assertEqual(p2.product_status, 2)
    self.assertEqual(p2.device_id, 2)

    self.assertEqual(p3.id, 3)
    self.assertEqual(p3.board, 'test_board_3')
    self.assertEqual(p3.model, 'test_model_3')
    self.assertEqual(p3.product_status, 3)
    self.assertEqual(p3.device_id, 2)

  def testUpdateDlmDevice_MissingRequiredFields(self):
    device = _DlmDevice(id=1, model='test_model')
    req = _UpdateDlmDeviceRequest(device=device)

    with self.assertRaisesRegex(
        protorpc_utils.ProtoRPCException,
        "Got invalid device data: missing required field 'board'") as ex:
      self.service.UpdateDlmDevice(req)

    self.assertEqual(ex.exception.code,
                     protorpc_utils.RPCCanonicalErrorCode.INVALID_ARGUMENT)


if __name__ == '__main__':
  unittest.main()
