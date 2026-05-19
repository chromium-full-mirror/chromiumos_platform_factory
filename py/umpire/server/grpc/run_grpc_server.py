#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A gRPC server to communicate with DUTs.

To add a new grpc servicer,
  1. define a new proto file,
  2. generate its binding files,
  3. import binding files in this script,
  4. call add_YourNewServicer_to_server in StartGrpcServer.

"""

import argparse
from concurrent import futures
import dataclasses
import logging
import typing
from typing import Optional

import grpc
import grpc._server

from cros.factory.umpire.server.grpc import shop_floor_servicer
from cros.factory.umpire.server.grpc import umpire_dut_commands_servicer
from cros.factory.umpire.server.proto import shop_floor_pb2_grpc
from cros.factory.umpire.server.proto import umpire_dut_commands_pb2_grpc


DEFAULT_SERVER_ADDRESS = '0.0.0.0:8289'


@dataclasses.dataclass(frozen=True)
class RunGrpcArgs:
  address: str = ''
  keyfile: Optional[str] = None
  certfile: Optional[str] = None
  root_certfile: Optional[str] = None
  log_file: Optional[str] = None
  shopfloor_service_url: str = ''
  umpire_cli_url: str = ''


def SetupConnection(grpc_server: grpc._server._Server, args: RunGrpcArgs):
  if args.keyfile and args.certfile:
    with open(args.keyfile, 'rb') as f:
      key_data = f.read()
    with open(args.certfile, 'rb') as f:
      certificate_data = f.read()
    root_cert_data = None
    if args.root_certfile:
      with open(args.root_certfile, 'rb') as f:
        root_cert_data = f.read()

    server_credentials = grpc.ssl_server_credentials(
        [(key_data, certificate_data)],
        root_cert_data,
    )
    grpc_server.add_secure_port(args.address, server_credentials)
  else:
    grpc_server.add_insecure_port(args.address)


def StartGrpcServer(args: RunGrpcArgs):
  log_format = '%(asctime)s %(levelname)s %(message)s'
  logging.basicConfig(level=logging.DEBUG, format=log_format,
                      filename=args.log_file)

  grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
  shop_floor_pb2_grpc.add_ShopFloorServicer_to_server(
      shop_floor_servicer.ShopFloorServicer(args.shopfloor_service_url),
      grpc_server)
  umpire_dut_commands_pb2_grpc.add_UmpireDUTCommandsServicer_to_server(
      umpire_dut_commands_servicer.UmpireDUTCommandsServicer(
          args.umpire_cli_url), grpc_server)

  SetupConnection(grpc_server, args)

  grpc_server.start()
  grpc_server.wait_for_termination()


def main():
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '-a', '--address', metavar='ADDR', default=DEFAULT_SERVER_ADDRESS,
      help=f'address to bind (default: {DEFAULT_SERVER_ADDRESS})')
  parser.add_argument('--keyfile', type=str, default=None,
                      help='Use this for tls.')
  parser.add_argument('--certfile', type=str, default=None,
                      help='Use this for tls.')
  parser.add_argument('--root-certfile', type=str, default=None,
                      help='Use this for tls.')
  parser.add_argument('--log-file', type=str, default=None,
                      help='File to store the log.')
  parser.add_argument('--shopfloor-service-url', type=str, default='',
                      help='The shopfloor service url.')
  parser.add_argument('--umpire-cli-url', type=str, default='',
                      help='The umpire cli url.')
  args = parser.parse_args()
  StartGrpcServer(typing.cast(RunGrpcArgs, args))


if __name__ == "__main__":
  main()
