# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
from unittest import mock

from jsonschema import ValidationError as JSONValidationError
# yapf: disable
from pydantic import ValidationError as PydanticValidationError  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long

from cros.factory.test.test_lists import test_list_common
from cros.factory.test_list_editor.backend.schema import files as file_schema


# yapf: enable



class TestFilesObject(unittest.TestCase):

  @mock.patch.object(test_list_common, 'ValidateTestListFileSchema')
  def testInvalidFileValidation(self, mock_validator):
    mock_validator.side_effect = JSONValidationError('Error Message')

    with self.assertRaises(PydanticValidationError):
      file_schema.FileObject(filename='foo1.json', data={})
