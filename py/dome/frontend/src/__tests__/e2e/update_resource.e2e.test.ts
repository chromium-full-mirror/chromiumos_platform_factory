// Copyright 2025 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import md5File from 'md5-file';
import path from 'path';
import {getDocument, queries} from 'pptr-testing-library';
import {Browser, ElementHandle, Page} from 'puppeteer';

import {setupBrowser, setupNewPage} from '@app/__tests__/setup_utils';

const {getByTestId, getByText} = queries;

/**
 * An e2e test for update resources
 */
describe('an e2e test for update resources', () => {
  let browser: Browser;
  let page: Page;
  let document: ElementHandle;

  beforeAll(async () => {
    browser = await setupBrowser();
    page = await setupNewPage(browser);
    document = await getDocument(page);
  });

  test('switch a project', async () => {
    // switch a project
    const projectSelector = 'project-0';
    await page.waitForSelector(`[data-testid="${projectSelector}"]`);
    const projectElement = await getByTestId(document, projectSelector);
    await projectElement.click();

    // check the port text exist in the document
    const portNumber = '1111';
    const expectString = `port: ${portNumber}`;
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toEqual(expectString);
  });

  test('update resource with a bundle to an umpire project', async () => {
    // go to "Bundles" page
    const mentitemElement = await getByText(document, 'Bundles');
    await mentitemElement.click();

    // expand the existing bundle
    const correctBundleName = 'fake_bundle_name';
    await page.waitForSelector(
      `[data-testid="bundle-content-${correctBundleName}"]`);
    const cardElement =
      await getByTestId(document, `bundle-content-${correctBundleName}`);
    await cardElement.click();
    await page.waitForTimeout(1000);

    // update a resource
    const resourceName = 'netboot_cmdline';
    const [fileChooser] = await Promise.all([
      page.waitForFileChooser(),
      await page.click(`[data-testid="bundle-content-${correctBundleName}"]
        + div [data-testid="resource-download-${resourceName}"]
        [data-testid="PublishIcon"]`),
    ]);
    const filePath = 'testdata/cmdline';
    const resourcePath = path.join(__dirname, filePath);
    await fileChooser.accept([resourcePath]);
    await page.waitForTimeout(1000);

    // confirm to update resource
    await page.click('.MuiDialogActions-root > button:nth-child(1)');
    await page.waitForTimeout(3000);

    // download a resource
    type ResolversType = (value: string) => void;
    interface DownloadsType {
      resolvers: Set<ResolversType>;
      filename: string;
    }
    const downloadFolder = '/tmp/download';
    const browserClient = await browser.target().createCDPSession();
    const downloads = new Map<string, DownloadsType>();
    let downloadResolvers = new Set<ResolversType>();
    await browserClient.send('Browser.setDownloadBehavior', {
      behavior: 'allow',
      downloadPath: downloadFolder,
      eventsEnabled: true,
    });
    const download = async (resource: string) => {
      browserClient.on('Browser.downloadWillBegin', ((event) => {
        if (downloadResolvers.size > 0) {
          downloads.set(event.guid, {
            resolvers: downloadResolvers,
            filename: event.suggestedFilename,
          });
          downloadResolvers = new Set<ResolversType>();
        }
      }));
      browserClient.on('Browser.downloadProgress', ((event) => {
        const {guid} = event;
        if (event.state === 'completed' && downloads.has(guid)) {
          const getDownload: DownloadsType = downloads.get(guid)!;
          const resolvers: Set<ResolversType> = getDownload.resolvers;
          const filename: string = getDownload.filename;
          downloads.delete(guid);
          resolvers.forEach((resolve: ResolversType) => resolve(filename));
        }
      }));
      const downloadPromise = new Promise((resolve: ResolversType) =>
        downloadResolvers.add(resolve));
      await page.click(`[data-testid="resource-download-${resource}"]
        [data-testid="GetAppIcon"]`);
      const fileName = await downloadPromise;
      return await md5File(`${downloadFolder}/${fileName}`);
    };

    // download resources to verify the upload is succeeded
    const resourceHash = '4a9c552e1f65dcfa1922aba7f28b1ea0';
    const md5hash = await download(resourceName);
    expect(md5hash).toBe(resourceHash);
  }, 60000);

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
