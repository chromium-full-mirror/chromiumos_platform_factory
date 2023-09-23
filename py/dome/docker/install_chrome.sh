#!/bin/bash
# Copyright 2023 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

if [ -n "${dome_dev_run}" ] && [ "${dome_dev_run}" = "true" ]; then
  # Install latest chrome dev package.
  # Note: this installs the necessary libs to make the bundled version of
  # Chrome that Puppeteer installs, work.
  apt-get update \
  && apt-get install -y wget gnupg \
  && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
  && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
  && apt-get update \
  && apt-get install -y google-chrome-stable libxss1 --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*
fi
