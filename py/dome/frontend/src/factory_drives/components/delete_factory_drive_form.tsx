// Copyright 2026 The ChromiumOS Authors
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
import {
  InjectedFormProps,
  reduxForm,
  submit,
} from 'redux-form';

import formDialog from '@app/form_dialog';
import project from '@app/project';
import {RootState} from '@app/types';

import {HiddenSubmitButton} from '@common/form';
import {DispatchProps} from '@common/types';

import {deleteFactoryDrive} from '../actions';
import {DELETE_FACTORY_DRIVE_FORM} from '../constants';
import {DeleteRequest} from '../types';

const InnerFormComponent: React.SFC<InjectedFormProps<DeleteRequest>> =
  ({handleSubmit}) => (
    <form onSubmit={handleSubmit}>
      <HiddenSubmitButton />
    </form>
  );

const InnerForm = reduxForm<DeleteRequest>({
  form: DELETE_FACTORY_DRIVE_FORM,
})(InnerFormComponent);

type DeleteFactoryDriveFormProps =
  ReturnType<typeof mapStateToProps> &
  DispatchProps<typeof mapDispatchToProps>;

class DeleteFactoryDriveForm
  extends React.Component<DeleteFactoryDriveFormProps> {
  render() {
    const {open, cancelDelete, deleteFactoryDrive, submitForm} = this.props;
    const payload = this.props.payload as DeleteRequest;
    const initialValues = {
      id: payload.id,
      name: payload.name,
    };
    return (
      <Dialog open={open} onClose={cancelDelete}>
        <DialogTitle>Delete Factory Drive</DialogTitle>
        <DialogContent>
          <InnerForm
            onSubmit={deleteFactoryDrive}
            initialValues={initialValues}
          />
          <DialogContentText>
            Delete all versions of this file
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button color="primary" onClick={submitForm}>Delete</Button>
          <Button onClick={cancelDelete}>Cancel</Button>
        </DialogActions>
      </Dialog>
    );
  }
}

const isFormVisible =
  formDialog.selectors.isFormVisibleFactory(DELETE_FACTORY_DRIVE_FORM);
const getFormPayload =
  formDialog.selectors.getFormPayloadFactory(DELETE_FACTORY_DRIVE_FORM);

const mapStateToProps = (state: RootState) => ({
  open: isFormVisible(state),
  project: project.selectors.getCurrentProject(state),
  payload: getFormPayload(state)!,
});

const mapDispatchToProps = {
  submitForm: () => submit(DELETE_FACTORY_DRIVE_FORM),
  cancelDelete: () => formDialog.actions.closeForm(DELETE_FACTORY_DRIVE_FORM),
  deleteFactoryDrive,
};

export default connect(
  mapStateToProps, mapDispatchToProps)(DeleteFactoryDriveForm);
