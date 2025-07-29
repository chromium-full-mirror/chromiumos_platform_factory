// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {getDocument, queries} from 'pptr-testing-library';
import {Browser, ElementHandle, Page} from 'puppeteer';

import {setupBrowser, setupNewPage} from '@app/__tests__/setup_utils';

const {getByRole, getByTestId, getByText} = queries;

/**
 * An e2e test for changing the timezone on specific umpire project
 */
describe('an e2e test for changing the timezone on umpire project', () => {
  let browser: Browser;
  let page: Page;
  let document: ElementHandle;
  const delayOfClick = 1000;

  beforeAll(async () => {
    browser = await setupBrowser();
    page = await setupNewPage(browser);
    document = await getDocument(page);
  });

  test('switch a project to Dashboard page', async () => {
    // switch to home page
    const mentitemElement = await getByText(document, 'Select project');
    await mentitemElement.click();

    // switch a project
    const projectSelector = 'project-0';
    await page.waitForSelector(`[data-testid="${projectSelector}"]`);
    const projectElement = await getByTestId(document, projectSelector);
    await projectElement.click();

    // click "Dashboard" page
    const menuElement = await getByRole(document, 'menu');
    const dashboardElement = await getByText(menuElement, 'Dashboard');
    await dashboardElement.click();
  });

  test('update umpireTimezone service is succeed', async () => {
    // expend umpireTimezone services
    const umpireTimezoneTitle = 'service-title-umpireTimezone';
    await page.waitForSelector(`[data-testid="${umpireTimezoneTitle}"]`);
    const umpireTimezoneCard = await getByTestId(document, umpireTimezoneTitle);
    await umpireTimezoneCard.click();

    // click "active" switch button
    const umpireTimezoneTestid = '[data-testid="service-umpireTimezone"]';
    const activeBtn = `${umpireTimezoneTestid} .MuiSwitch-root`;
    await page.waitForSelector(`${umpireTimezoneTestid}.MuiCollapse-entered`);
    await page.waitForSelector(activeBtn);
    await page.click(activeBtn);
    const selector = `${umpireTimezoneTestid} .MuiSwitch-switchBase`;
    const activeBtnElement = await page.$(selector);
    const activeBtnIsChecked = await activeBtnElement?.evaluate((el) => {
      return el.className.includes('Mui-checked');
    });
    expect(activeBtnIsChecked).toBe(true);

    // input timezone data
    const timezoneElement = 'input[name="timezone"]';
    const timezone = '8';
    await page.waitForSelector(timezoneElement);
    // Set the typing delay as 200ms, because every test needs to wait around
    // 1 second for deploying (enabling) the umpire project.
    await page.type(timezoneElement, timezone, {delay: 200});
    const receivedTimezoneElement = await page.$(timezoneElement);
    const receivedTimezone = await receivedTimezoneElement?.evaluate((el) => {
      return el.value;
    });
    expect(receivedTimezone).toBe(timezone);

    // click "DEPLOY" button
    const deployButton = `${umpireTimezoneTestid} [type="submit"]`;
    await page.click(deployButton);
    await page.waitForTimeout(delayOfClick);

    // verify update "umpireTimezone" service is succeed
    const testConnectString = 'update "umpireTimezone" service';
    const testConnectElement = await getByText(document, testConnectString);
    const taskIconTestid = await testConnectElement.evaluate((el) => {
      const icon = el.nextElementSibling?.nextElementSibling?.firstElementChild;
      return icon?.getAttribute('data-testid');
    });
    expect(taskIconTestid).toBe('CheckCircleIcon');
  }, 10000);

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
