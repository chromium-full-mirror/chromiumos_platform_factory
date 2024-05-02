# Copyright 2013 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Common functions across different cellular modules."""

import logging
import re
import subprocess
from typing import Any, List

from cros.factory.test.rf.modem import Modem
from cros.factory.test import session
from cros.factory.utils import process_utils
from cros.factory.utils import type_utils

from cros.factory.external.py_lib import dbus


MODEM_STATUS = ['modem', 'status']
MODEM_IMEI_REG_EX = 'imei: ([0-9]*)'

MODEM_FIRMWARE_REG_EX = 'carrier: (.*)'
WCDMA_FIRMWARE = 'Generic UMTS'
CDMA_FIRMWARE = 'Verizon Wireless'

ENABLE_FACTORY_TEST_MODE_COMMAND = 'AT+CFUN=5'
DISABLE_FACTORY_TEST_MODE_COMMAND = 'AT+CFUN=1'

MM_PATH = '/org/freedesktop/ModemManager1'
MM_BUS_NAME = 'org.freedesktop.ModemManager1'
OM_IFACE_NAME = 'org.freedesktop.DBus.ObjectManager'
PROPERTIES_IFACE_NAME = 'org.freedesktop.DBus.Properties'
MODEM_IFACE_NAME = 'org.freedesktop.ModemManager1.Modem'
SIM_IFACE = 'org.freedesktop.ModemManager1.Sim'


def _GetDbusModem(bus=None):
  bus = bus or dbus.SystemBus()
  modem_manager_obj = bus.get_object(MM_BUS_NAME, MM_PATH)
  object_manager_iface = dbus.Interface(modem_manager_obj, OM_IFACE_NAME)
  modem_objs_info = object_manager_iface.GetManagedObjects()

  for modem_path, interfaces in modem_objs_info.items():
    if MODEM_IFACE_NAME not in interfaces:
      continue
    return bus.get_object(MM_BUS_NAME, modem_path)


def ProbeSimInfo(properties: List[str], bus=None) -> List[List[Any]]:
  """Returns sims properties according to fields.

  Args:
    properties: Requested properties. e.g. ['SimIdentifier', 'SimType', 'Imsi']
    bus: The dbus.

  Returns:
    A table of sim info. One row for each sim and the columns are the
    requested properties. If a requested property is absence then the value
    in the table is None.
  """
  bus = bus or dbus.SystemBus()  # type: ignore #TODO(b/338318729) Fixit!
  modem_obj = _GetDbusModem(bus)
  if modem_obj is None:
    return []
  properties_iface = dbus.Interface(modem_obj, PROPERTIES_IFACE_NAME)  # type: ignore #TODO(b/338318729) Fixit!
  sims = properties_iface.Get(MODEM_IFACE_NAME, 'SimSlots')

  ret = []
  for sim_path in sims:
    if sim_path == '/':
      continue
    sim_obj = bus.get_object(MM_BUS_NAME, sim_path)
    sim_properties_iface = dbus.Interface(sim_obj, PROPERTIES_IFACE_NAME)  # type: ignore #TODO(b/338318729) Fixit!

    data = []
    for name in properties:
      try:
        value = sim_properties_iface.Get(SIM_IFACE, name)
      except Exception:
        value = None
      data.append(value)
    ret.append(data)
  return ret


def ProbeModemInfo(properties: List[str], bus=None) -> List[Any]:
  """Returns the modem properties according to fields.

  Args:
    properties: Requested properties. e.g. ['EquipmentIdentifier', 'Model']
    bus: The dbus.

  Returns:
    A list of requested properties. If a requested property is absence then the
    value in the list is None.
  """
  bus = bus or dbus.SystemBus()  # type: ignore #TODO(b/338318729) Fixit!
  modem_obj = _GetDbusModem(bus)
  modem_properties_iface = dbus.Interface(modem_obj, PROPERTIES_IFACE_NAME)  # type: ignore #TODO(b/338318729) Fixit!
  data = []
  for name in properties:
    try:
      value = modem_properties_iface.Get(MODEM_IFACE_NAME, name)
    except Exception:
      value = None
    data.append(value)
  return data


def GetIMEI():
  """Gets the IMEI of current active modem."""
  stdout = process_utils.Spawn(
      MODEM_STATUS, read_stdout=True,
      log_stderr_on_error=True, check_call=True).stdout_data
  match = re.search(MODEM_IMEI_REG_EX, stdout)
  if not match:
    logging.info('Returned stdout %r', stdout)
    raise type_utils.Error('Cannot get IMEI from modem')
  return match.group(1)


def GetModemFirmware():
  """Returns the firmware info."""
  stdout = process_utils.Spawn(
      MODEM_STATUS, read_stdout=True,
      log_stderr_on_error=True, check_call=True).stdout_data
  match = re.search(MODEM_FIRMWARE_REG_EX, stdout)
  if not match:
    logging.info('Returned stdout %r', stdout)
    raise type_utils.Error('Cannot switching firmware')
  return match.group(1)


def SwitchModemFirmware(target):
  """Switch firmware if different from target.

  Returns:
    the firmware version before switching.
  """
  firmware_info = GetModemFirmware()
  session.console.info('Firmware version = %r', firmware_info)
  try:
    if firmware_info != target:
      session.console.info('Switching firmware to %r', target)
      stdout = process_utils.Spawn(
          ['modem', 'set-carrier', target], read_stdout=True,
          log_stderr_on_error=True, check_call=True).stdout_data
      logging.info('Output when switching to %r =\n%s', target, stdout)
  except subprocess.CalledProcessError:
    session.console.info('%r switching failed.', target)
    raise
  return firmware_info


def EnterFactoryMode(modem_path):
  """Enters factory mode of a modem.

  Args:
    modem_path: path to the modem.

  Returns:
    A Modem object that is ready in factory mode.

  Raises:
    subprocess.CalledProcessError: if switching fails.
  """
  session.console.info('Entering factory test mode(FTM)')
  modem = Modem(modem_path)
  modem.SendCommand(ENABLE_FACTORY_TEST_MODE_COMMAND)
  modem.ExpectLine('OK')
  session.console.info('Entered factory test mode')
  return modem


def ExitFactoryMode(modem):
  """Exits factory mode of a modem.

  Args:
    modem_path: path to the modem.
  """
  session.console.info('Exiting factory test mode(FTM)')
  modem.SendCommand(DISABLE_FACTORY_TEST_MODE_COMMAND)
  session.console.info('Exited factory test mode')
