#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import ast
import re
import unittest

from cros.factory.hwid.service.appengine.data import dlm_product_data
from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module


class DLMProductManagerTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self._ndb_connector = ndbc_module.NDBConnector()
    self._manager = dlm_product_data.DLMProductManager(self._ndb_connector)

  def tearDown(self):
    super().tearDown()
    self._manager.CleanAllForTest()

  def _CreateDLMProduct(self, **kwargs) -> dlm_product_data.DLMProduct:
    entity = dlm_product_data.DLMProduct()

    with self._ndb_connector.CreateClientContext():
      entity.populate(**kwargs)
      entity.put()
    return entity

  def testUpdateDLMProduct_CreateNewProduct(self):
    self._manager.UpdateDLMProduct(1, board='test_board', model='test_model',
                                   product_status=2, device_id=3)

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
    self.assertEqual(len(res), 1)
    self.assertEqual(res[0].id, 1)
    self.assertEqual(res[0].board, 'test_board')
    self.assertEqual(res[0].model, 'test_model')
    self.assertEqual(res[0].product_status, 2)
    self.assertEqual(res[0].device_id, 3)

  def testUpdateDLMProduct_UpdateExistingProduct(self):
    p1 = self._CreateDLMProduct(id=1, board='test_board_1',
                                model='test_model_1', product_status=1,
                                device_id=1)
    p2 = self._CreateDLMProduct(id=2, board='test_board_2',
                                model='test_model_2', product_status=2,
                                device_id=2)

    self._manager.UpdateDLMProduct(1, board='test_board_3',
                                   model='test_model_3', product_status=3,
                                   device_id=3)

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
      # Entity keys can only be accessed in context.
      p1 = p1.key.get()
      p2 = p2.key.get()
      self.assertCountEqual(res, [p1, p2])

    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'test_board_3')
    self.assertEqual(p1.model, 'test_model_3')
    self.assertEqual(p1.product_status, 3)
    self.assertEqual(p1.device_id, 3)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'test_board_2')
    self.assertEqual(p2.model, 'test_model_2')
    self.assertEqual(p2.product_status, 2)
    self.assertEqual(p2.device_id, 2)

  def testUpdateDLMProduct_MissingRequiredFields(self):
    self.assertRaisesRegex(
        dlm_product_data.InvalidProductError,
        "Failed to update invalid product data {'id': 1} with exception: "
        'Entity has uninitialized properties: board, device_id, product_status',
        self._manager.UpdateDLMProduct, 1)

  def testUpdateDLMProduct_InvalidFieldValue(self):
    kwargs = {
        'board': 'test_board',
        'model': 'test_model',
        'product_status': 'invalid_value',
        'device_id': 1
    }
    error_re = re.compile(r'Failed to update invalid product data '
                          r"({[\w\'\:\,\s]+}) with exception: Expected integer,"
                          r" got 'invalid_value'")

    with self.assertRaisesRegex(dlm_product_data.InvalidProductError,
                                error_re) as e:
      self._manager.UpdateDLMProduct(1, **kwargs)

    invalid_args = error_re.search(str(e.exception)).group(1)  # type: ignore #TODO(b/338318729) Fixit!
    invalid_args = ast.literal_eval(invalid_args)
    self.assertEqual(invalid_args, {
        'id': 1,
        **kwargs
    })

  def testUpdateDLMProduct_NonExistentField(self):
    kwargs = {
        'non_existent_field': 1
    }
    error_re = re.compile(r'Failed to update invalid product data '
                          r"({[\w\'\:\,\s]+}) with exception: type object "
                          r"'DLMProduct' has no attribute 'non_existent_field'")

    with self.assertRaisesRegex(dlm_product_data.InvalidProductError,
                                error_re) as e:
      self._manager.UpdateDLMProduct(1, **kwargs)

    invalid_args = error_re.search(str(e.exception)).group(1)  # type: ignore #TODO(b/338318729) Fixit!
    invalid_args = ast.literal_eval(invalid_args)
    self.assertEqual(invalid_args, {
        'id': 1,
        **kwargs
    })

  def testGetDLMProductsByBoards(self):
    p1 = self._CreateDLMProduct(id=1, board='test_board_1',
                                model='test_model_1', product_status=1,
                                device_id=1)
    p2 = self._CreateDLMProduct(id=2, board='test_board_2',
                                model='test_model_2', product_status=2,
                                device_id=2)
    p3 = self._CreateDLMProduct(id=3, board='test_board_2',
                                model='test_model_2', product_status=3,
                                device_id=2)
    self._CreateDLMProduct(id=4, board='test_board_3', model='test_model_3',
                           product_status=1, device_id=3)

    res = self._manager.GetDLMProductsByBoards(['test_board_1', 'test_board_2'])

    with self._ndb_connector.CreateClientContext():
      # Entity keys can only be accessed in context.
      self.assertCountEqual(res, [p1, p2, p3])

  def testGetDLMProductsByBoards_NoMatchingResult(self):
    self._CreateDLMProduct(id=1, board='test_board_1', model='test_model_1',
                           product_status=1, device_id=1)
    self._CreateDLMProduct(id=2, board='test_board_2', model='test_model_2',
                           product_status=2, device_id=2)

    res = self._manager.GetDLMProductsByBoards(['test_board_3'])

    self.assertEqual(res, [])

  def testUpdateDLMProductByDeviceId(self):
    p1 = self._CreateDLMProduct(id=1, board='test_board_1',
                                model='test_model_1', product_status=1,
                                device_id=1)
    p2 = self._CreateDLMProduct(id=2, board='test_board_2',
                                model='test_model_2', product_status=2,
                                device_id=2)
    p3 = self._CreateDLMProduct(id=3, board='test_board_2',
                                model='test_model_2', product_status=3,
                                device_id=2)

    self._manager.UpdateDLMProductByDeviceId(2, 'test_board_3', 'test_model_3')

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


if __name__ == '__main__':
  unittest.main()
