#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""A script for installing an apk as a priv-app.

Dependencies:
1. adb
2. aapt
"""

import argparse
import dataclasses
import logging
import pathlib
import re
import shlex
import subprocess
import sys
import time
from typing import List, Optional, Sequence, Union


_PRIV_APP_PATH = pathlib.Path('/system/priv-app')
_PACKAGE_NAME_PATTERN = re.compile(r"package: name='([^']*)'")
_PERMISSION_PATTERN = re.compile(r"uses-permission: name='([^']*)'", re.M)
_PRIVILEGED_PATTERN = re.compile(r'^.*\bprivateFlags=.*\bPRIVILEGED\b.*$', re.M)


def Run(
    args: Union[str, Sequence[str]],
    *,
    shell=False,
    cwd: Optional[str] = None,
    check=True,
    encoding: Optional[str] = 'utf-8',
    log=True,
    **kwargs,
):
  """A wrapper of `subprocess.run`.

  Differences:
  1. All parameters except args are keyword-only.
  2. `check` default to True
  3. `encoding` default to 'utf-8'
  4. Log running command into logging.info by default.
  """
  args_to_log: str
  if shell:
    if not isinstance(args, str):
      raise TypeError('Command must be a string when shell is specified.')
    args_to_log = args
  else:
    if isinstance(args, str):
      raise TypeError('Command must be a sequence (list/tuple) of string.')
    args_to_log = ' '.join(map(shlex.quote, args))
  if log:
    message = f'Running command: "{args_to_log}"'
    if cwd is not None:
      message += f' in {cwd}'
    logging.info(message)
  return subprocess.run(args, shell=shell, cwd=cwd, check=check,
                        encoding=encoding, **kwargs)


@dataclasses.dataclass
class InstallAsPrivAppArgs:
  apk_path: pathlib.Path
  dir_app_name: str
  skip_factory_settings: bool
  target: Optional[str] = None
  package_name: str = ''
  permission_path: pathlib.Path = pathlib.Path()
  uninstall_previous: bool = False

  @property
  def adb(self):
    result = ['adb']
    if self.target:
      result.extend(['-s', self.target])
    return result


def MakeParser():
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('apk_path', metavar='APK_PATH', type=pathlib.Path,
                      help='Path to the apk.')
  parser.add_argument('--target', type=str,
                      help='Use as HOST in adb connection.')
  parser.add_argument('--dir_app_name', type=str, default='Factory',
                      help='The apk name on the device.')
  parser.add_argument('--uninstall_previous', action='store_true',
                      help='Uninstall the app before deployment.')
  parser.add_argument(
      '--skip_factory_settings', action='store_true',
      help=('If set, skip factory settings. Factory settings include stay on '
            'while plugged in and other configurations. Check '
            'SetFactorySettings for detail.'))
  return parser


def ParsePackageName(apk_info: str):
  match = _PACKAGE_NAME_PATTERN.match(apk_info)
  if match is None:
    logging.info('No package name in apk_info')
    sys.exit(1)
  return match.group(1)


def GeneratePermissionFile(args: InstallAsPrivAppArgs, apk_info: str):
  with args.permission_path.open('w', encoding='utf-8') as f:
    f.write('<permissions>\n')
    f.write(f'  <privapp-permissions package="{args.package_name}">\n')
    for match in _PERMISSION_PATTERN.finditer(apk_info):
      f.write(f"    <permission name='{match.group(1)}' />\n")
    f.write('  </privapp-permissions>\n')
    f.write('</permissions>\n')


def UnInstallPreviousForUser(args: InstallAsPrivAppArgs, userId: int):
  result = Run(
      args.adb + ['shell', 'pm', 'list', 'package', '--user',
                  str(userId)], stdout=subprocess.PIPE)
  pattern = re.compile(rf'^package:{args.package_name}\b.*$', re.M)
  match = pattern.findall(result.stdout)
  logging.info('UnInstallPreviousForUser userId=%s match=%s', userId, match)
  if match:
    Run(args.adb + ['uninstall', '--user', str(userId), args.package_name])


def GetCanSwitchToHeadlessSystemUser(args: InstallAsPrivAppArgs):
  result = Run(
      args.adb + ['shell', 'cmd', 'user', 'can-switch-to-headless-system-user'],
      stdout=subprocess.PIPE)
  return 'true' in result.stdout


def UnInstallPrevious(args: InstallAsPrivAppArgs):
  """Uninstall previous package.

  We have two users, 0 (system user) and 10 (owner). Reference:
  https://source.android.com/docs/automotive/users_accounts/multi_user

  May need to modify the code to uninstall for all users or a specific user
  later.
  """
  if not args.uninstall_previous:
    return
  for user in (10, 0):
    UnInstallPreviousForUser(args, user)


def WaitForSystem(args: InstallAsPrivAppArgs):
  Run(args.adb + ['wait-for-device'])
  # Wait until package manager is up so we can launch activity.
  while True:
    result = Run(args.adb + ['shell', 'dumpsys', '-l'], stdout=subprocess.PIPE)
    if 'package' in result.stdout:
      break
    time.sleep(1.0)
  Run(args.adb + ['root'])


def InstallApk(args: InstallAsPrivAppArgs):
  """Install an apk.

  1. -g grants runtime permissions
  2. -t allows test-only packages
     Check
     https://developer.android.com/guide/topics/manifest/application-element#testOnly
     for doc of test-only packages. Additionally, We cannot remove a device
     owner with `adb shell dpm remove-active-admin` unless the device owner is a
     test-only package.
  """  # pylint: disable=line-too-long
  Run(args.adb + ['install', '-g', '-t', str(args.apk_path)])


def Install(args: InstallAsPrivAppArgs):
  Run(args.adb + ['root'])
  result = Run(args.adb + ['remount', '-R'], check=False)
  if result.returncode == 255:
    logging.info('return code is 255. Wait for reboot completed.')
    WaitForSystem(args)
    Run(args.adb + ['remount'])
  elif result.returncode == 0:
    logging.info('return code is 0.')
  else:
    logging.info('return code is %s.', result.returncode)
    sys.exit(1)

  on_device_dir_path = _PRIV_APP_PATH / args.dir_app_name
  Run(args.adb + ['shell', 'mkdir', '-p', str(on_device_dir_path)])
  Run(args.adb + ['shell', 'chmod', '755', str(on_device_dir_path)])

  on_device_apk_path = on_device_dir_path / f'{args.dir_app_name}.apk'
  Run(args.adb + ['push', str(args.apk_path), str(on_device_apk_path)])
  Run(args.adb + ['shell', 'chmod', '644', str(on_device_apk_path)])

  on_device_permission_path = pathlib.Path(
      'system', 'etc', 'permissions',
      f'privapp-permissions-{args.dir_app_name}.xml')
  Run(args.adb +
      ['push',
       str(args.permission_path),
       str(on_device_permission_path)])
  Run(args.adb + ['shell', 'chmod', '644', str(on_device_permission_path)])

  InstallApk(args)

  result = Run(args.adb + ['shell', 'dumpsys', 'package', args.package_name],
               stdout=subprocess.PIPE)
  match = _PRIVILEGED_PATTERN.findall(result.stdout)
  for line in match:
    logging.info('%s', line)
  if not match:
    logging.info('App is not privileged and requires a reboot to enable '
                 'privileged.')
    Run(args.adb + ['reboot'])
    WaitForSystem(args)
    # Previous -g will be invalidated after reboot if the package was not
    # privileged.
    InstallApk(args)
  else:
    logging.info('App is already privileged.')


def SetFactorySettings(args: InstallAsPrivAppArgs):
  if args.skip_factory_settings:
    return
  Run(args.adb +
      ['shell', 'settings', 'put', 'global', 'stay_on_while_plugged_in', '3'])


def LaunchApp(args: InstallAsPrivAppArgs):
  Run(args.adb + ['shell', 'am', 'start', args.package_name])


def DoMain(argv: List[str]):
  parser = MakeParser()
  args = InstallAsPrivAppArgs(**parser.parse_args(argv).__dict__)
  result = Run(
      ['aapt', 'dump', 'badging', str(args.apk_path)], stdout=subprocess.PIPE)
  apk_info = result.stdout
  args.package_name = ParsePackageName(apk_info)
  logging.info('package_name="%s"', args.package_name)
  args.permission_path = (
      args.apk_path.parent / f'privapp-permissions-{args.dir_app_name}.xml')
  logging.info('permission_path="%s"', args.permission_path)
  GeneratePermissionFile(args, apk_info)
  if args.target is not None:
    Run(['adb', 'connect', args.target])
  UnInstallPrevious(args)
  Install(args)
  SetFactorySettings(args)
  LaunchApp(args)


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  DoMain(sys.argv[1:])
