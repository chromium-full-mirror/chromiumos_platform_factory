// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import puppeteer, {Browser} from 'puppeteer';

import config from '@app/__tests__/e2e/e2e_config';

export const setupBrowser = async () => {
  return await puppeteer.launch({
    headless: 'new',
    executablePath: 'google-chrome-stable',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
    ],
  });
};

export const setupNewPage = async (browser: Browser) => {
  const page = await browser.newPage();
  await page.setViewport({
    width: config.pageWidth,
    height: config.pageHeight,
  });
  await page.goto(config.url);
  return page;
};
