# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""DLM product data model and its manager."""

from typing import Sequence

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
  """

  id = ndb.IntegerProperty(indexed=True, required=True)
  board = ndb.StringProperty(required=True)
  model = ndb.StringProperty()
  product_status = ndb.IntegerProperty(required=True)
  device_id = ndb.IntegerProperty(indexed=True, required=True)


class InvalidProductError(Exception):
  """The product data is invalid."""


class DLMProductManager:

  def __init__(self, ndb_connector: ndbc_module.NDBConnector):
    self._ndb_connector = ndb_connector

  def GetDLMProductsByBoards(self,
                             boards: Sequence[str]) -> Sequence[DLMProduct]:
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      q = DLMProduct.query(DLMProduct.board.IN(boards))
      return list(q)

  def UpdateDLMProduct(self, product_id: int, **attrs):
    try:
      with self._ndb_connector.CreateClientContextWithGlobalCache():
        need_save = False

        entity = DLMProduct.query(DLMProduct.id == product_id).get()
        if entity is None:
          entity = DLMProduct(id=product_id, **attrs)
          need_save = True
        else:
          for attr, value in attrs.items():
            if getattr(entity, attr) != value:
              setattr(entity, attr, value)
              need_save = True

        if need_save:
          entity.put()
    except (AttributeError, ndb.exceptions.BadValueError) as e:
      raise InvalidProductError(
          'Failed to update invalid product data '
          f'{ {"id": product_id, **attrs} } with exception: {e}') from e

  def UpdateDLMProductByDeviceId(self, device_id: int, board: str, model: str):
    with self._ndb_connector.CreateClientContextWithGlobalCache():
      q = DLMProduct.query().filter(DLMProduct.device_id == device_id)
      products_to_update = []
      for product in q:
        if product.board != board or product.model != model:
          product.board = board
          product.model = model
          products_to_update.append(product)

      if products_to_update:
        ndb.model.put_multi(products_to_update)

  def CleanAllForTest(self):
    with self._ndb_connector.CreateClientContext():
      ndb.delete_multi(DLMProduct.query().iter(keys_only=True))
