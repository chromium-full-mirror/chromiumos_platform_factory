// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {getDocument, queries} from 'pptr-testing-library';
import {Browser, ElementHandle, Page} from 'puppeteer';

import config from '@app/__tests__/e2e/e2e_config';
import {setupBrowser, setupNewPage} from '@app/__tests__/setup_utils';

const {getByRole, getByTestId, getByText} = queries;

/**
 * An e2e test for downloading or cleaning the csv from factory server
 */
describe('an e2e test for downloading or cleaning the csv', () => {
  let browser: Browser;
  let page: Page;
  let document: ElementHandle;
  const delayOfClick = 1000;

  beforeAll(async () => {
    browser = await setupBrowser();
    page = await setupNewPage(browser);
    document = await getDocument(page);
  });

  test('download csv can succeed', async () => {
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

    // click "CSV" tab
    await page.click('#logForm .MuiCardContent-root button:nth-child(3)');

    // switch to "download" csv section
    await page.click('[role="button"]');
    const downloadOption = '[data-value="download"]';
    await page.click(downloadOption);
    await page.waitForTimeout(delayOfClick);

    // click "download" button
    const downloadButton = '[type="submit"]';
    await page.click(downloadButton);

    const expectString = `${config.umpireFakeProjectName}-csv.tar.bz2`;
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toEqual(expectString);
  });

  test('cleanup csv is succeed', async () => {
    // switch to "cleanup" csv section
    await page.click('[role="button"]');
    const cleanupOption = '[data-value="cleanup"]';
    await page.click(cleanupOption);
    await page.waitForTimeout(delayOfClick);

    // click "cleanup" button
    const cleanupButton = '#logForm .MuiCardContent-root > div > button';
    await page.click(cleanupButton);
    await page.waitForTimeout(delayOfClick);

    // click "OK" button
    const confirmButton = '.MuiModal-root.MuiDialog-root button:nth-child(1)';
    await page.click(confirmButton);

    const expectString = 'CSV file removed successfully';
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toEqual(expectString);
  }, 60000);

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
