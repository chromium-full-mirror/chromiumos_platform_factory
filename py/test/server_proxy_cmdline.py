#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Command-line interface for server proxy."""

import argparse
import sys

from cros.factory.test import server_proxy
from cros.factory.utils import file_utils


def UploadReportMain(args: argparse.Namespace):
  """Call UploadReport."""
  # `server` is a proxy of cros.factory.umpire.server.rpc_dut.LogDUTCommands
  server = server_proxy.GetServerProxy(args.url, args.expected_project,
                                       args.timeout)
  if args.report_blob_filename:
    report_blob = file_utils.ReadFile(args.report_blob_filename, encoding=None)
  else:
    report_blob = b'test_report_blob'
  server.UploadReport(args.serial_number, report_blob, args.report_name,
                      args.stage)


def UploadCSVEntryMain(args: argparse.Namespace):
  """Call UploadCSVEntry."""
  # `server` is a proxy of cros.factory.umpire.server.rpc_dut.LogDUTCommands
  server = server_proxy.GetServerProxy(args.url, args.expected_project,
                                       args.timeout)
  server.UploadCSVEntry(args.csv_name, args.data)


def RetrieveParameter(args: argparse.Namespace):
  """Call GetParameters"""
  server = server_proxy.GetServerProxy(args.url, args.expected_project,
                                       args.timeout)
  content = server.GetParameters(args.source_namespace, args.source_file).data
  output_file = args.output or args.source_file
  print(f'Saving to {output_file}, it should be a tar file.')
  with open(output_file, 'wb') as f:
    f.write(content)


def ParseOptions():
  """Creates the argument parser and returns the parsed options."""
  # Create the root argument parser.
  arg_parser = argparse.ArgumentParser(
      description=sys.modules[__name__].__doc__)
  arg_parser.add_argument('--url', default='http://localhost:8080')
  arg_parser.add_argument('--expected_project', default=None)
  arg_parser.add_argument('--timeout', default=None)

  subparsers = arg_parser.add_subparsers(title='subcommands', dest='subcommand')
  subparsers.required = True

  subparser = subparsers.add_parser('upload_report')
  subparser.add_argument('--serial_number', default='test_serial_number')
  subparser.add_argument('--report_blob_filename', default=None)
  subparser.add_argument('--report_name', default=None)
  subparser.add_argument('--stage', default='EVT100')
  subparser.set_defaults(_Command=UploadReportMain)

  subparser = subparsers.add_parser('upload_csv')
  subparser.add_argument('--csv_name', default='test_csv')
  subparser.add_argument('--data', nargs='+', default=[])
  subparser.set_defaults(_Command=UploadCSVEntryMain)

  subparser = subparsers.add_parser('retrieve_parameter')
  subparser.add_argument('--source_namespace', required=True)
  subparser.add_argument('--source_file', required=True)
  subparser.add_argument('--output', '-o', default=None)
  subparser.set_defaults(_Command=RetrieveParameter)

  # Parse the argument.
  return arg_parser.parse_args()


def Main():
  options = ParseOptions()
  options._Command(options)  # pylint: disable=protected-access


if __name__ == "__main__":
  Main()
