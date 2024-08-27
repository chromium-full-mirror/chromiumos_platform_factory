# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""DLM product data model and its manager."""

from typing import Optional, Sequence, Union

from google.cloud import ndb

from cros.factory.hwid.service.appengine import ndb_connector as ndbc_module


class DLMProduct(ndb.Model):
  """The product data in DLM.

  Attributes:
    id: The product id.
    board: The board name of the device to which the product belongs.
    model: The model name of the device to which the product belongs.
    product_status: The status of the product.
    device_id: The id of the device to which the product belongs.
    device_type: The type of the device to which the product belongs.
  """

  ENTITY_KIND = 'DLMProduct'

  id = ndb.IntegerProperty(indexed=True, required=True)
  board = ndb.StringProperty(required=True)
  model = ndb.StringProperty()
  product_status = ndb.IntegerProperty(required=True)
  device_id = ndb.IntegerProperty(indexed=True, required=True)
  device_type = ndb.IntegerProperty()


class DLMDevice(ndb.Model):
  """The device data in DLM.

  Attributes:
    id: The device id.
    board: The board name of the device.
    model: The model name of the device.
    device_type: The type of the device.
    factory_branch: The factory branch.
  """

  ENTITY_KIND = 'DLMDevice'

  id = ndb.IntegerProperty(indexed=True, required=True)
  board = ndb.StringProperty(required=True)
  model = ndb.StringProperty()
  device_type = ndb.IntegerProperty()
  factory_branch = ndb.StringProperty()


@ndb.transactional()
def _SaveEntities(entities: Sequence[Union[DLMProduct, DLMDevice]]):
  for entity in entities:
    entity.key = ndb.Key(entity.ENTITY_KIND, entity.id)
  ndb.put_multi(entities)


class DLMProductManager:

  def __init__(self, ndb_connector: ndbc_module.NDBConnector):
    self._ndb_connector = ndb_connector

  def GetDLMProductsByBoards(self,
                             boards: Sequence[str]) -> Sequence[DLMProduct]:
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      q = DLMProduct.query(DLMProduct.board.IN(boards))
      return list(q)

  def UpdateDLMProducts(self, products: Sequence[DLMProduct]):
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      _SaveEntities(products)

  def UpdateDLMProductsByDeviceId(self, device_id: int, board: str, model: str,
                                  device_type: int):
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      q = DLMProduct.query().filter(DLMProduct.device_id == device_id)
      products_to_update = []
      for product in q:
        if (product.board, product.model, product.device_type) != (board, model,
                                                                   device_type):
          product.board = board
          product.model = model
          product.device_type = device_type
          products_to_update.append(product)

      if products_to_update:
        ndb.model.put_multi(products_to_update)

  def GetDLMDeviceByModel(self, model: str) -> Optional[DLMDevice]:
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      return DLMDevice.query(DLMDevice.model == model).get()

  def UpdateDLMDevice(self, device: DLMDevice):
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      _SaveEntities([device])

  def CleanAllForTest(self):
    with self._ndb_connector.CreateClientContext():
      ndb.delete_multi(DLMProduct.query().iter(keys_only=True))
      ndb.delete_multi(DLMDevice.query().iter(keys_only=True))
