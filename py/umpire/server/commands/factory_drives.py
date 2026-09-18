# Copyright 2019 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Action on factory drive.

See FactoryDrives for detail.
"""

import logging
import os
from typing import Any

from cros.factory.umpire import common
from cros.factory.umpire.server import utils
from cros.factory.utils import file_utils
from cros.factory.utils import json_utils


class _FactoryDriveObject:
  """Provides operation on factory drive objects.

  Properties:
    data: including files and dirs.
    files: factory drive component files.
    dirs: factory drive directory.
  """

  def __init__(self, data):
    self.dirs: dict[int, Any] = {
        d['id']: d
        for d in data['dirs']
    }
    self.files: dict[int, Any] = {
        f['id']: f
        for f in data['files']
    }

  def _FindComponentsByName(self, dir_id, name):
    """Return List of component(s) in given directory and component name.

    If name is None, return all components in this directory.
    """
    fs = [f for f in self.files.values() if f['dir_id'] == dir_id]
    if name is not None:
      fs = [f for f in fs if f['name'] == name]
    return fs

  def _FindChildDirByName(self, parent_id, dir_name):
    """Return directory in given parent directory and directory name."""
    return next((d for d in self.dirs.values()
                 if d['name'] == dir_name and d['parent_id'] == parent_id),
                None)

  def _FindComponentById(self, comp_id):
    """Return component with given id."""
    return self.files.get(comp_id)

  def _FindDirectoryById(self, dir_id):
    """Return directory with given id."""
    return self.dirs.get(dir_id)

  def _UpdateExistingComponent(self, component, rename, using_ver, dst_path):
    """Update existing component: revision, update new version, and rename."""
    if sum(attr is not None for attr in [rename, using_ver, dst_path]) > 1:
      raise common.UmpireError(
          'Intend to do multiple operations at the same time.')
    if dst_path:
      # update component to new version
      version_count = len(component['revisions'])
      component['revisions'].append(dst_path)
      component['using_ver'] = version_count
    elif using_ver is not None:
      # rollback component to existed version
      if not 0 <= using_ver < len(component['revisions']):
        raise common.UmpireError(
            'Intend to use invalid version of factory drive '
            f'{int(component["id"])}.')
      component['using_ver'] = using_ver
    elif rename is not None:
      # rename component
      component['name'] = rename
    return component

  def _RemoveExistingComponent(self, component):
    comp_id = component['id']
    revisions_to_delete = component.get('revisions', [])
    if not revisions_to_delete:
      raise common.UmpireError(f'No revisions listed for id {comp_id}')

    for file_path in set(revisions_to_delete):
      if os.path.exists(file_path):
        try:
          os.remove(file_path)
        except PermissionError as e:
          raise common.UmpireError(
              f'Error: Permission denied to delete {file_path}: {e}')
        except Exception as e:
          raise common.UmpireError(f'An error occurred during deletion: {e}')
      else:
        raise common.UmpireError(f'NOT FOUND: {file_path}')
    del self.files[comp_id]

  def GetNewCompId(self):
    return max(self.files.keys(), default=-1) + 1

  def _CreateComponent(self, dir_id, comp_name, dst_path):
    """Create new component."""
    new_comp_id = self.GetNewCompId()
    component = {
        'id': new_comp_id,
        'dir_id': dir_id,
        'name': comp_name,
        'using_ver': 0,
        'revisions': [dst_path]
    }
    self.files[new_comp_id] = component
    return component

  def UpdateComponent(self, comp_id, dir_id, comp_name, using_ver, dst_path):
    """See UmpireEnv.UpdateFactoryDriveComponent for detail"""
    if comp_id is not None:
      component = self._FindComponentById(comp_id)
      rename = comp_name if comp_name != component['name'] else None
      if rename and self._FindComponentsByName(component['dir_id'], rename):
        raise common.UmpireError('Intend to rename to existing component.')
      return self._UpdateExistingComponent(component, rename, using_ver,
                                           dst_path)

    # check if same name component already existed in same dir
    existed_comp = self._FindComponentsByName(dir_id, comp_name)
    if existed_comp:
      # create file but name existed in same dir, view as updating version
      return self._UpdateExistingComponent(existed_comp[0], None, using_ver,
                                           dst_path)
    if using_ver is not None:
      raise common.UmpireError(
          'Intend to create component but assigned using_ver.')
    return self._CreateComponent(dir_id, comp_name, dst_path)

  def RemoveComponent(self, comp_id):
    component = self._FindComponentById(comp_id)
    if not component:
      raise common.UmpireError(f'Component with id {comp_id} not found.')
    self._RemoveExistingComponent(component)

  def _UpdateExistingDirectory(self, directory, rename):
    """Update existing directory: rename."""
    if rename is not None:
      directory['name'] = rename
    return directory

  def _CreateDirectory(self, parent_id, dir_name):
    """Create new directory"""
    dir_id = len(self.dirs)
    new_dir = {
        'id': dir_id,
        'parent_id': parent_id,
        'name': dir_name
    }
    self.dirs[dir_id] = new_dir
    return new_dir

  def UpdateDirectory(self, dir_id, parent_id, dir_name):
    """See UmpireEnv.UpdateFactoryDriveDirectory for detail."""
    if dir_id is not None:
      directory = self._FindDirectoryById(dir_id)
      rename = dir_name if dir_name != directory['name'] else None
      if rename and self._FindChildDirByName(directory['parent_id'], rename):
        raise common.UmpireError('Intend to rename to existing directory.')
      return self._UpdateExistingDirectory(directory, rename)

    existed_dir = self._FindChildDirByName(parent_id, dir_name)
    if existed_dir:
      # create dir but name existed in parent dir, directly return
      return existed_dir
    return self._CreateDirectory(parent_id, dir_name)

  def _GetDirIdByNameSpace(self, namespace):
    """Retrieve directory by given namespace."""
    if namespace is None:
      return None
    normalized_namespace = os.path.normpath(namespace)
    if normalized_namespace in ('.', '/'):
      return None
    parts = normalized_namespace.strip('/').split('/')
    current_id = None
    for name in parts:
      next_dir = self._FindChildDirByName(current_id, name)
      if next_dir is None:
        raise common.UmpireError('Directory namespace not exists.')
      current_id = next_dir['id']
    return current_id

  def GetComponentsAbsPath(self, namespace, name):
    """See UmpireEnv.QueryFactoryDrives for detail."""
    try:
      dir_id = self._GetDirIdByNameSpace(namespace)
    except common.UmpireError:
      logging.error('Intend to request non-existent namespace.')
      return []
    fs = self._FindComponentsByName(dir_id, name)
    return [(f['name'], f['revisions'][f['using_ver']]) for f in fs]

  def GetComponentAbsPathById(self, comp_id):
    """Get the disk path of the component's current revision."""
    comp = self._FindComponentById(comp_id)
    if comp is None:
      raise common.UmpireError(f'Compnent with id {comp_id} does not exist.')
    return comp['revisions'][comp['using_ver']]

  def _GetNameaspace(self, dir_id):
    """Recursively resolve the namespace of dir in factory drive."""
    if dir_id is None:
      return '/'

    directory = self._FindDirectoryById(dir_id)
    if directory is None:
      raise common.UmpireError(f'Dir with id {dir_id} not found.')
    return self._GetNameaspace(directory['parent_id']) + directory['name'] + '/'

  def GetPathInFactoryDrive(self, comp_id):
    """Get the file path of component in factory drive."""
    comp = self._FindComponentById(comp_id)
    if comp:
      return self._GetNameaspace(comp['dir_id']) + comp['name']
    logging.error('Compnent with id %s does not exist.', comp_id)
    return None


class FactoryDrives:
  """Wraps FactoryDriveObject and synchronize the data to
     factory_drive_json_file.

  Properties:
    env: UmpireEnv object.
  """

  def __init__(self, env):
    self._factory_drive_json_file = env.factory_drive_json_file
    self._factory_drives_dir = env.factory_drives_dir
    self._factory_drive = _FactoryDriveObject(
        json_utils.LoadFile(self._factory_drive_json_file))

  def _DumpFactoryDrive(self):
    """Dump factory drive to json file."""
    data = {
        "dirs": list(self._factory_drive.dirs.values()),
        "files": list(self._factory_drive.files.values())
    }
    json_utils.DumpFile(self._factory_drive_json_file, data)

  def GetFactoryDriveDstPath(self, comp_id, src_path):
    """Prepend file MD5 sum to file path"""
    original_filename = os.path.basename(src_path)
    md5sum = file_utils.MD5InHex(src_path)
    comp_id = comp_id if comp_id else self._factory_drive.GetNewCompId()
    new_filemame = '.'.join([original_filename, str(comp_id), md5sum])
    return os.path.join(self._factory_drives_dir, new_filemame)

  def _AddFactoryDrive(self, comp_id, src_path):
    dst_path = self.GetFactoryDriveDstPath(comp_id, src_path)
    utils.CheckAndMoveFile(src_path, dst_path, False)
    return dst_path

  def GetFactoryDriveManifest(self):
    """Get the factory drive manifest."""
    manifest = []
    for comp_id in self._factory_drive.files.keys():
      virtual_path = self._factory_drive.GetPathInFactoryDrive(comp_id)
      disk_path = self._factory_drive.GetComponentAbsPathById(comp_id)
      file_md5sum = disk_path.split('.')[-1]
      manifest.append({
          'file_path': virtual_path,
          'hash': file_md5sum
      })
    return manifest

  def UpdateFactoryDriveComponent(self, comp_id, dir_id, comp_name, using_ver,
                                  src_path):
    """Update a factory drive component file.

    Support following types of actions:
      1) Create new component.
      2) Rollback component to existed version.
      3) Update component to new version.
      4) Rename component.

    Args:
      comp_id: component id. None if intend to create a new component.
      dir_id: directory id where the component will be created.
              None if component is at root directory.
      comp_name: new component name.
      using_ver: file version component will use.
      src_path: uploaded file path.

    Returns:
      Updated component dictionary.
    """
    dst_path = self._AddFactoryDrive(comp_id, src_path) if src_path else None
    component = self._factory_drive.UpdateComponent(comp_id, dir_id, comp_name,
                                                    using_ver, dst_path)
    self._DumpFactoryDrive()
    return component

  def RemoveFactoryDriveComponent(self, comp_id):
    """Remove a factory drive component file.

    Args:
      comp_id: component id. None if intend to create a new component.
    """
    try:
      self._factory_drive.RemoveComponent(comp_id)
    except Exception as e:
      raise common.UmpireError(f'An error occurred during deletion: {e}')
    self._DumpFactoryDrive()

  def GetFactoryDriveInfo(self):
    """Dump factory drive info.

    Returns:
      Factory drive dictionary, which contains component files and directories.
      {
        "files": FileComponent[],
        "dirs": Directory[]
      }
      FileComponent = {
        "id": number, // index
        "dir_id": number | null, // directory index
        "name": string, // component name
        "using_ver": number, // version to use, range: [0, len(revisions))
        "revisions": string[], // file paths
      }
      Directory = {
        "id": number, // index
        "parent_id": number | null, // parent directory index
        "name": string, // directory name
      }
    """
    data = {
        "dirs": list(self._factory_drive.dirs.values()),
        "files": list(self._factory_drive.files.values())
    }
    return data

  def UpdateFactoryDriveDirectory(self, dir_id, parent_id, name):
    """Update a factory drive directory.

    Support following types of actions:
      1) Create new directory.
      2) Rename directory.

    Args:
      parent_id: parent directory id where the dir will be created.
                 None if parent is root directory.
      name: new directory name.

    Returns:
      Updated directory dictionary.
    """
    directory = self._factory_drive.UpdateDirectory(dir_id, parent_id, name)
    self._DumpFactoryDrive()
    return directory

  def QueryFactoryDrives(self, namespace, name):
    """Gets file path of queried component(s).

    Args:
      namespace: relative directory path(separate by '/') of queried
                 component(s). None if they are in root directory.
      name: component name of queried component. None if queries all components
            under namespace.

    Returns:
      List of tuple(component name, file path)
    """
    return self._factory_drive.GetComponentsAbsPath(namespace, name)
