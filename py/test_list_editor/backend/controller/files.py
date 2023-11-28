# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from flask import g

from cros.factory.test_list_editor.backend.models import files as file_model
from cros.factory.test_list_editor.backend.schema import common as common_schema
from cros.factory.test_list_editor.backend.schema import files as file_schema


class FileController:

  def __init__(self, factory: file_model.ITestListFileFactory):
    self.factory = factory

  def SaveFiles(
      self,
      files_request: file_schema.FilesRequest) -> file_schema.SaveFilesResponse:

    folder_path = g.session_folder

    for file in files_request.files:
      test_list_file: file_model.ITestListFile = self.factory.Get(
          data=file.data, filename=file.filename, diff_data={},
          folder_path=folder_path)
      test_list_file.Save()

    return file_schema.SaveFilesResponse(
        status=common_schema.StatusEnum.SUCCESS)
