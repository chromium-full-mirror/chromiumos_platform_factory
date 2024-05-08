# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A decorator middleware for validating request and response.

The `Validate` function can be used as a decorator to validate the parameters
and the request body of a Flask route function using Pydantic models. If the
validation fails, an error response with a 422 status code is returned. If the
validation succeeds, the wrapped function is called, and its result is
validated against the specified return type.

You can use the decorator like the following.

```python
@app.route('/foo')
@Validate
def Function(...):
  ...
```

To use the decorator to perform data validation, you should add type hintings
to the wrapped function. The decorator will look at the type
hints of `params`, `request_body` and return type. It will use these three
types to validate the corresponding data. See below example.

Examples:
```python

class UserIDParam(BaseModel):
  user_id: int

class UserData(BaseModel):
  name: str

class UserResponse(BaseModel):
  user_id: int
  name: str

@app.route('/users/<user_id>', methods=['POST'])
@Validate
def CreateUser(params: UserIDParam, request_body: UserData) -> UserResponse:

  assert isinstance(params.user_id, int)
```
"""

from functools import wraps
import os
import typing
from typing import Callable, Sequence, Type, Union

# yapf: enable
# yapf: disable
from flask import g  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
from flask import request
# yapf: enable
# yapf: disable
from pydantic import BaseModel  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
from pydantic import ValidationError

from cros.factory.test_list_editor.backend.middleware import validation_exception as exceptions
from cros.factory.test_list_editor.backend.models import files as file_model
from cros.factory.test_list_editor.backend.schema import common as common_schema


_PARAMS_STR = 'params'
_REQUEST_STR = 'request_body'
_RESPONSE_STR = 'return'


def _MarshalData(model: Type[BaseModel], data: dict) -> BaseModel:
  return model(**data)


def _ValidateDataWithModels(
    data_model: Type[BaseModel], data: dict,
    model_exception: Type[exceptions.ValidationException]):
  """Validates data using Pydantic models.

  This function validates the given data using a Pydantic model specified as
  `data_model`. If validation succeeds, the validated data is returned. If
  validation fails, a `model_exception` is raised with the error message.

  Args:
    data_model: A Pydantic model used for validating the data.
    data: The data to be validated, provided as a dictionary.
    model_exception: The exception class to be raised in case of
      validation failure. This should be a class derived from
      exceptions.ValidationException.

  Returns:
      The validated data.

  Raises:
      ValidationException: If the data fails validation.

  """
  try:
    return _MarshalData(data_model, data)
  except ValidationError as e:
    raise model_exception(str(e)) from e


def Validate(f: Callable[..., Union[Sequence[BaseModel], BaseModel]]):
  """Decorator function for validating request and response.

  This decorator function validates the incoming request's parameters, request
  body using Pydantic models specified in the function's type hints.

  If validation succeeds, the wrapped function is called with the validated
  parameters and request body. If validation fails, the function returns an
  error response with a validation error message.

  Args:
    f: A function to be wrapped.

  Returns:
    A wrapper function that validates the incoming request's parameters, request
      body and response.
  """
  hints = typing.get_type_hints(f)

  @wraps(f)
  def wrapped(*args, **kwargs):  # pylint: disable=unused-argument
    func_kwargs = {}
    if _PARAMS_STR in hints:
      func_kwargs[_PARAMS_STR] = _ValidateDataWithModels(
          hints[_PARAMS_STR], request.view_args,
          exceptions.ParamsValidationException)
    if _REQUEST_STR in hints:
      func_kwargs[_REQUEST_STR] = _ValidateDataWithModels(
          hints[_REQUEST_STR], request.get_json(),
          exceptions.RequestValidationException)

    result = f(**func_kwargs)

    if isinstance(result, Sequence):
      resp_type = hints[_RESPONSE_STR]

      body = _ValidateDataWithModels(resp_type.__args__[0], result[0].dict(),
                                     exceptions.ResponseValidationException)
      if len(result) == 2 and issubclass(resp_type.__args__[1],
                                         common_schema.BaseHeader):
        header = _ValidateDataWithModels(resp_type.__args__[1],
                                         result[1].dict(by_alias=True),
                                         exceptions.ResponseValidationException)
        return body.dict(), header.dict(by_alias=True)

      # TODO(louischiu): Handle the other cases here.
      raise exceptions.ResponseValidationException(
          'Unexpected response argument')
    result_data = _ValidateDataWithModels(
        hints[_RESPONSE_STR], result.dict(),
        exceptions.ResponseValidationException)
    return result_data.dict()

  return wrapped


def ValidateUserSession(func):

  @wraps(func)
  def wrapper(*args, **kwargs):
    user_id = request.headers.get('user_id')
    session_id = request.headers.get('session_id')

    # Validate user_id and session_id
    if not user_id or not session_id:
      raise exceptions.HeaderValidationException(
          'Missing user_id or session_id in headers')

    # Setup user session folder
    user_session_folder = os.path.join(file_model.TEST_LIST_STORAGE_DIR,
                                       user_id, session_id)
    file_model.CopyAndUpdateTestLists(user_session_folder)

    g.session_folder = user_session_folder

    return func(*args, **kwargs)

  return wrapper
