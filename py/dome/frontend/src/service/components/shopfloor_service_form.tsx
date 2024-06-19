// Copyright 2024 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import Button from '@mui/material/Button';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import React from 'react';
import {InjectedFormProps, reduxForm} from 'redux-form';

import {Schema, Service} from '../types';

import RenderFields from './render_fields';

type ShopfloorServiceFormData = Service;

interface ShopfloorServiceFormProps {
  schema: Schema;
  handleTestConnection?: React.MouseEventHandler<HTMLButtonElement>;
}

class ShopfloorServiceForm extends React.Component<
ShopfloorServiceFormProps
& InjectedFormProps<ShopfloorServiceFormData, ShopfloorServiceFormProps>> {
  render() {
    const {
      handleSubmit,
      handleTestConnection,
      schema,
      reset,
    } = this.props;

    return (
      <form onSubmit={handleSubmit}>
        <CardContent>
          <RenderFields schema={schema} />
        </CardContent>
        <CardActions>
          <Button onClick={reset}>
            Discard Changes
          </Button>
          <Button type="submit" color="primary">
            Deploy
          </Button>
          <Button
            type="submit"
            color="primary"
            onClick={handleTestConnection}
            data-testid="deploy-test-btn"
          >
            Deploy & Test
          </Button>
        </CardActions>
      </form>
    );
  }
}

export default reduxForm<ShopfloorServiceFormData, ShopfloorServiceFormProps>(
  {})(ShopfloorServiceForm);
