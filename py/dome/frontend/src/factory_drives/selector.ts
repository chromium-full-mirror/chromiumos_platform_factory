// Copyright 2018 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {createSelector} from 'reselect';

import {RootState} from '@app/types';

import {displayedState} from '@common/optimistic_update';

import {NAME} from './constants';
import {FactoryDriveState} from './reducer';
import {FactoryDrive, FactoryDriveDirectory} from './types';

export const localState = (state: RootState): FactoryDriveState =>
  displayedState(state)[NAME];

export const getFactoryDrives =
  (state: RootState): FactoryDrive[] => localState(state).files;

export const getFactoryDriveDirs =
  (state: RootState): FactoryDriveDirectory[] => localState(state).dirs;

export const getFactoryDrivesById = createSelector(
  getFactoryDrives,
  (factoryDrives: FactoryDrive[]): Map<number, FactoryDrive> => {
    const drivesMap = new Map<number, FactoryDrive>();
    for (const drive of factoryDrives) {
      drivesMap.set(drive.id, drive);
    }
    return drivesMap;
  },
);
