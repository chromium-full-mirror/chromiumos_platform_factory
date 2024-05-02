#!/usr/bin/env python3
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from typing import Tuple
import unittest
from unittest import mock

from flask import Flask  # type: ignore #TODO(b/338318729) Fixit!
from pydantic import BaseModel  # type: ignore #TODO(b/338318729) Fixit!
from pydantic import Field

from cros.factory.test_list_editor.backend.middleware import validation
from cros.factory.test_list_editor.backend.middleware import validation_exception
from cros.factory.test_list_editor.backend.models import files as file_model
from cros.factory.test_list_editor.backend.schema import common


class TestValidateParams(unittest.TestCase):

  def setUp(self) -> None:
    self.app = Flask(__name__)

    class UserIDParam(BaseModel):
      user_id: int

    class UserResponse(BaseModel):
      user_id: int

    @self.app.route('/users/<user_id>', methods=['GET'])
    @validation.Validate
    def GetUser(params: UserIDParam) -> UserResponse:
      return UserResponse(user_id=params.user_id)

    class UserResourceParam(BaseModel):
      user_id: int
      file_name: str

    class UserResourceResponse(BaseModel):
      user_id: int
      file_name: str

    @self.app.route('/users/<user_id>/file/<file_name>', methods=['GET'])
    @validation.Validate
    def GetUserFile(params: UserResourceParam) -> UserResourceResponse:
      return UserResourceResponse(user_id=params.user_id,
                                  file_name=params.file_name)

    validation_exception.RegisterErrorHandler(self.app)

  def testValidParams(self):
    with self.app.test_client() as client:
      response = client.get('/users/123')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.get_json(), {'user_id': 123})

  def testMultipleValidParams(self):
    with self.app.test_client() as client:
      response = client.get('/users/123/file/foo.txt')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.get_json(), {
          'user_id': 123,
          'file_name': 'foo.txt'
      })

  def testInvalidParams(self):
    with self.app.test_client() as client:
      response = client.get('/users/abc')
      self.assertEqual(response.status_code, 422)
      self.assertEqual(response.get_json()['status'],
                       common.StatusEnum.VALIDATION_ERROR)


class TestValidateRequest(unittest.TestCase):

  def setUp(self) -> None:
    self.app = Flask(__name__)

    class UserRequest(BaseModel):
      user_id: int

    class UserResponse(BaseModel):
      user_id: int

    @self.app.route('/users/', methods=['GET'])
    @validation.Validate
    def CreateUser(request_body: UserRequest) -> UserResponse:  # pylint: disable=unused-argument
      return UserResponse(user_id=123)

    validation_exception.RegisterErrorHandler(self.app)

  def testValidRequestBody(self):
    with self.app.test_client() as client:
      response = client.get('/users/', json={'user_id': 123})
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.get_json(), {'user_id': 123})

  def testInvalidRequestBody(self):
    with self.app.test_client() as client:
      response = client.get('/users/', json={'user_id': 'abc'})
      self.assertEqual(response.status_code, 422)
      self.assertEqual(response.get_json()['status'],
                       common.StatusEnum.VALIDATION_ERROR)


class TestValidateResponse(unittest.TestCase):

  def setUp(self) -> None:
    self.app = Flask(__name__)

    validation_exception.RegisterErrorHandler(self.app)

  def testValidResponse(self):

    class UserResponseBody(BaseModel):
      user_id: int  # type: ignore #TODO(b/338318729) Fixit!

    @self.app.route('/users/', methods=['GET'])
    @validation.Validate
    def CreateUser() -> UserResponseBody:
      return UserResponseBody(user_id=123)

    with self.app.test_client() as client:
      response = client.get('/users/')

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.get_json(), {'user_id': 123})

  def testValidResponseTupleType(self):

    class UserResponseBody(BaseModel):
      user_id: int  # type: ignore #TODO(b/338318729) Fixit!

    class UserResponseHeader(common.BaseHeader):
      custom_header: str = Field(alias='custom-header')  # type: ignore #TODO(b/338318729) Fixit!

    @self.app.route('/export/users/', methods=['GET'])
    @validation.Validate
    def DownloadUser() -> Tuple[UserResponseBody, UserResponseHeader]:
      header = {
          'custom-header': '1'
      }
      return UserResponseBody(user_id=123), UserResponseHeader(**header)

    with self.app.test_client() as client:
      response = client.get('/export/users/')

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.headers.get('custom-header', None), '1')
    self.assertEqual(response.get_json(), {'user_id': 123})


  def testValidResponseDifferentClass(self):

    class UserResponse(BaseModel):
      user_id: int  # type: ignore #TODO(b/338318729) Fixit!

    class AnotherUserResponse(BaseModel):
      user_id: int  # type: ignore #TODO(b/338318729) Fixit!

    @self.app.route('/users/', methods=['GET'])
    @validation.Validate
    def GetUser() -> UserResponse:
      return AnotherUserResponse(user_id=123)  # type: ignore

    with self.app.test_client() as client:
      response = client.get('/users/')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.get_json(), {'user_id': 123})

  def testInvalidResponse(self):

    class UserResponse(BaseModel):
      user_id: int  # type: ignore #TODO(b/338318729) Fixit!

    class BadUserResponse(BaseModel):
      user_id: str  # type: ignore #TODO(b/338318729) Fixit!

    @self.app.route('/users/', methods=['GET'])
    @validation.Validate
    def CreateUser() -> UserResponse:
      return BadUserResponse(user_id='abc')  # type: ignore

    with self.app.test_client() as client:
      response = client.get('/users/')
      self.assertEqual(response.status_code, 500)
      self.assertEqual(response.get_json()['status'],
                       common.StatusEnum.VALIDATION_ERROR)

  def testInvalidResponseUnknownType(self):

    class UserResponseBody(BaseModel):
      user_id: int  # type: ignore #TODO(b/338318729) Fixit!

    class BadUserResponse(BaseModel):
      bad_data: int  # type: ignore #TODO(b/338318729) Fixit!

    @self.app.route('/export/bad/users/', methods=['GET'])
    @validation.Validate
    def DownloadBadUser() -> Tuple[UserResponseBody, BadUserResponse]:
      return UserResponseBody(user_id=123), BadUserResponse(bad_data=1)

    with self.app.test_client() as client:
      response = client.get('/export/bad/users/')
      self.assertEqual(response.status_code, 500)

class TestCombinedUsecase(unittest.TestCase):

  def setUp(self) -> None:
    self.app = Flask(__name__)

    class UserParams(BaseModel):
      user_id: str

    class UserRequest(BaseModel):
      data: str

    class UserResponse(BaseModel):
      content: dict

    @self.app.route('/users/<user_id>', methods=['GET'])
    @validation.Validate
    def CreateUser(
        params: UserParams,  # pylint: disable=unused-argument
        request_body: UserRequest  # pylint: disable=unused-argument
    ) -> UserResponse:
      return UserResponse(content={})

    validation_exception.RegisterErrorHandler(self.app)

  def testCombined(self):

    with self.app.test_client() as client:
      response = client.get('/users/foo', json={'data': 'test123'})
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.get_json(), {'content': {}})


class TestUserSession(unittest.TestCase):

  def setUp(self) -> None:
    self.app = Flask(__name__)

    @self.app.route('/', methods=['GET'])
    @validation.ValidateUserSession
    def MockEndpoint():
      return {}

    validation_exception.RegisterErrorHandler(self.app)

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testCreating(self, _: mock.Mock):
    with self.app.test_client() as client:
      response = client.get('/', headers={
          'user_id': 'uid1',
          'session_id': 'sid1'
      })
      self.assertEqual(response.status_code, 200)

  @mock.patch.object(file_model, 'CopyAndUpdateTestLists')
  def testMissingHeader(self, _: mock.Mock):
    with self.app.test_client() as client:
      response = client.get('/', headers={
          'user_id': 'uid1',
      })
      self.assertEqual(response.status_code, 401)
      self.assertEqual(response.get_json()['status'],
                       common.StatusEnum.VALIDATION_ERROR)
