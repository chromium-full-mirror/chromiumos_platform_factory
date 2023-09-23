// Copyright 2023 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {getDocument, queries} from 'pptr-testing-library';
import {Browser, ElementHandle, Page} from 'puppeteer';

import {setupBrowser, setupNewPage} from '@app/__tests__/setup_utils';

const {getByTestId} = queries;

/**
 * An e2e test for home page (project list)
 */
describe('an e2e test for home page (project list)', () => {
  let browser: Browser;
  let page: Page;
  let document: ElementHandle;

  beforeAll(async () => {
    browser = await setupBrowser();
  });

  beforeEach(async () => {
    page = await setupNewPage(browser);
    document = await getDocument(page);
  });

  test('the project list is empty at initial status', async () => {
    const expectedDescription = 'no projects, create or add an existing one';
    const element = await getByTestId(document, 'no-projects');
    const receivedDescription = await element.evaluate((el) => el.textContent);
    expect(receivedDescription).toBe(expectedDescription);
  });

  afterEach(async () => {
    await page.close();
  });

  afterAll(async () => {
    await browser.close();
  });
});
