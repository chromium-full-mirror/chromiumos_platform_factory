#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""This script generates self-signed keys for TLS.

1. It creates a separate Certificate Authority (CA): ca.key, ca.crt
2. It generates a key for your server: server.key
3. It generates a Certificate Signing Request (CSR) with server.key: server.csr
4. It uses the CA to sign the CSR: server.crt
5. It converts server.key into pem format: server.pem

Usage:
1. Run the server with server.key (or server.pem) and server.crt.
2. To verify the server, your client must trust our CA by adding ca.crt into the
   trusted list.

Each CA owns its ca.key. We can pay CA to get them signed our server.csr and
will generate different server.crt.

Self-signed means that we are our own CA, so we generate our own ca.key.

This script requires openssl.
"""

import argparse
import dataclasses
import logging
import os
import subprocess
import tempfile
import typing
from typing import Optional


@dataclasses.dataclass(frozen=True)
class GenerateArgs:
  out: str
  ip: Optional[str]
  dns: Optional[str]
  verbose: bool


def Create(args: GenerateArgs):
  ca_key = os.path.join(args.out, 'ca.key')
  ca_cert = os.path.join(args.out, 'ca.crt')
  subprocess.run([
      'openssl', 'genrsa', '-passout', 'pass:ca', '-des3', '-out', ca_key,
      '4096'
  ], check=True)
  subprocess.run([
      'openssl', 'req', '-passin', 'pass:ca', '-new', '-x509', '-days', '365',
      '-subj', '/C=US/O=CA', '-key', ca_key, '-out', ca_cert
  ], check=True)

  if args.verbose:
    subprocess.run(['openssl', 'x509', '-noout', '-text', '-in', ca_cert],
                   check=True)

  server_key = os.path.join(args.out, 'server.key')
  server_cert_request = os.path.join(args.out, 'server.csr')

  subprocess.run([
      'openssl', 'genrsa', '-passout', 'pass:server', '-des3', '-out',
      server_key, '4096'
  ], check=True)
  subprocess.run([
      'openssl', 'req', '-passin', 'pass:server', '-new', '-subj',
      '/C=US/O=SERVER', '-key', server_key, '-out', server_cert_request
  ], check=True)

  if args.verbose:
    subprocess.run(
        ['openssl', 'req', '-noout', '-text', '-in', server_cert_request],
        check=True)

  server_cert = os.path.join(args.out, 'server.crt')

  with tempfile.TemporaryDirectory(prefix='self_signed') as dir_path:
    ext_path = os.path.join(dir_path, 'ext')
    with open(ext_path, 'w', encoding='utf-8') as f:
      if args.ip:
        f.write(f'subjectAltName = IP:{args.ip}\n')
      if args.dns:
        f.write(f'subjectAltName = DNS:{args.dns}\n')

    subprocess.run([
        'openssl', 'x509', '-req', '-extfile', ext_path, '-days', '365',
        '-passin', 'pass:ca', '-CAkey', ca_key, '-CA', ca_cert, '-set_serial',
        '01', '-in', server_cert_request, '-out', server_cert
    ], check=True)

  if args.verbose:
    subprocess.run(['openssl', 'x509', '-noout', '-text', '-in', server_cert],
                   check=True)

  # Convert the private key to nocrypt.
  # Check https://github.com/grpc/grpc/issues/14216.
  subprocess.run([
      'openssl', 'pkcs8', '-topk8', '-nocrypt', '-passin', 'pass:server', '-in',
      server_key, '-out',
      os.path.join(args.out, 'server.pem')
  ], check=True)


def main():
  logging.basicConfig(level=logging.INFO)

  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('--out', type=str, default='.', help='Output directory.')
  parser.add_argument('--ip', type=str, default=None, help='Server IP.')
  parser.add_argument('--dns', type=str, default=None, help='Server DNS.')
  parser.add_argument('--verbose', action='store_true',
                      help='Print out the generated certificate.')
  args = parser.parse_args()

  Create(typing.cast(GenerateArgs, args))


if __name__ == '__main__':
  main()
