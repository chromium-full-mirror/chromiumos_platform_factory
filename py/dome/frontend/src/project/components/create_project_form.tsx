// Copyright 2016 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import React from 'react';
import {InjectedFormProps, reduxForm} from 'redux-form';

import ReduxFormTextField from '@common/components/redux_form_text_field';
import {validateRequired} from '@common/form';

import {CREATE_PROJECT_FORM} from '../constants';

export interface CreateProjectFormData {
  name: string;
  isAndroid: boolean;
}

interface CreateProjectFormProps {
  projectNames: string[];
}

class CreateProjectForm extends React.Component<
  CreateProjectFormProps
  & InjectedFormProps<CreateProjectFormData, CreateProjectFormProps>> {

  validateUnique = (value: string) => {
    return this.props.projectNames.includes(value) ?
      `${value} already exist` : undefined;
  }

  render() {
    const {handleSubmit, change} = this.props;
    return (
      <form onSubmit={handleSubmit}>
        <ReduxFormTextField
          name="name"
          label="New project name"
          validate={[
            validateRequired,
            this.validateUnique,
          ]}
        />
        <FormControlLabel
          control={
            <Checkbox
              name="isAndroid"
              onChange={(event) => change('isAndroid', event.target.checked)}
            />}
          label="Is this an Android project?"
        />
        <Button
          color="primary"
          variant="contained"
          fullWidth
          type="submit"
        >
          Create a new project
        </Button>
      </form>);
  }
}

export default reduxForm<CreateProjectFormData, CreateProjectFormProps>({
  form: CREATE_PROJECT_FORM,
})(CreateProjectForm);
