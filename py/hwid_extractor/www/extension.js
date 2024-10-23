// Copyright 2024 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

const HWID_EXTRACTOR_ORIGIN = new URLSearchParams(window.location.search).get(
  'openerLocation'
);

function callback() {
  try {
    const authCodeDiv = document.getElementsByClassName('auth-code')[0];
    if (!authCodeDiv) {
      return;
    }

    const codeText = authCodeDiv.textContent.trim();
    const label = 'Unlock Code: ';
    if (!codeText.startsWith(label)) {
      return;
    }

    const code = codeText.slice(label.length);
    window.opener.postMessage(code, HWID_EXTRACTOR_ORIGIN);
    window.close();
  } catch (e) {
    // Alert the error message for debugging.
    alert(e);
  }
}

function main() {
  try {
    const contentArea = document.getElementById('content-area');
    if (!contentArea) {
      throw new Error('Expect #content-area to exist, but not found.');
    }
    const observer = new MutationObserver(callback);
    observer.observe(contentArea, {subtree: true, childList: true});
  } catch (e) {
    // Alert the error message for debugging.
    alert(e);
  }
}

if (window.opener && HWID_EXTRACTOR_ORIGIN) {
  main();
}
