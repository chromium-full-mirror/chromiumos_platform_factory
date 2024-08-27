#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from google.cloud import ndb

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
      entity.key = ndb.Key(entity.ENTITY_KIND, kwargs['id'])
      entity.put()
    return entity

  def _CreateDLMDevice(self, **kwargs) -> dlm_product_data.DLMDevice:
    entity = dlm_product_data.DLMDevice()

    with self._ndb_connector.CreateClientContext():
      entity.populate(**kwargs)
      entity.key = ndb.Key(entity.ENTITY_KIND, kwargs['id'])
      entity.put()
    return entity

  def testUpdateDLMProducts_CreateNewProducts(self):
    product1 = dlm_product_data.DLMProduct(
        id=1, board='test_board_1', model='test_model_1', product_status=1,
        device_id=1, device_type=1)
    product2 = dlm_product_data.DLMProduct(
        id=2, board='test_board_2', model='test_model_2', product_status=2,
        device_id=2, device_type=2)

    self._manager.UpdateDLMProducts(products=[product1, product2])

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query(order_by=['id']))
      self.assertEqual(len(res), 2)
      # Entity keys can only be accessed in context.
      self.assertEqual(res[0].key, ndb.Key('DLMProduct', 1))
      self.assertEqual(res[1].key, ndb.Key('DLMProduct', 2))

    self.assertEqual(res[0].id, 1)
    self.assertEqual(res[0].board, 'test_board_1')
    self.assertEqual(res[0].model, 'test_model_1')
    self.assertEqual(res[0].product_status, 1)
    self.assertEqual(res[0].device_id, 1)
    self.assertEqual(res[0].device_type, 1)

    self.assertEqual(res[1].id, 2)
    self.assertEqual(res[1].board, 'test_board_2')
    self.assertEqual(res[1].model, 'test_model_2')
    self.assertEqual(res[1].product_status, 2)
    self.assertEqual(res[1].device_id, 2)
    self.assertEqual(res[1].device_type, 2)

  def testUpdateDLMProducts_UpdateExistingProducts(self):
    self._CreateDLMProduct(id=1, board='test_board_1', model='test_model_1',
                           product_status=1, device_id=1, device_type=1)
    self._CreateDLMProduct(id=2, board='test_board_2', model='test_model_2',
                           product_status=2, device_id=2, device_type=1)
    self._CreateDLMProduct(id=3, board='test_board_3', model='test_model_3',
                           product_status=3, device_id=3, device_type=1)
    updated_p2 = dlm_product_data.DLMProduct(
        id=2, board='test_board_4', model='test_model_4', product_status=4,
        device_id=4, device_type=2)
    updated_p3 = dlm_product_data.DLMProduct(
        id=3, board='test_board_5', model='test_model_5', product_status=5,
        device_id=5, device_type=2)

    self._manager.UpdateDLMProducts(products=[updated_p2, updated_p3])

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query(order_by=['id']))
      self.assertEqual(len(res), 3)
      # Entity keys can only be accessed in context.
      self.assertEqual(res[0].key, ndb.Key('DLMProduct', 1))
      self.assertEqual(res[1].key, ndb.Key('DLMProduct', 2))
      self.assertEqual(res[2].key, ndb.Key('DLMProduct', 3))

    self.assertEqual(res[0].id, 1)
    self.assertEqual(res[0].board, 'test_board_1')
    self.assertEqual(res[0].model, 'test_model_1')
    self.assertEqual(res[0].product_status, 1)
    self.assertEqual(res[0].device_id, 1)
    self.assertEqual(res[0].device_type, 1)

    self.assertEqual(res[1].id, 2)
    self.assertEqual(res[1].board, 'test_board_4')
    self.assertEqual(res[1].model, 'test_model_4')
    self.assertEqual(res[1].product_status, 4)
    self.assertEqual(res[1].device_id, 4)
    self.assertEqual(res[1].device_type, 2)

    self.assertEqual(res[2].id, 3)
    self.assertEqual(res[2].board, 'test_board_5')
    self.assertEqual(res[2].model, 'test_model_5')
    self.assertEqual(res[2].product_status, 5)
    self.assertEqual(res[2].device_id, 5)
    self.assertEqual(res[2].device_type, 2)

  def testUpdateDLMProducts_UpdateExistingAndCreateNewProducts(self):
    self._CreateDLMProduct(id=1, board='test_board_1', model='test_model_1',
                           product_status=1, device_id=1, device_type=1)
    self._CreateDLMProduct(id=2, board='test_board_2', model='test_model_2',
                           product_status=2, device_id=2, device_type=1)
    self._CreateDLMProduct(id=3, board='test_board_3', model='test_model_3',
                           product_status=3, device_id=3, device_type=1)
    updated_p2 = dlm_product_data.DLMProduct(
        id=2, board='test_board_4', model='test_model_4', product_status=4,
        device_id=4, device_type=2)
    updated_p3 = dlm_product_data.DLMProduct(
        id=3, board='test_board_5', model='test_model_5', product_status=5,
        device_id=5, device_type=2)
    new_p4 = dlm_product_data.DLMProduct(id=4, board='test_board_6',
                                         model='test_model_6', product_status=1,
                                         device_id=1, device_type=1)

    self._manager.UpdateDLMProducts(products=[updated_p2, updated_p3, new_p4])

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query(order_by=['id']))
      self.assertEqual(len(res), 4)
      # Entity keys can only be accessed in context.
      self.assertEqual(res[0].key, ndb.Key('DLMProduct', 1))
      self.assertEqual(res[1].key, ndb.Key('DLMProduct', 2))
      self.assertEqual(res[2].key, ndb.Key('DLMProduct', 3))
      self.assertEqual(res[3].key, ndb.Key('DLMProduct', 4))

    self.assertEqual(res[0].id, 1)
    self.assertEqual(res[0].board, 'test_board_1')
    self.assertEqual(res[0].model, 'test_model_1')
    self.assertEqual(res[0].product_status, 1)
    self.assertEqual(res[0].device_id, 1)
    self.assertEqual(res[0].device_type, 1)

    self.assertEqual(res[1].id, 2)
    self.assertEqual(res[1].board, 'test_board_4')
    self.assertEqual(res[1].model, 'test_model_4')
    self.assertEqual(res[1].product_status, 4)
    self.assertEqual(res[1].device_id, 4)
    self.assertEqual(res[1].device_type, 2)

    self.assertEqual(res[2].id, 3)
    self.assertEqual(res[2].board, 'test_board_5')
    self.assertEqual(res[2].model, 'test_model_5')
    self.assertEqual(res[2].product_status, 5)
    self.assertEqual(res[2].device_id, 5)
    self.assertEqual(res[2].device_type, 2)

    self.assertEqual(res[3].id, 4)
    self.assertEqual(res[3].board, 'test_board_6')
    self.assertEqual(res[3].model, 'test_model_6')
    self.assertEqual(res[3].product_status, 1)
    self.assertEqual(res[3].device_id, 1)
    self.assertEqual(res[3].device_type, 1)

  def testGetDLMProductsByBoards(self):
    p1 = self._CreateDLMProduct(id=1, board='test_board_1',
                                model='test_model_1', product_status=1,
                                device_id=1, device_type=1)
    p2 = self._CreateDLMProduct(id=2, board='test_board_2',
                                model='test_model_2', product_status=2,
                                device_id=2, device_type=2)
    p3 = self._CreateDLMProduct(id=3, board='test_board_2',
                                model='test_model_2', product_status=3,
                                device_id=2, device_type=2)
    self._CreateDLMProduct(id=4, board='test_board_3', model='test_model_3',
                           product_status=1, device_id=3, device_type=1)

    res = self._manager.GetDLMProductsByBoards(['test_board_1', 'test_board_2'])

    with self._ndb_connector.CreateClientContext():
      # Entity keys can only be accessed in context.
      self.assertCountEqual(res, [p1, p2, p3])

  def testGetDLMProductsByBoards_NoMatchingResult(self):
    self._CreateDLMProduct(id=1, board='test_board_1', model='test_model_1',
                           product_status=1, device_id=1, device_type=1)
    self._CreateDLMProduct(id=2, board='test_board_2', model='test_model_2',
                           product_status=2, device_id=2, device_type=1)

    res = self._manager.GetDLMProductsByBoards(['test_board_3'])

    self.assertEqual(res, [])

  def testUpdateDLMProductsByDeviceId(self):
    p1 = self._CreateDLMProduct(id=1, board='test_board_1',
                                model='test_model_1', product_status=1,
                                device_id=1, device_type=1)
    p2 = self._CreateDLMProduct(id=2, board='test_board_2',
                                model='test_model_2', product_status=2,
                                device_id=2, device_type=1)
    p3 = self._CreateDLMProduct(id=3, board='test_board_2',
                                model='test_model_2', product_status=3,
                                device_id=2, device_type=1)

    self._manager.UpdateDLMProductsByDeviceId(2, 'test_board_3', 'test_model_3',
                                              2)

    with self._ndb_connector.CreateClientContext():
      res = list(dlm_product_data.DLMProduct.query())
      # Entity keys can only be accessed in context.
      p1 = p1.key.get()
      p2 = p2.key.get()
      p3 = p3.key.get()
      self.assertCountEqual(res, [p1, p2, p3])
      self.assertEqual(p1.key, ndb.Key('DLMProduct', 1))
      self.assertEqual(p2.key, ndb.Key('DLMProduct', 2))
      self.assertEqual(p3.key, ndb.Key('DLMProduct', 3))

    self.assertEqual(p1.id, 1)
    self.assertEqual(p1.board, 'test_board_1')
    self.assertEqual(p1.model, 'test_model_1')
    self.assertEqual(p1.product_status, 1)
    self.assertEqual(p1.device_id, 1)
    self.assertEqual(p1.device_type, 1)

    self.assertEqual(p2.id, 2)
    self.assertEqual(p2.board, 'test_board_3')
    self.assertEqual(p2.model, 'test_model_3')
    self.assertEqual(p2.product_status, 2)
    self.assertEqual(p2.device_id, 2)
    self.assertEqual(p2.device_type, 2)

    self.assertEqual(p3.id, 3)
    self.assertEqual(p3.board, 'test_board_3')
    self.assertEqual(p3.model, 'test_model_3')
    self.assertEqual(p3.product_status, 3)
    self.assertEqual(p3.device_id, 2)
    self.assertEqual(p3.device_type, 2)

  def testGetDLMDeviceByModel(self):
    d1 = self._CreateDLMDevice(id=2, board='board', model='test_model_3')

    self.assertIsNone(self._manager.GetDLMDeviceByModel('not_found'))
    self.assertEqual(self._manager.GetDLMDeviceByModel('test_model_3'), d1)

  def testUpdateDLMDevice(self):
    d1 = self._CreateDLMDevice(id=2, board='board')

    device1 = dlm_product_data.DLMDevice(
        id=2, board='test_board_3', model='test_model_2', device_type=1,
        factory_branch='factory-testboard-12345.B')
    device2 = dlm_product_data.DLMDevice(
        id=3, board='test_board_3', model='test_model_3', device_type=1,
        factory_branch='factory-testboard-12345.B')

    self._manager.UpdateDLMDevice(device1)
    self._manager.UpdateDLMDevice(device2)

    with self._ndb_connector.CreateClientContext():
      self.assertEqual(dlm_product_data.DLMDevice.query().count(), 2)
      # Entity keys can only be accessed in context.
      d1 = d1.key.get()
      d2 = dlm_product_data.DLMDevice.query(
          dlm_product_data.DLMDevice.id == 3).get()
      self.assertEqual(d1.key, ndb.Key('DLMDevice', 2))
      self.assertEqual(d2.key, ndb.Key('DLMDevice', 3))

    self.assertEqual(d1.id, 2)
    self.assertEqual(d1.board, 'test_board_3')
    self.assertEqual(d1.model, 'test_model_2')
    self.assertEqual(d1.device_type, 1)
    self.assertEqual(d1.factory_branch, 'factory-testboard-12345.B')

    self.assertEqual(d2.id, 3)
    self.assertEqual(d2.board, 'test_board_3')
    self.assertEqual(d2.model, 'test_model_3')
    self.assertEqual(d2.device_type, 1)
    self.assertEqual(d2.factory_branch, 'factory-testboard-12345.B')


if __name__ == '__main__':
  unittest.main()
