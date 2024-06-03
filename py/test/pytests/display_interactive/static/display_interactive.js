// Copyright 2024 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/**
 * API for display interactive test.
 */
class DisplayInteractiveTest {
  /**
   * Constructor for DisplayInteractiveTest.
   */
  constructor() {
    this.fullscreen = false;
    this.fullscreenElement = document.getElementById("display-full-screen");
    this.displayDiv = document.getElementById("display-div");
    // Add transition for smooth changes.
    this.displayDiv.style.transition =
      "background-image 0.2s ease-in-out, background-color 0.2s ease-in-out";
  }

  /**
   * Toggles the fullscreen display.
   */
  toggleFullscreen() {
    this.fullscreen = !this.fullscreen;
    this.fullscreenElement.classList.toggle("hidden", !this.fullscreen);
    window.test.setFullScreen(this.fullscreen);
  }

  /**
   * Shows a display pattern.
   * @param {string} patternType The type of pattern to show
   *     (css, image, message).
   * @param {string} pattern The pattern to apply.
   *     - For css: Class name to apply to displayDiv.
   *     - For image: Image path relative to the current file.
   *     - For message: Message to display.
   */
  showPattern(patternType, pattern) {
    this._clearDisplay();
    // Map pattern types to actions.
    const patternActions = {
      css: () => this.displayDiv.classList.add(pattern),
      image: () => {
        this.displayDiv.style.backgroundImage = `url(./${pattern})`;
        this.displayDiv.classList.add("custom-image");
      },
      message: () => {
        const textMessageDiv = document.createElement("div");
        textMessageDiv.classList.add("text-message");
        textMessageDiv.textContent = pattern;
        this.displayDiv.appendChild(textMessageDiv);
      },
    };
    const action = patternActions[patternType];
    // Execute the action if it exists.
    action?.();
  }

  /**
   * Clears the display, removing any applied styles or images.
   */
  _clearDisplay() {
    // Remove all classes from the display div.
    this.displayDiv.classList.remove(...this.displayDiv.classList);
    this.displayDiv.style.backgroundImage = "";
    this.displayDiv.classList.remove("custom-image");
    const textMessageElements =
      this.displayDiv.querySelectorAll(".text-message");
    textMessageElements.forEach((element) => element.remove());
  }
}

window.DisplayInteractiveTest = DisplayInteractiveTest;
