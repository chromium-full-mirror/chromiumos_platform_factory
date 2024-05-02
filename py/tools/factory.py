#!/usr/bin/env python3
#
# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Command-line interface for miscellaneous factory actions.

Run "factory --help" for more info and a list of subcommands.

To add a subcommand, just add a new Subcommand subclass to this file.
"""

import argparse
import csv
import functools
import inspect
import json
import logging
import os
import pprint
import re
import socket
import sys
import time

import yaml

from cros.factory.device import info
from cros.factory.test import device_data
from cros.factory.test.rules import phase
from cros.factory.test.rules import privacy
from cros.factory.test import state
from cros.factory.test.state import TestState
from cros.factory.test.test_lists import manager
from cros.factory.test.test_lists import test_list_common
from cros.factory.utils import debug_utils
from cros.factory.utils import log_utils
from cros.factory.utils.process_utils import Spawn
from cros.factory.utils import sys_interface

from cros.factory.external.py_lib import setproctitle


def Dump(data, dump_format, stream=sys.stdout, use_filter=True):
  """Dumps data to stream in given format.

  Args:
    data: the object to dump, usually dict.
    dump_format: a string describing format: json, yaml, pprint.
    stream: an file-like object, default to sys.stdout.
  """
  if use_filter:
    data = privacy.FilterDict(data)
  if dump_format == 'yaml':
    yaml.safe_dump(data, stream, default_flow_style=False)
  elif dump_format == 'json':
    json.dump(data, stream, indent=2, sort_keys=True, separators=(',', ': '))
  elif dump_format == 'pprint':
    pprint.pprint(data, stream)
  else:
    raise RuntimeError(f'Unknown format: {dump_format}')


class Subcommand:
  """A 'factory' subcommand.

  Properties:
    name: The name of the command (set by the subclass).
    help: Help text for the command (set by the subclass).
    parser: The ArgumentParser object.
    subparser: The subparser object created with parser.add_subparsers.
    subparsers: A collection of all subparsers.
    args: The parsed arguments.
  """
  name = None  # Overridden by subclass
  help = None  # Overridden by subclass

  parser = None
  args = None
  subparser = None
  subparsers = None

  def Init(self):
    """Initializes the subparser.

    May be implemented the subclass, which may use "self.subparser" to
    refer to the subparser object.
    """

  def Run(self):
    """Runs the command.

    Must be implemented by the subclass.
    """
    raise NotImplementedError


class HelpCommand(Subcommand):
  name = 'help'
  help = 'Get help on COMMAND'

  def Init(self):
    self.subparser.add_argument('command', metavar='COMMAND', nargs='?')  # type: ignore #TODO(b/338318729) Fixit!

  def Run(self):
    if self.args.command:  # type: ignore #TODO(b/338318729) Fixit!
      choice = self.subparsers.choices.get(self.args.command)  # type: ignore #TODO(b/338318729) Fixit!
      if not choice:
        sys.exit(f'Unknown subcommand {self.args.command!r}')  # type: ignore #TODO(b/338318729) Fixit!
      choice.print_help()
    else:
      self.parser.print_help()  # type: ignore #TODO(b/338318729) Fixit!


class RunCommand(Subcommand):
  name = 'run'
  help = 'Run a test'

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        'id', metavar='ID',
        help='ID of the test to run')

  def Run(self):
    run_id = state.GetInstance().RunTest(self.args.id)  # type: ignore #TODO(b/338318729) Fixit!
    print(f'Running test {self.args.id}')  # type: ignore #TODO(b/338318729) Fixit!
    print(f'Active test run ID: {run_id}')


class WaitCommand(Subcommand):
  name = 'wait'
  help = ('Wait for all tests to finish running, displaying status as testing '
          'progresses')

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--poll-interval', type=int, default=1,
        help='Poll interval in seconds')

  def Run(self):
    # Dict mapping test path -> test information.
    last_test_dict = None

    while True:
      tests = state.GetInstance().GetTests()
      test_dict = {}
      for t in tests:
        # Don't bother showing parent nodes.
        if t['parent']:
          continue
        # pylint: disable=unsubscriptable-object
        if last_test_dict is None:
          # First time; just print active tests
          if t['status'] == TestState.ACTIVE:
            print(f"{t['path']}: {t['status']}")
        else:
          # Show any tests with changed statuses.
          if t['status'] != last_test_dict[t['path']]['status']:
            sys.stdout.write(f"{t['path']}: {t['status']}")
            if t['status'] == TestState.FAILED:
              sys.stdout.write(f" ({str(t['error_msg'])!r})")
            sys.stdout.write('\n')

        test_dict[t['path']] = t

      # Save the test information for next time.
      last_test_dict = test_dict
      sys.stdout.flush()
      if not any(t['pending'] for t in tests):
        # All done!  Bail.
        print('done')
        break
      # Wait one second and poll again
      time.sleep(1)


class RunStatusCommand(Subcommand):
  name = 'run-status'
  help = 'Show information about a test run'

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--id', default=None, help='ID of the test run')

  def Run(self):
    goofy = state.GetInstance()
    run_status = goofy.GetTestRunStatus(self.args.id)  # type: ignore #TODO(b/338318729) Fixit!
    print(f"status: {run_status['status']}")
    if 'run_id' in run_status:
      print(f"run_id: {run_status['run_id']}")
      print('scheduled_tests:')
      # Simply call 'tests' subcommand to print out information about the
      # scheduled tests.
      args = self.parser.parse_args(['tests', '--this-run', '--status'])  # type: ignore #TODO(b/338318729) Fixit!
      args.subcommand.args = args
      args.subcommand.Run()


class TestsCommand(Subcommand):
  name = 'tests'
  help = 'Show information about tests'

  def __init__(self):
    self.goofy = state.GetInstance()

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--status', '-s', action='store_true',
        help='Include information about test status')
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--this-run', action='store_true',
        help='Show only information about current active run')
    self.subparser.add_argument('--csv', action='store_true',  # type: ignore #TODO(b/338318729) Fixit!
                                help='Show test status in CSV format')
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--label', action='store_true',
        help=('Show en-US label instead of test item path.'))
    self.subparser.add_argument('--readiness', '-r', action='store_true',  # type: ignore #TODO(b/338318729) Fixit!
                                help='Create a factory readiness report.')
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--output', '-o', type=str, default=None, metavar='path',
        help='Path to store the csv file. Print to stdout if not set.')

  def _GetHeader(self, readiness=False):
    device = sys_interface.SystemInterface()
    system_info = info.SystemInfo(device)
    header = [
        ['Product', f'{system_info.device_name}'],
        ['Build Phase', f'{system_info.stage}'],
        ['Release Image Version', f'{system_info.release_image_version}'],
        ['FW Version', f'{system_info.firmware_version}'],
        ['Test Image Version', f'{system_info.test_image_version}'],
        ['Factory Toolkit', f'{system_info.toolkit_version}'],
    ]
    if readiness:
      header.append([
          'Test Category', 'Component Readiness', 'Test Station', 'Test Group',
          'Test Item', 'Test Status'
      ])
    return header

  @functools.lru_cache(maxsize=1000)
  def _GetLabelInner(self, path, label):
    test_object = self.goofy.test_list.LookupPath(path)
    if label and 'en-US' in test_object.label:
      return test_object.label['en-US']
    return path

  def _GetLabel(self, path):
    return self._GetLabelInner(path, self.args.label)  # type: ignore #TODO(b/338318729) Fixit!

  def _GetCSVLabelFromPath(self, path: str) -> list:
    """Returns the test object path in a CSV label format.

    Args:
      path: The test object path.

    Returns:
      A list representing the CSV label:
      [{test_station}, {test_group}, {test_item}].

    Example:
      path ='main_rex:FAT.RexUpdatePSROEMData'
      returns ['FAT (Final Assembly Test)', '', 'Update PSR Oem Data']
    """

    path = path.split('.', 2)  # type: ignore #TODO(b/338318729) Fixit!
    labels = [self._GetLabel('.'.join(path[:i + 1])) for i in range(len(path))]
    if len(path) == 1:
      return ['', ''] + labels
    if len(path) == 2:
      return [labels[0], '', labels[1]]
    return labels

  def _GenerateFactoryTestStatusSheet(self, tests):
    # the csv can be used to generate factory test status sheet like the
    # template here: go/factory-test-status-template
    self.args.label = True  # type: ignore #TODO(b/338318729) Fixit!
    output_csv = []

    if self.args.output:  # type: ignore #TODO(b/338318729) Fixit!
      csv_filename = self.args.output  # type: ignore #TODO(b/338318729) Fixit!
      if os.path.exists(csv_filename):
        raise RuntimeError(f'Filename: {csv_filename} exists. '
                           'Use `factory tests --csv -o` with a unique path.')
      logging.info('Creating factory test status sheet...')

    output_csv += self._GetHeader()
    for t in tests:
      output_csv.append(self._GetCSVLabelFromPath(t["path"]) + [t["status"]])

    if self.args.output:  # type: ignore #TODO(b/338318729) Fixit!
      with open(csv_filename, 'w', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(output_csv)
      logging.info('%s is created.', csv_filename)
    else:
      writer = csv.writer(sys.stdout)
      writer.writerows(output_csv)

  def _GenerateFactoryReadinessReport(self, tests):
    pytest_to_skip = ['shutdown', 'summary']
    if self.args.output:  # type: ignore #TODO(b/338318729) Fixit!
      csv_filename = self.args.output  # type: ignore #TODO(b/338318729) Fixit!
      if os.path.exists(csv_filename):
        raise RuntimeError(f'Filename: {csv_filename} exists. '
                           'Use `factory tests -r -o` with a unique path.')
      logging.info('Creating factory readiness report...')

    self.args.label = True  # type: ignore #TODO(b/338318729) Fixit!
    report = {}  # type: ignore #TODO(b/338318729) Fixit!
    uncategorized_tests = []
    output_csv = []

    for t in tests:
      if t['pytest_name'] in pytest_to_skip:
        continue
      if not t['related_components']:
        uncategorized_tests.append(t)
      for test_category in t['related_components']:
        report.setdefault(test_category, []).append(t)

    output_csv += self._GetHeader(readiness=True)
    for category, categorized_tests in report.items():
      readiness = 'Ready' if all(t['status'] == state.TestState.PASSED
                                 for t in categorized_tests) else 'Not Ready'
      output_csv.append([category.name, readiness])
      for t in categorized_tests:
        output_csv.append(['', ''] + self._GetCSVLabelFromPath(t['path']) +
                          [t['status']])
    output_csv.append(['Uncategorized Tests'])
    for t in uncategorized_tests:
      output_csv.append(self._GetCSVLabelFromPath(t['path']) + [t['status']])

    if self.args.output:  # type: ignore #TODO(b/338318729) Fixit!
      with open(csv_filename, 'w', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(output_csv)
      logging.info('%s is created.', csv_filename)
    else:
      writer = csv.writer(sys.stdout)
      writer.writerows(output_csv)

  def Run(self):
    # Consider only tests without parents
    tests = [t for t in self.goofy.GetTests() if not t.get('parent')]

    if self.args.this_run:  # type: ignore #TODO(b/338318729) Fixit!
      scheduled_tests = (
          self.goofy.GetTestRunStatus(None).get('scheduled_tests') or [])
      scheduled_tests = {t['path']
                         for t in scheduled_tests}
      tests = [t for t in tests if t['path'] in scheduled_tests]

    if self.args.csv:  # type: ignore #TODO(b/338318729) Fixit!
      self._GenerateFactoryTestStatusSheet(tests)
    elif self.args.readiness:  # type: ignore #TODO(b/338318729) Fixit!
      self._GenerateFactoryReadinessReport(tests)
    else:
      for t in tests:
        sys.stdout.write(self._GetLabel(t['path']))
        if self.args.status:  # type: ignore #TODO(b/338318729) Fixit!
          if t['status'] != TestState.UNTESTED:
            sys.stdout.write(f": {t['status']}")
          if t['error_msg']:
            sys.stdout.write(f": {str(t['error_msg'])!r}")
        sys.stdout.write('\n')


class ClearCommand(Subcommand):
  name = 'clear'
  help = 'Stop all tests and clear test state'

  def Run(self):
    state.GetInstance().ClearState()


class StopCommand(Subcommand):
  name = 'stop'
  help = 'Stop all tests'

  def Run(self):
    state.GetInstance().StopTest()


class DumpTestListCommand(Subcommand):
  name = 'dump-test-list'
  help = 'Dump a test list in given format'

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--format', metavar='FORMAT',
        help='Format in which to dump test list',
        default='json',
        choices=('yaml', 'csv', 'json', 'pprint'))
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        'id', metavar='ID', help='ID of test list to dump')

  def Run(self):
    mgr = manager.Manager()
    all_test_lists, unused_errors = mgr.BuildAllTestLists()
    test_list = all_test_lists[self.args.id].ToFactoryTestList()  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.format == 'csv':  # type: ignore #TODO(b/338318729) Fixit!
      writer = csv.writer(sys.stdout)
      writer.writerow(('id', 'module'))
      for t in test_list.Walk():
        if t.IsLeaf():
          if t.pytest_name:
            module = t.pytest_name
          else:
            module = ''

          writer.writerow((t.path, module))
    else:
      Dump(test_list.ToTestListConfig(), dump_format=self.args.format)  # type: ignore #TODO(b/338318729) Fixit!


class TestListCommand(Subcommand):
  name = 'test-list'
  help = ('Set or get the active test list, and/or list all test lists. '
          'Note that generic test list is allowed only when there is no '
          'main test list.')

  TIMEOUT_SECS = 60
  POLL_INTERVAL_SECS = 0.5

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        'id', metavar='ID', nargs='?',
        help=('ID of test list to activate (run '
              '"factory test-list --list" to see all available IDs)'))
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--list', action='store_true',
        help='List all available test lists')
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--restart', action='store_true',
        help='Restart goofy and wait for new test list to come up')
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--clear-all', '-a', action='store_true',
        help='If restarting goofy, clear all state (like factory_restart -a)')

  def Run(self):
    device = sys_interface.SystemInterface()
    mgr = manager.Manager()
    all_test_lists, unused_errors = mgr.BuildAllTestLists()

    if self.args.id:  # type: ignore #TODO(b/338318729) Fixit!
      if self.args.id not in all_test_lists:  # type: ignore #TODO(b/338318729) Fixit!
        sys.exit(
            f'Unknown test list ID {self.args.id!r} (use "factory test-list '  # type: ignore #TODO(b/338318729) Fixit!
            '--list" to see available test lists')
      mgr.SetActiveTestList(self.args.id)  # type: ignore #TODO(b/338318729) Fixit!
      print(
          f'Set active test list to {self.args.id} (wrote {self.args.id!r} to '  # type: ignore #TODO(b/338318729) Fixit!
          f'{test_list_common.ACTIVE_TEST_LIST_CONFIG_PATH})')
      sys.stdout.flush()
    else:
      print(mgr.GetActiveTestListId(device))

    if self.args.list:  # type: ignore #TODO(b/338318729) Fixit!
      active_id = mgr.GetActiveTestListId(device)

      # Calculate the maximum width of test_lists for alignment of displaying.
      test_lists_id_maxlen = max(map(len, all_test_lists), default=0)
      id_width = max(test_lists_id_maxlen, len('ID'))

      line_format = '{is_active:>8} {id:<{id_width}} {source_path}'
      print(line_format.format(is_active='ACTIVE?', id='ID', id_width=id_width,
                               source_path='PATH'))

      for k, v in sorted(all_test_lists.items()):
        is_active = '(active)' if k == active_id else ''
        print(line_format.format(is_active=is_active, id=k, id_width=id_width,
                                 source_path=v.source_path))

    if self.args.restart:  # type: ignore #TODO(b/338318729) Fixit!
      goofy = state.GetInstance()

      # Get goofy's current UUID
      try:
        uuid = goofy.GetGoofyStatus()['uuid']
      except socket.error:
        logging.info('goofy is not up')
      except Exception:
        logging.exception('Unable to get goofy status; assuming it is down')
        uuid = None

      # Set the proc title so factory_restart won't kill us.
      if setproctitle.MODULE_READY:
        setproctitle.setproctitle('factory set-active-test-list')  # type: ignore #TODO(b/338318729) Fixit!
      else:
        sys.stderr.write(
            'WARNING: setproctitle not available, factory_restart may fail.\n')

      # Restart goofy, clearing its state
      Spawn(['factory_restart'] +
            (['-a'] if self.args.clear_all else []),  # type: ignore #TODO(b/338318729) Fixit!
            check_call=True, log=True)

      # Wait for goofy to come up with a different UUID
      start = time.time()

      last_status_summary = None

      while True:
        try:
          status = goofy.GetGoofyStatus()
          status_summary = str(status)
          if status['uuid'] == uuid:
            # goofy hasn't shut down yet
            continue
          if status['status'] == 'RUNNING':
            # All good
            logging.info(status_summary)
            logging.info('goofy is up')
            if status['test_list_id'] != self.args.id:  # type: ignore #TODO(b/338318729) Fixit!
              # Shouldn't ever happen
              sys.exit('goofy came up with wrong test list '
                       f'{status["test_list_id"]!r}')
            return
          if status['status'] not in ['UNINITIALIZED', 'INITIALIZING']:
            # This means it's never going to come up.
            sys.exit('goofy failed to come up; status is %r', status['status'])  # type: ignore #TODO(b/338318729) Fixit!
        except Exception:
          status_summary = f'Exception: {debug_utils.FormatExceptionOnly()}'
          if 'Connection refused' in status_summary:
            # Still waiting for goofy to open its RPC; print a friendly
            # error message
            status_summary = (
                'Waiting patiently for goofy to accept RPC connections...')

        if status_summary != last_status_summary:
          logging.info(status_summary)
          last_status_summary = status_summary
        if time.time() - start >= self.TIMEOUT_SECS:
          sys.exit(f'goofy did not come up after {self.TIMEOUT_SECS} seconds')
        time.sleep(self.POLL_INTERVAL_SECS)


class DeviceDataCommand(Subcommand):
  name = 'device-data'
  help = 'Show the contents of the device data dictionary'

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        'set', metavar='KEY=VALUE', nargs='*',
        help=('(To be used only manually for debugging) '
              'Sets a device data KEY to VALUE. If VALUE is one of '
              '["True", "true", "False", "false"], then it is considered '
              'a bool. If it is "None" then it is considered to be None. '
              'If it can be coerced to an int, it is considered an int. '
              'Otherwise, it is considered a string. '
              'To avoid type ambiguity, if you need to programmatically '
              'modify device data, don\'t use this; use --set-yaml.'))
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '-g', '--get',
        help='Read one device data and print its value.')
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--set-yaml', metavar='FILE',
        help=('Read FILE (or stdin if FILE is "-") as a YAML dictionary '
              'and set device data.'))
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--format', metavar='FORMAT',
        help='Format in which to dump device data',
        default='yaml',
        choices=('yaml', 'json', 'pprint'))
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--delete', '-d', metavar='KEY', nargs='*',
        help='Deletes KEYs from device data. '
             '"factory device-data -d A B C" deletes A, B, C from device-data.')
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--no-filter', action='store_false', dest='use_filter',
        help='Do not use filter when dumping device data.')

  def Run(self):
    if self.args.get:  # type: ignore #TODO(b/338318729) Fixit!
      print(device_data.GetDeviceData(self.args.get, ''))  # type: ignore #TODO(b/338318729) Fixit!
      return

    if self.args.set:  # type: ignore #TODO(b/338318729) Fixit!
      update = {}
      for item in self.args.set:  # type: ignore #TODO(b/338318729) Fixit!
        match = re.fullmatch(r'([^=]+)=(.*)', item)
        if not match:
          sys.exit('--set argument %r should be in the form KEY=VALUE')

        key, value = match.groups()
        if value in ['True', 'true']:
          value = True
        elif value in ['False', 'false']:
          value = False
        elif value == 'None':
          value = None
        else:
          try:
            value = int(value)
          except ValueError:
            pass  # No sweat

        update[key] = value
      device_data.UpdateDeviceData(update)

    if self.args.delete:  # type: ignore #TODO(b/338318729) Fixit!
      device_data.DeleteDeviceData(self.args.delete)  # type: ignore #TODO(b/338318729) Fixit!

    if self.args.set_yaml:  # type: ignore #TODO(b/338318729) Fixit!
      if self.args.set_yaml == '-':  # type: ignore #TODO(b/338318729) Fixit!
        update = yaml.safe_load(sys.stdin)
      else:
        with open(self.args.set_yaml, encoding='utf8') as f:  # type: ignore #TODO(b/338318729) Fixit!
          update = yaml.safe_load(f)
      if not isinstance(update, dict):
        sys.exit(f'Expected a dict but got a {type(update)!r}')
      device_data.UpdateDeviceData(update)

    Dump(device_data.GetAllDeviceData(), self.args.format,  # type: ignore #TODO(b/338318729) Fixit!
         use_filter=self.args.use_filter)  # type: ignore #TODO(b/338318729) Fixit!


class ScreenshotCommand(Subcommand):
  name = 'screenshot'
  help = 'Take a screenshot of the Goofy tab that runs the factory test UI'

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        'output_file', metavar='OUTPUT_FILE', nargs='?',
        help=('The output filepath to save the captured screen as a PNG file.  '
              'If not provided, defaults to /var/log/screenshot_<TIME>.png.'))

  def Run(self):
    state.GetInstance().DeviceTakeScreenshot(self.args.output_file)  # type: ignore #TODO(b/338318729) Fixit!


class PhaseCommand(Subcommand):
  name = 'phase'
  help = 'Query or set the current phase'

  def Init(self):
    self.subparser.add_argument(  # type: ignore #TODO(b/338318729) Fixit!
        '--set', metavar='PHASE',
        help='Sets the current phase (one of %(choices)s)',
        choices=phase.PHASE_NAMES + ['None'])

  def Run(self):
    if self.args.set:  # type: ignore #TODO(b/338318729) Fixit!
      phase.SetPersistentPhase(None if self.args.set in ['None', '']  # type: ignore #TODO(b/338318729) Fixit!
                               else self.args.set)  # type: ignore #TODO(b/338318729) Fixit!
    print(phase.GetPhase())


def main():
  log_utils.InitLogging()
  parser = argparse.ArgumentParser(
      description=(
          'Miscellaneous factory commands for use on DUTs (devices under '
          'test). Use "factory help COMMAND" for more info on a '
          'subcommand.'))
  subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
  subparsers.required = True

  for _, v in sorted(globals().items()):
    if v != Subcommand and inspect.isclass(v) and issubclass(v, Subcommand):
      subcommand = v()
      assert subcommand.name
      assert subcommand.help
      v.parser = parser
      v.subparsers = subparsers
      v.subparser = subparsers.add_parser(subcommand.name, help=subcommand.help)
      v.subparser.set_defaults(subcommand=subcommand)
      subcommand.Init()

  args = parser.parse_args()
  args.subcommand.args = args
  args.subcommand.Run()


if __name__ == '__main__':
  main()
