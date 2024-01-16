# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Cryptography utilities.

This module provides utilities related to cryptography.
"""

import base64
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


_OPENSSL_MAGIC = b'Salted__'


def AES256Encrypt(data: bytes, key: str, salt: Optional[bytes] = None) -> bytes:
  """Encrypt data with AES-256-CBC.

  This function encrypts data using AES-256-CBC and encode to base64 format.
  The result is compatible with openssl command.  Equivalent openssl command::

    openssl enc -aes256 -base64 -pbkdf2 -k <key> -S <salt>

  Args:
    data: the input to be encrypted.
    key: passphrase used for key generation.
    salt: a 8-byte string to use for better protection from dictionary attacks.
        A random salt will be used if None is given.  Will not use salt if an
        empty byte string is given.

  Returns:
    A ciphertext in base64 format.

  Raises:
    ValueError: If the length of salt is invalid.
  """
  if salt is None:
    salt = get_random_bytes(8)
  elif salt and len(salt) != 8:
    raise ValueError(f'invalid salt length: {len(salt)} != 8')
  gen_key = PBKDF2(key, salt, dkLen=32 + 16, count=10000,
                   hmac_hash_module=SHA256)
  gen_key, iv = gen_key[:32], gen_key[32:]

  cipher = AES.new(gen_key, AES.MODE_CBC, iv=iv)
  ciphertext = cipher.encrypt(pad(data, AES.block_size))
  # Do not prepend the magic string if a salt is not used.
  magic_salt = b'' if salt == b'' else _OPENSSL_MAGIC + salt
  return base64.encodebytes(magic_salt + ciphertext)
