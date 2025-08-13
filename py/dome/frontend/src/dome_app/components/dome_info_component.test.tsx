// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom';
import {render, screen} from '@testing-library/react';
import React from 'react';

import DomeInfoComponent from '@app/dome_app/components/dome_info_component';
import {DomeInfo} from '@app/dome_app/types';
import {createTheme, ThemeProvider} from '@mui/material/styles';

/**
 * DomeInfoComponent component test.
 */
describe('DomeInfoComponent', () => {
  const renderComponent = (domeInfo: DomeInfo | null) => {
    const theme = createTheme();
    return render(
      <ThemeProvider theme={theme}>
        <DomeInfoComponent domeInfo={domeInfo} />
      </ThemeProvider>,
    );
  };

  it('should render "(unknown)" when domeInfo is null', () => {
    renderComponent(null);
    expect(screen.getByText(/(unknown)/i)).toBeInTheDocument();
  });

  it('should render timestamp and hash when domeInfo is provided', () => {
    renderComponent({
      dockerImageGithash: 'abcdef123456',
      dockerImageIslocal: false,
      dockerImageTimestamp: '123456789',
      dockerImageLatestVersion: '',
      isDevServer: false,
    });
    expect(screen.getByText(/123456789/i)).toBeInTheDocument();
    expect(screen.getByText(/abcdef123456/i)).toBeInTheDocument();
  });

  it('should render "(local)" when dockerImageIslocal is true', () => {
    renderComponent({
      dockerImageGithash: 'abcdef123456',
      dockerImageIslocal: true,
      dockerImageTimestamp: '123456789',
      dockerImageLatestVersion: '',
      isDevServer: false,
    });
    expect(screen.getByText(/(local)/i)).toBeInTheDocument();
  });

  it('should render "DEV SERVER" when isDevServer is true', () => {
    renderComponent({
      dockerImageGithash: 'abcdef123456',
      dockerImageIslocal: false,
      dockerImageTimestamp: '123456789',
      dockerImageLatestVersion: '',
      isDevServer: true,
    });
    expect(screen.getByText(/DEV SERVER/i)).toBeInTheDocument();
  });
});
