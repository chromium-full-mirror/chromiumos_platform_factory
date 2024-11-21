// Copyright 2024 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom/extend-expect';
import {RenderResult} from '@testing-library/react';
import React from 'react';

import {wrappedRender} from '@app/__tests__/utils_wrapper';
import ConfigApp from '@app/config/components/config_app';

/**
 * ConfigApp component test.
 */
describe('ConfigApp', () => {
  let ConfigAppDOM: RenderResult;

  beforeEach(() => {
    ConfigAppDOM = wrappedRender(
      <ConfigApp />,
    );
  });

  test('verify that ConfigApp dom node is correct', () => {
    expect(ConfigAppDOM).toBeDefined();
  });
});
