// Copyright 2018 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import React from 'react';
import {connect} from 'react-redux';
import {submit} from 'redux-form';

import formDialog from '@app/form_dialog';
import project from '@app/project';
import {RootState} from '@app/types';

import FileUploadDialog, {
  SelectProps,
} from '@common/components/file_upload_dialog';
import {DispatchProps} from '@common/types';

import {startUpdateFactoryDrive} from '../actions';
import {UPDATE_FACTORY_DRIVE_FORM} from '../constants';
import {getFactoryDrives} from '../selector';
import {UpdateFactoryDriveFormPayload} from '../types';

import UpdateFactoryDriveForm from './update_factory_drive_form';

interface UpdateFactoryDriveDialogState {
  showDuplicateDialog: boolean;
}

type UpdateFactoryDriveDialogProps =
  ReturnType<typeof mapStateToProps> & DispatchProps<typeof mapDispatchToProps>;

class UpdateFactoryDriveDialog extends React.Component<
  UpdateFactoryDriveDialogProps, UpdateFactoryDriveDialogState> {

  state: UpdateFactoryDriveDialogState = {
    showDuplicateDialog: false,
  };

  handleCancel = () => {
    this.props.cancelUpdate();
  }

  handleCloseDuplicateDialog = () => {
    this.setState({showDuplicateDialog: false});
  }

  isExistingFile = (name: string, dirId: number | null) => {
    const {factoryDrives = []} = this.props;
    return factoryDrives.some((p) => p.name === name && p.dirId === dirId);
  }

  handleSubmitOne = ({file}: {file: File}) => {
    const {
      project,
      startUpdate,
      payload,
    } = this.props;
    const thisPayload = payload as UpdateFactoryDriveFormPayload;
    const data = {
      project,
      id: thisPayload.id,
      dirId: thisPayload.dirId,
    };
    if (thisPayload.id == null) {
      if (this.isExistingFile(file.name, thisPayload.dirId)) {
        this.props.cancelUpdate();
        this.setState({showDuplicateDialog: true});
        return;
      }
      startUpdate({...data, name: file.name, file});
    } else {
      startUpdate({...data, name: thisPayload.name, file});
    }
  }

  handleSubmitMultiple = ({files}: {files: FileList}) => {
    const {
      project,
      startUpdate,
      payload,
    } = this.props;
    const thisPayload = payload as UpdateFactoryDriveFormPayload;
    const data = {
      project,
      id: thisPayload.id,
      dirId: thisPayload.dirId,
    };
    let hasDuplicate = false;
    for (const f of files) {
      if (thisPayload.id == null &&
          this.isExistingFile(f.name, thisPayload.dirId)) {
        hasDuplicate = true;
        continue;
      }
      startUpdate({...data, name: f.name, file: f});
    }
    if (hasDuplicate) {
      this.props.cancelUpdate();
      this.setState({showDuplicateDialog: true});
    }
  }

  render() {
    const {open, submitForm, payload} = this.props;
    const {multiple} = payload as UpdateFactoryDriveFormPayload;
    const selectProps: SelectProps =
      multiple ? {multiple, onSubmit: this.handleSubmitMultiple} :
        {multiple, onSubmit: this.handleSubmitOne};
    return (
      <>
        <FileUploadDialog
          open={open}
          title="Update Factory Drive"
          onCancel={this.handleCancel}
          submitForm={submitForm}
          {...selectProps}
        >
          <UpdateFactoryDriveForm />
        </FileUploadDialog>
        <Dialog
          open={this.state.showDuplicateDialog}
          onClose={this.handleCloseDuplicateDialog}
        >
          <DialogTitle>Warning</DialogTitle>
          <DialogContent>
            <DialogContentText>
              This file already exists. Please use the &quot;Update&quot; button
              and do not use the add file button to upload the same file.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={this.handleCloseDuplicateDialog}
              color="primary"
            >
              OK
            </Button>
          </DialogActions>
        </Dialog>
      </>
    );
  }
}

const isFormVisible =
  formDialog.selectors.isFormVisibleFactory(UPDATE_FACTORY_DRIVE_FORM);
const getFormPayload =
  formDialog.selectors.getFormPayloadFactory(UPDATE_FACTORY_DRIVE_FORM);

const mapStateToProps = (state: RootState) => ({
  open: isFormVisible(state),
  project: project.selectors.getCurrentProject(state),
  payload: getFormPayload(state)!,
  factoryDrives: getFactoryDrives(state),
});

const mapDispatchToProps = {
  startUpdate: startUpdateFactoryDrive,
  cancelUpdate: () => formDialog.actions.closeForm(UPDATE_FACTORY_DRIVE_FORM),
  submitForm: () => submit(UPDATE_FACTORY_DRIVE_FORM),
};

export default connect(
  mapStateToProps, mapDispatchToProps)(UpdateFactoryDriveDialog);
