#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unittest for crypto_utils.py."""

import os
import subprocess
from typing import Optional
import unittest

from cros.factory.utils import crypto_utils
from cros.factory.utils import file_utils


_TEST_DATA_PATH = os.path.join(
    os.path.dirname(__file__), 'testdata', 'json_utils_unittest.json')


def OpenSSLAES256Decrypt(data: bytes, key: str,
                         nosalt: Optional[bool] = False) -> bytes:
  cmd = ['openssl', 'aes-256-cbc', '-d', '-pbkdf2', '-base64', '-k', key]
  if nosalt:
    cmd.append('-nosalt')
  p = subprocess.run(cmd, input=data, capture_output=True, check=True)
  return p.stdout


class AES256EncryptTest(unittest.TestCase):

  def testAES256Encrypt(self):
    plaintext = file_utils.ReadFile(_TEST_DATA_PATH).encode()

    ciphertext = crypto_utils.AES256Encrypt(plaintext, 'testkey')
    decrypted_plaintext = OpenSSLAES256Decrypt(ciphertext, 'testkey')
    self.assertEqual(plaintext, decrypted_plaintext)

  def testAES256EncryptWithValidSalt(self):
    plaintext = file_utils.ReadFile(_TEST_DATA_PATH).encode()

    ciphertext = crypto_utils.AES256Encrypt(plaintext, 'testkey', b'12345678')
    decrypted_plaintext = OpenSSLAES256Decrypt(ciphertext, 'testkey')
    self.assertEqual(plaintext, decrypted_plaintext)

  def testAES256EncryptWithInvalidLengthSalt(self):
    plaintext = file_utils.ReadFile(_TEST_DATA_PATH).encode()

    self.assertRaisesRegex(ValueError, r'invalid salt length: \d+ != 8',
                           crypto_utils.AES256Encrypt, plaintext, 'testkey',
                           b'123')

  def testAES256EncryptWithoutSalt(self):
    plaintext = file_utils.ReadFile(_TEST_DATA_PATH).encode()

    ciphertext = crypto_utils.AES256Encrypt(plaintext, 'testkey', b'')
    decrypted_plaintext = OpenSSLAES256Decrypt(ciphertext, 'testkey',
                                               nosalt=True)
    self.assertEqual(plaintext, decrypted_plaintext)


if __name__ == '__main__':
  unittest.main()
