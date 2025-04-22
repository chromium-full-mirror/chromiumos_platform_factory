// Copyright 2024 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import '@testing-library/jest-dom/extend-expect';
import {fireEvent, RenderResult} from '@testing-library/react';
import React from 'react';

import {wrappedRender} from '@app/__tests__/utils_wrapper';
import FileUploadDialog from '@common/components/file_upload_dialog';

/**
 * FileUploadDialog component test.
 */
describe('FileUploadDialog', () => {
  const mockOpenFn: any = jest.fn().mockReturnValue(true);
  const mockOnCancelFn = jest.fn();
  const mockOnSubmitFn = jest.fn();
  const mockSubmitFormFn = jest.fn();
  const rows = ['ChromeOS', 'ChromeOS Factory', 'ChromeOS Factory DOME'];
  const file = new File([rows.join('\n')], 'cros.csv');
  let FileUploadDialogDOM: RenderResult;

  beforeEach(() => {
    FileUploadDialogDOM = wrappedRender(
      <FileUploadDialog
        open={mockOpenFn}
        title="Update Factory Drive"
        onCancel={mockOnCancelFn}
        onSubmit={mockOnSubmitFn}
        submitForm={mockSubmitFormFn}
        multiple
      >
        <form>
          <button type="submit">Test onSubmit</button>
        </form>
      </FileUploadDialog>,
    );
  });

  test('verify that FileUploadDialog dom node is correct', () => {
    expect(FileUploadDialogDOM).toBeDefined();
  });

  test('verify that uploading multiple files is correct', () => {
    const {container, getByText} = FileUploadDialogDOM;
    const fileInput = container.querySelector('input[type="file"]')!;
    fireEvent.change(fileInput, {type: 'file', target: {files: [file, file]}});
    fireEvent.submit(getByText('Test onSubmit'));
    expect(mockOnSubmitFn).toHaveBeenCalled();

    fireEvent.click(getByText('confirm'));
    expect(mockSubmitFormFn).toHaveBeenCalled();
  });

  test('verify that uploading single file is correct', () => {
    const {container, getByText, rerender} = FileUploadDialogDOM;
    rerender(
      <FileUploadDialog
        open={mockOpenFn}
        title="Update Factory Drive"
        onCancel={mockOnCancelFn}
        onSubmit={mockOnSubmitFn}
        submitForm={mockSubmitFormFn}
        multiple={false}
      >
        <form>
          <button type="submit">Test onSubmit</button>
        </form>
      </FileUploadDialog>,
    );

    const fileInput = container.querySelector('input[type="file"]')!;
    fireEvent.change(fileInput, {type: 'file', target: {files: [file]}});
    fireEvent.submit(getByText('Test onSubmit'));
    expect(mockOnSubmitFn).toHaveBeenCalled();

    fireEvent.click(getByText('confirm'));
    expect(mockSubmitFormFn).toHaveBeenCalled();
  });
});
