# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Wrapper for loading external module."""

import importlib
import os
import pathlib
from typing import Any, Dict


def ExternalWrapperLoadModule(file_path: pathlib.Path,
                              context: Dict[str, Any]) -> bool:
  for parent in file_path.parents:
    if '.'.join(parent.parts[-4:]) == 'cros.factory.external.py_lib':
      file_path = file_path.relative_to(parent).with_suffix('')
      break
  else:
    raise ValueError('External modules must under cros.factory.external.py_lib '
                     f'Get file_path={file_path}')
  name = '.'.join(file_path.parts)
  module = None
  result = False
  try:
    module = importlib.import_module(name)
    result = True
  except Exception:
    # Only stop if required.
    if os.getenv('DEBUG_IMPORT'):
      raise

  if not module:
    # Try to load from dummy implementation. This should not change
    # MODULE_READY.
    name = 'cros.factory.external.py_lib._dummy.' + name
    try:
      module = importlib.import_module(name)
    except Exception:
      pass

  if module:
    # Publish everything from module.
    context.update(module.__dict__)

  return result


MODULE_READY = ExternalWrapperLoadModule(pathlib.Path(__file__), locals())
