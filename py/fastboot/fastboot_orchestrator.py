#!/usr/bin/env python3
# Copyright 2025 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import abc
import argparse
import ipaddress
import logging
import queue
from subprocess import CalledProcessError
from subprocess import TimeoutExpired
import threading
import time
from typing import List, Set

from cros.factory.fastboot import fastboot_util
from cros.factory.utils import process_utils


LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'


class DeviceScanner(abc.ABC):
  """An abstract class for available device scanner."""

  @abc.abstractmethod
  def __init__(self, dut_info_list):
    raise NotImplementedError

  @abc.abstractmethod
  def Scan(self):
    """Returns detected device information."""
    raise NotImplementedError


class UsbDeviceScanner(DeviceScanner):
  """Device scanner over USB transportation layer."""

  def __init__(self, dut_info_list):
    self.usb_device_list = dut_info_list

  # TODO(stevesu) Implement this part.
  # Probably can start with `lsusb` or `udevadm` monitor.
  def Scan(self) -> Set[str]:
    available_devices: Set[str] = set()
    return available_devices


class NmapIpScanner(DeviceScanner):
  """Device scanner over TCP transportation layer using nmap."""

  resolved_ip_set = set()

  def __init__(self, dut_info_list: List[str]):
    self.ip_to_scan = dut_info_list
    self.ConstructRawIpSet()

  # TODO(stevesu) Currently we did not rule out host ip & DHCP server IP.
  # Try adding this in the future to further reduce the network load.
  def Scan(self) -> set:
    """Scans alived TCP IP via nmap.

    Returns:
      A set of IP that is now being probed by nmap.
    """

    output = process_utils.CheckOutput(['nmap', '-sn', '-vv'] + self.ip_to_scan)
    return self.ParseNmapResult(output)

  def _GetAllIpInCidrRange(self, cidr_range: str) -> None:
    """Parses All IP from CIDR range.

    Args:
      cidr_range: A CIDR range string.

    Raises:
      RuntimeError: Cannot parse given CIDR range.
    """
    try:
      network = ipaddress.ip_network(cidr_range, strict=False)

      # Iterate over the network object to get all IP addresses
      for ip in network:
        self.resolved_ip_set.add(str(ip))
    except ValueError as e:
      logging.error('Error occured when parsing CIDR range: %s', e)
      raise RuntimeError('Cannot parse CIDR range.') from e

  def ConstructRawIpSet(self):
    """Constructs Raw IP set to be scanned."""

    for ip_str in self.ip_to_scan:
      if '/' in ip_str:
        self._GetAllIpInCidrRange(ip_str)
      else:
        self.resolved_ip_set.add(ip_str)
    logging.debug('Resolved Raw IP set is: %s', self.resolved_ip_set)

  def ParseNmapResult(self, output: str) -> set:
    """Parses nmap command result of current available IP."""

    found_ip_set = set()
    found_ip = None

    # For the ip being scanned, if the host is down, example stderr would be:
    # Nmap scan report for 192.168.0.178 [host down, received no-response]
    for line in output.split('\n'):
      tokens = line.split()
      # Alive host would return two lines in the stdout:
      # Nmap scan report for 192.168.0.177
      # Host is up, received conn-refused (0.0024s latency).
      if tokens and len(tokens) > 4 and tokens[4] in self.resolved_ip_set:
        found_ip = tokens[4]
      else:
        if found_ip and 'Host is up' in line:
          found_ip_set.add(found_ip)
          found_ip = None

    return found_ip_set


class FastbootImagingOrchestrator:
  """A multi-threaded orchestrator that can flash devices simultaneously."""

  def __init__(self, board_name: str, project_name: str, src_image_dir: str,
               ip_list: List[str], usb_device_list: List[str],
               is_fixed_ip: bool = False, scan_interval: int = 5,
               idle_timeout: int = 60):

    self.project_name = project_name
    self.board_name = board_name
    self.src_image_dir = src_image_dir

    self.ip_list = ip_list
    self.is_fixed_ip = is_fixed_ip
    self.usb_device_list = usb_device_list
    self.scan_interval = scan_interval
    self.idle_timeout = idle_timeout

    # TODO(stevesu) Wrap set with lock to have simpler coding pattern.
    self.dut_in_use: Set[str] = set()
    self.dut_in_use_lock: threading.Lock = threading.Lock()

    self.dut_queue: queue.Queue = queue.Queue()
    self.active_threads: List[threading.Thread] = []
    self.stop_event: threading.Event = threading.Event()

  def ConnectionIpScannerFunc(self) -> None:
    """Scanning function for nmap IP scanner."""

    ip_scanner = NmapIpScanner(self.ip_list)

    logging.info('Orchestrator scanner thread is up.')
    logging.info('Scanning every %d seconds for ip list: %s',
                 self.scan_interval, self.ip_list)

    while True:
      active_ip = ip_scanner.Scan()
      with self.dut_in_use_lock:
        for ip in active_ip:
          if ip not in self.dut_in_use:
            self.dut_queue.put(ip)
      time.sleep(self.scan_interval)

  def RunTask(self) -> None:
    # TODO(stevesu): Change scan target function to a composite pattern when
    # we supports USB, so that we can monitor TCP & USB at the same time.
    scanner_thread = threading.Thread(target=self.ConnectionIpScannerFunc,
                                      daemon=True)
    scanner_thread.start()

    try:
      while not self.stop_event.is_set():
        try:
          next_dut = self.dut_queue.get(False)
          task_thread = threading.Thread(target=self.ProcessTask,
                                         args=(next_dut, ),
                                         name=f"FBThread-{next_dut}")
          task_thread.daemon = True
          task_thread.start()
          self.active_threads.append(task_thread)
          with self.dut_in_use_lock:
            self.dut_in_use.add(next_dut)
        except queue.Empty:
          continue
    except KeyboardInterrupt:
      logging.info('Orchestrator: KeyboardInterrupt received. Shutting down')
    finally:
      self.ShutDown()

  def TaskFinished(self, dut_info: str) -> None:
    with self.dut_in_use_lock:
      logging.info('DUT [%s] exited flashing task.', dut_info)
      self.dut_in_use.remove(dut_info)

  # TODO(stevesu) Add support of fixed ip & usb cable case.
  def ProcessTask(self, dut_info: str) -> None:
    runner = fastboot_util.FastbootRunnerFactory(dut_info, self.src_image_dir,
                                                 self.idle_timeout)
    # FW fastboot & userspace fastboot reports different product name now.
    # This will be aligned after per-model build is introduced.
    try:
      if runner.GetProductName().lower() in (self.board_name,
                                             self.project_name):
        is_userspace = runner.GetIsUserSpace()
        if is_userspace:
          # Flash with userspace fastboot. We decided to flash everything again
          # during userspace fastboot, just to be safe. `flashall` will reboot
          # the device automatically.
          runner.FlashAll()
        else:
          runner.FlashMbrAndGptTable()
          runner.FlashBootPartitions()
          runner.RebootToUserSpaceFastboot()
    except TimeoutExpired as e:
      logging.error(('DUT [%s] task is terminated due to '
                     'exceeding the idle time limit (error: %r)'), dut_info, e)
    except CalledProcessError as e:
      logging.error(('DUT [%s] task is terminated due to '
                     'non-zero exit (error: %r)'), dut_info, e)
    finally:
      self.TaskFinished(dut_info)

  def ShutDown(self) -> None:
    self.stop_event.set()  # Signal all threads to stop
    logging.info('Orchestrator: Waiting for active threads to complete...')
    for t in self.active_threads:
      if t.is_alive():
        try:
          t.join(timeout=5)  # Wait for threads to finish
          if t.is_alive():
            logging.info('Orchestrator: Thread %s did not terminate.', t.name)
        except Exception as e:
          logging.info('Orchestrator: Error joining thread %s: %s', t.name, e)
    logging.info('Orchestrator: Shutdown complete.')


def InitLogger(log_path: str, log_level: int) -> None:
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
  parser.add_argument('--verbose', '-v',
                      help='Verbose log with detailed device information',
                      action="store_const", dest="log_level",
                      const=logging.DEBUG, default=logging.INFO)
  parser.add_argument('--src_image_dir', '-s', required=True,
                      help='Directory for source image to be flashed.')
  parser.add_argument('--ip_list', '-i', nargs='+',
                      help='A list of ip and CIDR range to monitor')
  parser.add_argument('--board', '-b', help='Board name of the target device',
                      required=True)
  parser.add_argument('--project', '-p',
                      help='Project name of the target device', required=True)
  parser.add_argument(
      '--is_fixed_ip', type=bool, default=False,
      help='If set, the ip in the ip list will be regarded as fixed ip.')
  parser.add_argument('--scan_interval', '-t', type=int, default=5,
                      help='Default scan interval for the orchestrator')
  parser.add_argument('--usb_device_list', '-u',
                      help='A list of adb/fastboot usb cable device to monitor')
  parser.add_argument('--log_path', '-l', help='Path to the log file')
  parser.add_argument(
      '--idle_timeout', type=int, default=60,
      help=('The idle time limit for executing a single fastboot command. '
            'Set to any non-positive number for unlimited timeout'))

  args = parser.parse_args()
  if args.ip_list is None and args.usb_device_name is None:
    parser.error('Either ip or usb device name has to be provided.')

  InitLogger(args.log_path, args.log_level)
  orchestartor = FastbootImagingOrchestrator(
      args.board, args.project, args.src_image_dir, args.ip_list,
      args.is_fixed_ip, args.usb_device_list, args.scan_interval,
      args.idle_timeout)
  orchestartor.RunTask()
