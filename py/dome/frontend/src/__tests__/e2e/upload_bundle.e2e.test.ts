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
 * An e2e test for uploading bundle
 */
describe('an e2e test for uploading bundle', () => {
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

  test('upload a bundle', async () => {
    // go to "Bundles" page
    const mentitemElement = await getByText(document, 'Bundles');
    await mentitemElement.click();

    // check the empty bundle text exist in the document
    const expectString = `empty`;
    const textSelector = await page.waitForSelector(
      `text/${expectString}`,
    );
    const actualString = await textSelector?.evaluate((el) => el.textContent);
    expect(actualString).toEqual(expectString);

    // upload bundle file to "Bundles"
    const [fileChooser] = await Promise.all([
      page.waitForFileChooser(),
      (await getByTestId(document, 'upload-factory-bundle')).click(),
    ]);
    const filePath = 'testdata/fake_factory_bundle.tar.bz2';
    const bundlePath = path.join(__dirname, filePath);
    await fileChooser.accept([bundlePath]);
    await page.waitForTimeout(1000);

    // input the fake bundle name
    const correctBundleName = 'fake_bundle_name';
    const nameSelector = 'input[name="name"]';
    await page.waitForSelector(nameSelector);
    await page.type(nameSelector, correctBundleName);

    // input the fake bundle note
    const correctBundleNote = 'fake_bundle_note';
    const noteSelector = 'input[name="note"]';
    await page.waitForSelector(noteSelector);
    await page.type(noteSelector, correctBundleNote);
    await page.click('.MuiDialogActions-root > button:nth-child(1)');
    await page.waitForTimeout(3000);

    // expand the uploaded bundle
    await page.waitForSelector(
      `[data-testid="bundle-content-${correctBundleName}"]`);
    const cardElement =
      await getByTestId(document, `bundle-content-${correctBundleName}`);
    await cardElement.click();
    await page.waitForTimeout(1000);

    // download resources
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
      const md5hash = await md5File(`${downloadFolder}/${fileName}`);
      return md5hash;
    };

    // download resources to verify the upload is succeeded
    const resourceHash = {
      complete: '0e1cd144ed31497d4b84600ba7651dc8',
      firmware: 'abcd08427a0783041e40241a90ae085e',
      netboot_kernel: '82c0d943e472b476d117bbd5418626a1',
      netboot_cmdline: 'd8974e39c07ced15ff955e4e0cb56d08',
      netboot_firmware: 'd02589f02a3cceaeb0e705bae17d9a67',
      toolkit: '8d40de945b7e1ef115da5e63ce88a39a',
    };
    const completeHash = await download('complete');
    expect(completeHash).toBe(resourceHash.complete);
    const firmwareHash = await download('firmware');
    expect(firmwareHash).toBe(resourceHash.firmware);
    const netbootCmdlineHash = await download('netboot_cmdline');
    expect(netbootCmdlineHash).toBe(resourceHash.netboot_cmdline);
    const netbootFirmwareHash = await download('netboot_firmware');
    expect(netbootFirmwareHash).toBe(resourceHash.netboot_firmware);
    const toolkitHash = await download('toolkit');
    expect(toolkitHash).toBe(resourceHash.toolkit);
  }, 60000);

  afterAll(async () => {
    await page.close();
    await browser.close();
  });
});
