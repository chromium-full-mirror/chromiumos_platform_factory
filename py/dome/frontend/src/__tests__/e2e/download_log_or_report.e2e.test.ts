// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import dateFormat from 'dateformat';
import {getDocument, queries} from 'pptr-testing-library';
import {Browser, ElementHandle, Page} from 'puppeteer';

import config from '@app/__tests__/e2e/e2e_config';
import {setupBrowser, setupNewPage} from '@app/__tests__/setup_utils';

const {getByRole, getByTestId, getByText} = queries;

/**
 * An e2e test for downloading or cleaning the log/report from factory server
 */
describe('an e2e test for downloading or cleaning the log/report', () => {
  let browser: Browser;
  let page: Page;
  let document: ElementHandle;
  const now = new Date();
  const date = dateFormat(now, 'yyyymmdd');
  const dateForInput = dateFormat(now, 'mmddyyyy');

  beforeAll(async () => {
    browser = await setupBrowser();
    page = await setupNewPage(browser);
    document = await getDocument(page);
  });

  test('download reports can succeed', async () => {
    // switch to home page
    const mentitemElement = await getByText(document, 'Select project');
    await mentitemElement.click();

    // switch a project
    const projectSelector = 'project-0';
    await page.waitForSelector(`[data-testid="${projectSelector}"]`);
    const projectElement = await getByTestId(document, projectSelector);
    await projectElement.click();

    // click "Logs" page
    const menuElement = await getByRole(document, 'menu');
    const logsElement = await getByText(menuElement, 'Logs');
    await logsElement.click();

    // click "Report" tab
    await page.click('#logForm .MuiCardContent-root button:nth-child(2)');

    // switch to "download" reports section
    await page.click('[role="button"]');
    const downloadOption = '[data-value="download"]';
    await page.click(downloadOption);

    // input start date and end date
    await page.type('[name="startDate"]', dateForInput, {delay: 200});
    await page.type('[name="endDate"]', dateForInput, {delay: 200});

    // click "download" button
    const downloadButton = '[type="submit"]';
    await page.click(downloadButton);

    const projectName = config.umpireFakeProjectName;
    const expectString = `${projectName}-${date}-${date}-0.tar.bz2`;
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toEqual(expectString);
  });

  test('cleanup reports is succeed', async () => {
    // switch to "cleanup" reports section
    await page.click('[role="button"]');
    const cleanupOption = '[data-value="cleanup"]';
    await page.click(cleanupOption);

    // input start date and end date
    await page.type('[name="startDate"]', dateForInput, {delay: 200});
    await page.type('[name="endDate"]', dateForInput, {delay: 200});

    // click "cleanup" button
    const cleanupButton = '#logForm .MuiCardContent-root > div > button';
    await page.click(cleanupButton);

    // click "OK" button
    const confirmButton = '.MuiModal-root.MuiDialog-root button:nth-child(1)';
    await page.click(confirmButton);

    const expectString = 'File removed successfully';
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toEqual(expectString);
  });

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
