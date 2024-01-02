// Copyright 2024 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

const body = document.getElementById('body');

/**
 * Update display state.
 *
 * @param {str} imageUrl
 */
const updateDisplay = async (imageUrl) => {
  if(imageUrl === '') {
    body.innerHTML = ''
  } else {
    const img = goog.dom.createDom(
      'img', {'class': 'fullscreen-image', 'src': imageUrl});
    body.appendChild(img);
  }
};

window.updateDisplay = updateDisplay;
