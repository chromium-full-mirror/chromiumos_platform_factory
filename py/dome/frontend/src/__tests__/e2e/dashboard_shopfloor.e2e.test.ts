// Copyright 2024 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {getDocument, queries} from 'pptr-testing-library';
import {Browser, ElementHandle, Page} from 'puppeteer';

import config from '@app/__tests__/e2e/e2e_config';
import {setupBrowser, setupNewPage} from '@app/__tests__/setup_utils';

const {getByTestId, getByText} = queries;

/**
 * An e2e test for testing connection of shopfloor service
 */
describe('an e2e test for testing connection of shopfloor service', () => {
  let browser: Browser;
  let page: Page;
  let document: ElementHandle;

  beforeAll(async () => {
    browser = await setupBrowser();
    page = await setupNewPage(browser);
    document = await getDocument(page);
  });

  test('create a new project correctly', async () => {
    // input the fake project name
    const inputSelector = 'input[name="name"]';
    await page.waitForSelector(inputSelector);
    await page.type(inputSelector, config.umpireFakeProjectName);

    // click the "create a new project" button
    const buttonSelector = 'button[type="submit"]';
    await page.waitForSelector(buttonSelector);
    await page.click(buttonSelector);

    // get the project name from project list
    const projectNameTestId = 'project-name-0';
    await page.waitForSelector(`[data-testid="${projectNameTestId}"]`);
    const element = await getByTestId(document, projectNameTestId);
    const projectName = await element.evaluate((el) => el.textContent);
    expect(projectName).toBe(config.umpireFakeProjectName);
  });

  test('enable a project', async () => {
    // switch a project
    const projectSelector = 'project-0';
    await page.waitForSelector(`[data-testid="${projectSelector}"]`);
    const projectElement = await getByTestId(document, projectSelector);
    await projectElement.click();

    // click "Enable Umpire" switch button
    const enableSelector = 'input[type="checkbox"]';
    await page.waitForSelector(enableSelector);
    await page.click(enableSelector);

    // clear and input the port number to umpire port field
    const umpirePortSelector = 'input[name="umpirePort"]';
    const portNumber = '1111';
    await page.waitForSelector(umpirePortSelector);
    await page.click(umpirePortSelector);
    await page.keyboard.down('Control');
    await page.keyboard.press('A');
    await page.keyboard.up('Control');
    await page.keyboard.press('Backspace');
    await page.keyboard.type(portNumber, {delay: 100});

    // click button to enable project
    const confirmButtonSelector = 'enable-confirm-btn';
    await page.waitForSelector(`[data-testid="${confirmButtonSelector}"]`);
    const confirmButton = await getByTestId(document, confirmButtonSelector);
    await confirmButton.click();
    const delayOfClick = 1000;
    await page.waitForTimeout(delayOfClick);

    // check the port text exist in the document
    const expectString = `port: ${portNumber}`;
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toBe(expectString);

    // verify the enable umpire is succeed
    const enableUmpireString =
      `Enable Umpire for project "${config.umpireFakeProjectName}"`;
    const enableUmpireElement = await getByText(document, enableUmpireString);
    const taskIconTestid = await enableUmpireElement.evaluate((el) => {
      const icon = el.nextElementSibling?.nextElementSibling?.firstElementChild;
      return icon?.getAttribute('data-testid');
    });
    expect(taskIconTestid).toBe('CheckCircleIcon');
  });

  test('test shopfloor connection', async () => {
    // expend shopfloor services
    const shopfloorTitleSelector = 'service-title-shopFloor';
    await page.waitForSelector(`[data-testid="${shopfloorTitleSelector}"]`);
    const shopfloorCard = await getByTestId(document, shopfloorTitleSelector);
    await shopfloorCard.click();

    // click "active" switch button
    const shopfloorTestid = '[data-testid="service-shopFloor"]';
    const activeBtn = `${shopfloorTestid} .MuiSwitch-root`;
    await page.waitForSelector(`${shopfloorTestid}.MuiCollapse-entered`);
    await page.waitForSelector(activeBtn);
    await page.click(activeBtn);
    const selector = `${shopfloorTestid} .MuiSwitch-switchBase`;
    const activeBtnElement = await page.$(selector);
    const activeBtnIsChecked = await activeBtnElement?.evaluate((el) => {
      return el.className.includes('Mui-checked');
    });
    expect(activeBtnIsChecked).toBe(true);

    // input serviceUrl data
    const serviceUrlElement = 'input[name="serviceUrl"]';
    const serviceUrl = 'http://localhost:8091';
    await page.waitForSelector(serviceUrlElement);
    // Set the typing delay as 200ms, because every test needs to wait around
    // 1 second for deploying (enabling) the umpire project.
    await page.type(serviceUrlElement, serviceUrl, {delay: 200});
    const urlElement = await page.$(serviceUrlElement);
    const receivedUrl = await urlElement?.evaluate((el) => {
      return el.value;
    });
    expect(receivedUrl).toBe(serviceUrl);

    // click "DEPLOY & TEST" button
    const testBtnSelector = 'deploy-test-btn';
    await page.waitForSelector(`[data-testid="${testBtnSelector}"]`);
    const testBtn = await getByTestId(document, testBtnSelector);
    await testBtn.click();

    // verify the shopfloor service connection is succeed
    const testConnectString = 'test connection of "shopFloor" service';
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
