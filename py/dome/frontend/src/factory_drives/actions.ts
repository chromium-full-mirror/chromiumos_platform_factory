// Copyright 2018 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {createAction} from 'typesafe-actions';

import error from '@app/error';
import formDialog from '@app/form_dialog';
import project from '@app/project';
import task from '@app/task';
import {Dispatch, RootState} from '@app/types';

import {authorizedAxios, isAxiosError} from '@common/utils';

import {
  CREATE_DIRECTORY_FORM,
  DELETE_FACTORY_DRIVE_FORM,
  RENAME_DIRECTORY_FORM,
  RENAME_FACTORY_DRIVE_FORM,
  UPDATE_FACTORY_DRIVE_FORM,
} from './constants';
import {
  getFactoryDriveDirs,
  getFactoryDrives,
  getFactoryDrivesById,
} from './selector';
import {
  CreateDirectoryRequest,
  DeleteRequest,
  FactoryDrive,
  FactoryDriveDirectory,
  RenameRequest,
  UpdateFactoryDriveRequest,
  UpdateFactoryDriveVersionRequest,
} from './types';

const baseURL = (getState: () => RootState): string => {
  return `/projects/${project.selectors.getCurrentProject(getState())}`;
};

const receiveFactoryDrives = createAction('RECEIVE_FACTORY_DRIVES', (resolve) =>
  (factoryDrives: FactoryDrive[]) => resolve({factoryDrives}));

const receiveFactoryDriveDirs =
  createAction('RECEIVE_FACTORY_DRIVE_DIRS', (resolve) =>
  (factoryDriveDirs: FactoryDriveDirectory[]) => resolve({factoryDriveDirs}));

const updateFactoryDrive = createAction('UPDATE_FACTORY_DRIVE', (resolve) =>
  (factoryDrive: FactoryDrive) => resolve({factoryDrive}));

const updateFactoryDriveDir =
  createAction('UPDATE_FACTORY_DRIVE_DIR', (resolve) =>
  (factoryDriveDir: FactoryDriveDirectory) => resolve({factoryDriveDir}));

const deleteFactoryDriveImpl = createAction('DELETE_FACTORY_DRIVE', (resolve) =>
  (factoryDriveId: number) => resolve({factoryDriveId}));

export const basicActions = {
  receiveFactoryDrives,
  updateFactoryDrive,
  receiveFactoryDriveDirs,
  updateFactoryDriveDir,
  deleteFactoryDriveImpl,
};

export const startCreateDirectory = (data: CreateDirectoryRequest) =>
  async (dispatch: Dispatch, getState: () => RootState) => {
    dispatch(formDialog.actions.closeForm(CREATE_DIRECTORY_FORM));

    const factoryDriveDirs = getFactoryDriveDirs(getState());
    const optimisticUpdate = () => {
      let newFactoryDriveDir = factoryDriveDirs.find((d) => (
        d.name === data.name && d.parentId === data.parentId));
      if (!newFactoryDriveDir) {
        newFactoryDriveDir = {
          id: factoryDriveDirs.length,
          name: data.name,
          parentId: data.parentId,
        };
      }
      dispatch(updateFactoryDriveDir(newFactoryDriveDir));
    };

    // send the request
    const description = `Create Directory "${data.name}"`;
    const factoryDriveDir =
      await dispatch(task.actions.runTask<FactoryDriveDirectory>(
        description, 'POST', `${baseURL(getState)}/factory_drives/dirs/`, data,
        optimisticUpdate));
    dispatch(updateFactoryDriveDir(factoryDriveDir));
  };

export const startUpdateFactoryDrive = (data: UpdateFactoryDriveRequest) =>
  async (dispatch: Dispatch, getState: () => RootState) => {
    dispatch(formDialog.actions.closeForm(UPDATE_FACTORY_DRIVE_FORM));

    const factoryDrives = getFactoryDrives(getState());
    const factoryDrivesMap: Map<number, FactoryDrive> =
      getFactoryDrivesById(getState());
    const optimisticUpdate = () => {
      let newFactoryDrive = null;
      if (data.id == null) {
        newFactoryDrive = factoryDrives.find((p) => (
          p.name === data.name && p.dirId === data.dirId));
        if (!newFactoryDrive) {
          let newId = 0;
          if (factoryDrives.length !== 0) {
            const ids = factoryDrives.map((file) => file.id);
            newId = Math.max(...ids) + 1;
          }
          newFactoryDrive = {
            id: newId,
            dirId: data.dirId,
            name: data.name,
            usingVer: 0,
            revisions: [],
          };
        }
      } else {
        newFactoryDrive = factoryDrivesMap.get(data.id)!;
      }
      dispatch(updateFactoryDrive(newFactoryDrive));
    };

    // send the request
    const description = `Update factory drive "${data.name}"`;
    const factoryDriveComponent = await dispatch(
      task.actions.runTask<FactoryDrive>(
      description, 'POST', `${baseURL(getState)}/factory_drives/files/`, data,
      optimisticUpdate));
    dispatch(updateFactoryDrive(factoryDriveComponent));
  };

export const startUpdateComponentVersion =
  (data: UpdateFactoryDriveVersionRequest) =>
    async (dispatch: Dispatch, getState: () => RootState) => {
      // send the request
      const description = `Update factory drive "${data.name}"  version`;
      const factoryDriveComponent = await dispatch(
        task.actions.runTask<FactoryDrive>(
        description, 'POST', `${baseURL(getState)}/factory_drives/files/`, data,
        () => {
          const factoryDrivesMap: Map<number, FactoryDrive> =
            getFactoryDrivesById(getState());
          dispatch(updateFactoryDrive({
            ...factoryDrivesMap.get(data.id)!,
              usingVer: data.usingVer,
          }));
        }));
      dispatch(updateFactoryDrive(factoryDriveComponent));
    };

export const startRenameFactoryDrive = (data: RenameRequest) =>
  async (dispatch: Dispatch, getState: () => RootState) => {
    dispatch(formDialog.actions.closeForm(RENAME_FACTORY_DRIVE_FORM));
    // send the request
    const description = `Rename factory drive "${data.name}"`;
    const factoryDriveComponent = await dispatch(
      task.actions.runTask<FactoryDrive>(
      description, 'POST', `${baseURL(getState)}/factory_drives/files/`, data,
      () => {
        const factoryDrivesMap: Map<number, FactoryDrive> =
          getFactoryDrivesById(getState());
        dispatch(updateFactoryDrive({
          ...factoryDrivesMap.get(data.id)!,
            name: data.name,
          }));
      }));
    dispatch(updateFactoryDrive(factoryDriveComponent));
  };

export const startRenameDirectory = (data: RenameRequest) =>
  async (dispatch: Dispatch, getState: () => RootState) => {
    dispatch(formDialog.actions.closeForm(RENAME_DIRECTORY_FORM));
    // send the request
    const description = `Rename directory "${data.name}"`;
    const directoryComponent =
      await dispatch(task.actions.runTask<FactoryDriveDirectory>(
        description, 'POST', `${baseURL(getState)}/factory_drives/dirs/`, data,
        () => {
          dispatch(updateFactoryDriveDir({
            ...getFactoryDriveDirs(getState())[data.id], name: data.name}));
        }));
    dispatch(updateFactoryDriveDir(directoryComponent));
  };

export const deleteFactoryDrive = (data: DeleteRequest) =>
  (dispatch: Dispatch, getState: () => RootState) => {
    dispatch(formDialog.actions.closeForm(DELETE_FACTORY_DRIVE_FORM));
    dispatch(task.actions.runTask(
      `Delete factory drive "${data.name}"`,
      'DELETE',
      `${baseURL(getState)}/factory_drives/files/`,
      data,
      () => {
        dispatch(deleteFactoryDriveImpl(data.id));
      }));
  };

export const fetchFactoryDrives = () =>
  async (dispatch: Dispatch, getState: () => RootState) => {
    try {
      const components = await authorizedAxios().get<FactoryDrive[]>(
        `${baseURL(getState)}/factory_drives/files.json`);
      dispatch(receiveFactoryDrives(components.data));
      const directories = await authorizedAxios().get<FactoryDriveDirectory[]>(
        `${baseURL(getState)}/factory_drives/dirs.json`);
      dispatch(receiveFactoryDriveDirs(directories.data));
    } catch (unknownError: unknown) {
      if (isAxiosError(unknownError)) {
        let moreMessage = unknownError.response?.data.detail;
        if (moreMessage === undefined) {
          moreMessage = unknownError.response?.data;
        }
        dispatch(error.actions.setAndShowErrorDialog(
            `error fetching factory drives or dirs\n\n${unknownError.message}`,
            moreMessage));
      } else {
        throw unknownError;
      }
    }
  };
