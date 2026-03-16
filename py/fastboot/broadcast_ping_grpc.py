#!/usr/bin/env python3
# Copyright 2026 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import asyncio
from collections import defaultdict
import logging
import os
import time
from typing import Set

import grpc
from scapy.all import Ether  # type: ignore[import] # pylint: disable=import-error
from scapy.all import ICMP  # type: ignore[import] # pylint: disable=import-error
from scapy.all import IP  # type: ignore[import] # pylint: disable=import-error
from scapy.all import Raw  # type: ignore[import] # pylint: disable=import-error
from scapy.all import conf  # type: ignore[import] # pylint: disable=import-error
from scapy.all import get_if_addr  # type: ignore[import] # pylint: disable=import-error
from scapy.all import get_if_hwaddr  # type: ignore[import] # pylint: disable=import-error
from scapy.all import srp  # type: ignore[import] # pylint: disable=import-error

from cros.factory.fastboot.proto import broadcast_ping_pb2  # type: ignore[attr-defined] # pylint: disable=no-name-in-module
from cros.factory.fastboot.proto import broadcast_ping_pb2_grpc  # type: ignore[attr-defined] # pylint: disable=no-name-in-module
from cros.factory.utils import file_utils


conf.checkIPaddr = False

scan_locks = defaultdict(asyncio.Lock)
scan_times = {}  # Format: {"eth0": 16788822.1, "eth1": 16788823.5}
scan_results = {}  # Format: {"eth0": ["192..."], "eth1": ["10.0..."]}
CACHE_TTL = 5.0

LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
LOG_FILE = 'broadcast_ping_server.log'


class BroadcastPingServicer(broadcast_ping_pb2_grpc.BroadcastPingServicer):

  async def PerformScan(self, request: broadcast_ping_pb2.ScanRequest,
                        context: grpc.ServicerContext):
    logging.info('Handling request from %s', context.peer())

    iface = request.iface
    current_time = time.time()

    if iface in scan_times and (current_time - scan_times[iface] < CACHE_TTL):
      logging.info('Request from %s is under cached TTL.', context.peer())
      return broadcast_ping_pb2.ScanResponse(devices=scan_results[iface])

    async with scan_locks[iface]:
      if iface in scan_times and (current_time - scan_times[iface] < CACHE_TTL):
        logging.info('Request from %s is under cached TTL.', context.peer())
        return broadcast_ping_pb2.ScanResponse(devices=scan_results[iface])

      try:
        results = await asyncio.to_thread(self._run_scapy_scan, request)
        scan_results[iface] = results
        scan_times[iface] = time.time()

        return broadcast_ping_pb2.ScanResponse(devices=results)
      except Exception as e:
        logging.error('Exception occurs when handling request for %s: %s',
                      context.peer(), e)
        context.set_code(grpc.StatusCode.INTERNAL)
        context.set_details(f"Scan failed: {str(e)}")

        return broadcast_ping_pb2.ScanResponse()

  def _run_scapy_scan(self, req: broadcast_ping_pb2.ScanRequest) -> list:
    src_ip = get_if_addr(req.iface)
    src_mac = get_if_hwaddr(req.iface)

    packet = (
        Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff') /
        IP(src=src_ip, dst='255.255.255.255', ttl=req.ttl) / ICMP() /
        Raw(load=req.payload.encode('utf-8')))

    responders: Set[str] = set()
    for _ in range(req.num_probes):
      ans, _ = srp(packet, iface=req.iface, timeout=req.timeout, multi=True,
                   verbose=0)

      for _, recv_pkt in ans:
        if recv_pkt.haslayer(
            ICMP) and recv_pkt[ICMP].type == 0:  # Type 0 is Echo Reply
          responders.add(recv_pkt[IP].src)
    logging.info('ICMP responders when scanning %s: %s', req.iface, responders)
    return list(responders)


async def serve(ip, port):
  server = grpc.aio.server()
  broadcast_ping_pb2_grpc.add_BroadcastPingServicer_to_server(
      BroadcastPingServicer(), server)

  server.add_insecure_port(f'{ip}:{port}')

  logging.info('Starting broadcast ping server on %s:%s...', ip, port)
  await server.start()
  await server.wait_for_termination()


def _init_logger(log_path: str, log_level: int) -> None:
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
  logger = logging.getLogger()
  logger.setLevel(log_level)
  logger.handlers = [stream_handler]

  if log_path:
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.handlers.append(file_handler)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--ip', help='IP of the host in docker network',
                      required=True)
  parser.add_argument('-p', '--port',
                      help='Port to run the broadcast ping server', type=int,
                      required=True)
  parser.add_argument('-l', '--log-dir', help='path to Umpire log directory',
                      required=True)
  parser.add_argument('--verbose', '-v',
                      help='Verbose log with detailed device information',
                      action='store_const', dest='log_level',
                      const=logging.DEBUG, default=logging.INFO)

  args = parser.parse_args()

  log_file = os.path.join(args.log_dir, LOG_FILE)
  if os.path.exists(log_file):
    file_utils.TryUnlink(log_file)
  _init_logger(log_file, args.log_level)
  asyncio.run(serve(args.ip, args.port))
