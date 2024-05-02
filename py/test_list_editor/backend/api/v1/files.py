# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from flask import Blueprint  # type: ignore #TODO(b/338318729) Fixit!

from cros.factory.test_list_editor.backend.controller import files as file_controller
from cros.factory.test_list_editor.backend.middleware import validation
from cros.factory.test_list_editor.backend.models import files as files_model
from cros.factory.test_list_editor.backend.schema import files as file_schema


def CreateBP():
  bp = Blueprint('files', __name__, url_prefix='/api/v1/files')

  controller = file_controller.FileController(files_model.GetFactoryInstance())

  @bp.route('/', methods=['PUT'])
  @validation.Validate
  @validation.ValidateUserSession
  def SaveFiles(
      request_body: file_schema.FilesRequest) -> file_schema.SaveFilesResponse:
    """Saves files sent from the frontend."""
    return controller.SaveFiles(request_body)

  return bp
