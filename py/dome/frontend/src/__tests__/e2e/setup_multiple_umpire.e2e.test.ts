// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import {getDocument, queries} from 'pptr-testing-library';
import {Browser, ElementHandle, Page} from 'puppeteer';

import config from '@app/__tests__/e2e/e2e_config';
import {setupBrowser, setupNewPage} from '@app/__tests__/setup_utils';

const {getByRole, getByTestId, getByText} = queries;

/**
 * An e2e test for setup multiple umpire projects
 */
describe('an e2e test for setup multiple umpire projects', () => {
  let browser: Browser;
  let page: Page;
  let document: ElementHandle;
  const pirmaryPortNumber = '1111';
  const secondaryPortNumber = '2222';
  const dockerHostIp = '172.18.0.1';
  const delayOfClick = 1000;

  beforeAll(async () => {
    browser = await setupBrowser();
    page = await setupNewPage(browser);
    document = await getDocument(page);
  });

  test('create a new project for secondary information', async () => {
    // input the fake project name
    const inputSelector = 'input[name="name"]';
    await page.waitForSelector(inputSelector);
    await page.type(inputSelector, config.umpireFakeSecondary);

    // click the "create a new project" button
    const buttonSelector = 'button[type="submit"]';
    await page.waitForSelector(buttonSelector);
    await page.click(buttonSelector);

    // get the project name from project list
    const projectNameTestId = 'project-name-1';
    await page.waitForSelector(`[data-testid="${projectNameTestId}"]`);
    const element = await getByTestId(document, projectNameTestId);
    const projectName = await element.evaluate((el) => el.textContent);
    expect(projectName).toBe(config.umpireFakeSecondary);
  });

  test('enable the secondary project', async () => {
    // switch a project
    const projectSelector = 'project-1';
    await page.waitForSelector(`[data-testid="${projectSelector}"]`);
    const projectElement = await getByTestId(document, projectSelector);
    await projectElement.click();

    // click "Enable Umpire" switch button
    const enableSelector = 'input[type="checkbox"]';
    await page.waitForSelector(enableSelector);
    await page.click(enableSelector);

    // clear and input the port number to umpire port field
    const umpirePortSelector = 'input[name="umpirePort"]';
    await page.waitForSelector(umpirePortSelector);
    await page.click(umpirePortSelector);
    await page.keyboard.down('Control');
    await page.keyboard.press('A');
    await page.keyboard.up('Control');
    await page.keyboard.press('Backspace');
    await page.keyboard.type(secondaryPortNumber, {delay: 100});

    // click button to enable project
    const confirmButtonSelector = 'enable-confirm-btn';
    await page.waitForSelector(`[data-testid="${confirmButtonSelector}"]`);
    const confirmButton = await getByTestId(document, confirmButtonSelector);
    await confirmButton.click();
    await page.waitForTimeout(delayOfClick);

    // check the port text exist in the document
    const expectString = `port: ${secondaryPortNumber}`;
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toBe(expectString);

    // verify the enable umpire is succeed
    const enableUmpireString =
      `Enable Umpire for project "${config.umpireFakeSecondary}"`;
    const enableUmpireElement = await getByText(document, enableUmpireString);
    const taskIconTestid = await enableUmpireElement.evaluate((el) => {
      const icon = el.nextElementSibling?.nextElementSibling?.firstElementChild;
      return icon?.getAttribute('data-testid');
    });
    expect(taskIconTestid).toBe('CheckCircleIcon');
  });

  test('switch a project and setup multiple umpire projects', async () => {
    // switch to home page
    const mentitemElement = await getByText(document, 'Select project');
    await mentitemElement.click();

    // switch a project
    const projectSelector = 'project-0';
    await page.waitForSelector(`[data-testid="${projectSelector}"]`);
    const projectElement = await getByTestId(document, projectSelector);
    await projectElement.click();

    // click "dismiss all finished tasks" icon button
    await page.click('[aria-label="dismiss all finished tasks"]');
    await page.waitForTimeout(delayOfClick);

    // click "Dashboard" page
    const menuElement = await getByRole(document, 'menu');
    const dashboardElement = await getByText(menuElement, 'Dashboard');
    await dashboardElement.click();

    // expend umpireSync services
    const umpiresyncTitle = 'service-title-umpireSync';
    const umpiresyncTitleSelector = `[data-testid="${umpiresyncTitle}"]`;
    await page.waitForSelector(umpiresyncTitleSelector);
    await page.click(umpiresyncTitleSelector);

    // click "active" switch button
    const umpiresyncTestid = '[data-testid="service-umpireSync"]';
    const activeBtn = `${umpiresyncTestid} .MuiSwitch-root`;
    await page.waitForSelector(activeBtn);
    await page.click(activeBtn);

    // input synchronizeTime
    const synchronizeTimeInput = '[name="synchronizeTime"]';
    await page.waitForSelector(synchronizeTimeInput);
    await page.type(synchronizeTimeInput, '1', {delay: 100});

    // input primaryInformation
    const primaryIpInput = '[name="primaryInformation.ip"]';
    await page.waitForSelector(primaryIpInput);
    await page.type(primaryIpInput, dockerHostIp, {delay: 100});
    const primaryPortInput = '[name="primaryInformation.port"]';
    await page.waitForSelector(primaryPortInput);
    await page.type(primaryPortInput, pirmaryPortNumber, {delay: 100});

    // click "Add" button
    await page.click(`${umpiresyncTestid} [data-testid="AddIcon"]`);

    // input secondaryInformation
    const secondaryIpInput = '[name="secondaryInformation[0].ip"]';
    await page.waitForSelector(secondaryIpInput);
    await page.type(secondaryIpInput, dockerHostIp, {delay: 100});
    const secondaryPortInput = '[name="secondaryInformation[0].port"]';
    await page.waitForSelector(secondaryPortInput);
    await page.type(secondaryPortInput, secondaryPortNumber, {delay: 100});

    // click "DEPLOY" button
    const deployButton = `${umpiresyncTestid} [type="submit"]`;
    await page.click(deployButton);
    await page.waitForTimeout(delayOfClick);

    // go to "Sync Status" page
    const syncStatusPage = await getByText(document, 'Sync Status');
    await syncStatusPage.click();
    await page.waitForTimeout(delayOfClick);

    // check if the sync status is success
    const textToFind = 'Success';
    const textExists = await (await page.$('table'))?.evaluate(
      (el, text) => el.textContent?.includes(text),
      textToFind,
    );
    expect(textExists).toBe(true);
  }, 60000);

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
