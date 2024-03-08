#!/usr/bin/env python3
#
# Copyright 2017 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Implementation of ChromeOS Factory Shopfloor Service, version 1.0."""

import argparse
import enum
import logging
import socket
import ssl
import sys
from typing import TYPE_CHECKING


DEFAULT_SERVER_PORT = 8090
DEFAULT_SERVER_ADDRESS = '0.0.0.0'


class WebServiceProtocol(enum.Enum):
  xmlrpc = 'xmlrpc'
  soap = 'soap'
  json_soap = 'json_soap'


def main():
  """Main entry when being invoked by command line."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-a', '--address', metavar='ADDR', default=DEFAULT_SERVER_ADDRESS,
      help=f'address to bind (default: {DEFAULT_SERVER_ADDRESS})')
  parser.add_argument('-p', '--port', metavar='PORT', type=int,
                      default=DEFAULT_SERVER_PORT,
                      help=f'port to bind (default: {DEFAULT_SERVER_PORT})')
  parser.add_argument('-v', '--verbose', default=False, action='store_true',
                      help='provide verbose logs for debugging.')
  parser.add_argument('--protocol', type=WebServiceProtocol,
                      default=WebServiceProtocol.xmlrpc,
                      help='Use for different output protocol.')
  parser.add_argument('--keyfile', type=str, default=None,
                      help='Use this for ssl.')
  parser.add_argument('--certfile', type=str, default=None,
                      help='Use this for ssl.')
  args = parser.parse_args()

  log_format = '%(asctime)s %(levelname)s %(message)s'
  logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                      format=log_format)

  # Disable all DNS lookups, since otherwise the logging code may try to
  # resolve IP addresses, which may delay request handling.

  def GetFQDNWithoutDNS(name=''):
    return name or 'localhost'

  socket.getfqdn = GetFQDNWithoutDNS

  keyfile = args.keyfile
  certfile = args.certfile
  use_https = False
  context = None
  if keyfile or certfile:
    if not keyfile or not certfile:
      raise ValueError(f'keyfile={keyfile}, certfile={certfile}')
    use_https = True
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

  try:
    if args.protocol == WebServiceProtocol.xmlrpc:
      if TYPE_CHECKING:
        from cros.factory.shopfloor import xmlrpc_shopfloor_service
      else:
        import xmlrpc_shopfloor_service
      # pylint: disable=used-before-assignment
      xmlrpc_shopfloor_service.RunAsServer(
          address=args.address,
          port=args.port,
          logRequest=args.verbose,
          use_https=use_https,
          context=context,
      )
      # pylint: enable=used-before-assignment
    elif args.protocol == WebServiceProtocol.soap:
      try:
        if TYPE_CHECKING:
          from cros.factory.shopfloor import soap_shopfloor_service
        else:
          import soap_shopfloor_service
      except ImportError:
        logging.exception('The python package spyne is not installed.')
        sys.exit(1)
      # pylint: disable=used-before-assignment
      soap_shopfloor_service.RunAsSoapServer(
          address=args.address,
          port=args.port,
          use_https=use_https,
          context=context,
      )
      # pylint: enable=used-before-assignment
    else:
      try:
        if TYPE_CHECKING:
          from cros.factory.shopfloor import json_soap_shopfloor_service
        else:
          import json_soap_shopfloor_service
      except ImportError:
        logging.exception('The python package spyne is not installed.')
        sys.exit(1)
      # pylint: disable=used-before-assignment
      json_soap_shopfloor_service.RunAsSoapServer(
          address=args.address,
          port=args.port,
          use_https=use_https,
          context=context,
      )
      # pylint: enable=used-before-assignment
  finally:
    logging.warning('Server stopped.')


if __name__ == '__main__':
  main()
