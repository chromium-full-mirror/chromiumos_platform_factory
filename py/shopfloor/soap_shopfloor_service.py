# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Implementation of ChromeOS Factory Soap Shopfloor Service"""

import logging
import ssl
from typing import Optional

import spyne
from spyne.protocol import soap
from spyne.server import wsgi


KEY_SERIAL_NUMBER = 'serials.serial_number'
KEY_MLB_SERIAL_NUMBER = 'serials.mlb_serial_number'

SHOPFLOOR_TNS = 'spyne.shopfloor.soap'


class FactoryDeviceData(spyne.ComplexModel):
  __namespace__ = SHOPFLOOR_TNS
  _type_info = {
      'hwid': spyne.String,
      'factory.start_SMT': spyne.Boolean,
      'factory.end_SMT': spyne.Boolean,
      'factory.start_FAT': spyne.Boolean,
      'factory.end_FAT': spyne.Boolean,
      'factory.start_RUNIN': spyne.Boolean,
      'factory.end_RUNIN': spyne.Boolean,
      'factory.start_FFT': spyne.Boolean,
      'factory.end_FFT': spyne.Boolean,
      KEY_SERIAL_NUMBER: spyne.String,
      KEY_MLB_SERIAL_NUMBER: spyne.String,
  }


class EmptyFactoryDeviceData(spyne.ComplexModel):
  """A class to use as empty response.

  An empty dictionary decays to None when clients receive the response.

  A dictionary contains only one string decays to String when clients receive
  the response.

  Use two filler attributes to keep the response a dict.
  """
  __namespace__ = SHOPFLOOR_TNS
  _type_info = {
      'factory.filler1': spyne.String,
      'factory.filler2': spyne.String,
  }

  def __init__(self):
    super().__init__()
    for key in self._type_info:
      setattr(self, key, 'Unused filler.')


class FactoryDeviceInfo(spyne.ComplexModel):
  __namespace__ = SHOPFLOOR_TNS
  _type_info = {
      'vpd.ro.region': spyne.String,
      'vpd.rw.ubind_attribute': spyne.String,
      'vpd.rw.gbind_attribute': spyne.String,
  }

  def __init__(self, data):
    super().__init__()
    for key, value in data.items():
      setattr(self, key, value)


class SoapShopfloorService(spyne.ServiceBase):

  @spyne.rpc(_returns=spyne.String)
  def GetVersion(self):
    """Returns the version of supported protocol."""
    logging.info('GetVersion is called.')
    return '1.0'

  @spyne.rpc(FactoryDeviceData, spyne.String, _returns=EmptyFactoryDeviceData)
  def NotifyStart(self, data, station: str):
    """Notifies shopfloor backend that DUT is starting a manufacturing station.

    Args:
      data: A FactoryDeviceData instance.
      station: A string to indicate manufacturing station.

    Returns:
      A mapping in DeviceData format.
    """
    logging.info('DUT %s Entering station %s',
                 getattr(data, KEY_MLB_SERIAL_NUMBER, None), station)
    return EmptyFactoryDeviceData()

  @spyne.rpc(FactoryDeviceData, spyne.String, _returns=EmptyFactoryDeviceData)
  def NotifyEnd(self, data, station: str):
    """Notifies shopfloor backend that DUT has finished a manufacturing station.

    Args:
      data: A FactoryDeviceData instance.
      station: A string to indicate manufacturing station.

    Returns:
      A mapping in DeviceData format.
    """
    logging.info('DUT %s Leaving station %s',
                 getattr(data, KEY_MLB_SERIAL_NUMBER, None), station)
    return EmptyFactoryDeviceData()

  @spyne.rpc(FactoryDeviceData, spyne.String, _returns=EmptyFactoryDeviceData)
  def NotifyEvent(self, data, event):
    """Notifies shopfloor backend that the DUT has performed an event.

    Args:
      data: A FactoryDeviceData instance.
      event: A string to indicate manufacturing event.

    Returns:
      A mapping in FactoryDeviceData format.
    """
    assert event in ['Finalize', 'Refinalize']
    logging.info('DUT %s sending event %s',
                 getattr(data, KEY_MLB_SERIAL_NUMBER, None), event)
    return EmptyFactoryDeviceData()

  @spyne.rpc(FactoryDeviceData, _returns=FactoryDeviceInfo)
  def GetDeviceInfo(self, data):
    """Returns information about the device's expected configuration.

    Args:
      data: A FactoryDeviceData instance.

    Returns:
      A mapping in DeviceData format.
    """
    logging.info('DUT %s requesting device information',
                 getattr(data, KEY_MLB_SERIAL_NUMBER, None))
    # Empty string '' decays as None when the client receive the data so we use
    # some test string here.
    return FactoryDeviceInfo({
        'vpd.ro.region': 'us',
        'vpd.rw.ubind_attribute': 'test_ubind',
        'vpd.rw.gbind_attribute': 'test_gbind',
    })

  @spyne.rpc(spyne.String, spyne.String, spyne.String,
             _returns=EmptyFactoryDeviceData)
  def ActivateRegCode(self, ubind_attribute, gbind_attribute, hwid):
    """Notifies shopfloor backend that DUT has deployed a registration code.

    Args:
      ubind_attribute: A string for user registration code.
      gbind_attribute: A string for group registration code.
      hwid: A string for the HWID of the device.

    Returns:
      A mapping in DeviceData format.
    """
    logging.info('DUT <hwid=%s> requesting to activate regcode(u=%s,g=%s)',
                 hwid, ubind_attribute, gbind_attribute)
    return EmptyFactoryDeviceData()

  @spyne.rpc(FactoryDeviceData, spyne.String, spyne.String, spyne.String,
             _returns=EmptyFactoryDeviceData)
  def UpdateTestResult(self, data, test_id, status, details=None):
    """Sends the specified test result to shopfloor backend.

    Args:
      data: A FactoryDeviceData instance.
      test_id: A string as identifier of the given test.
      status: A string from TestState; one of PASSED, FAILED, SKIPPED, or
          FAILED_AND_WAIVED.
      details: (optional) A mapping to provide more details, including at least
          'error_message'.

    Returns:
      A mapping in DeviceData format. If 'action' is included, DUT software
      should follow the value to decide how to proceed.
    """
    logging.info('DUT %s updating test results for <%s> with status <%s> %s',
                 getattr(data, KEY_MLB_SERIAL_NUMBER, None), test_id, status,
                 details.get('error_message') if details else '')
    return EmptyFactoryDeviceData()


def RunAsSoapServer(address, port, use_https: bool,
                    context: Optional[ssl.SSLContext]):
  from wsgiref.simple_server import make_server
  application = spyne.Application([SoapShopfloorService], SHOPFLOOR_TNS,
                                  in_protocol=soap.Soap11(validator='lxml'),
                                  out_protocol=soap.Soap11())
  wsgi_application = wsgi.WsgiApplication(application)

  protocol = 'https' if use_https else 'http'

  logging.info('listening to %s://%s:%d', protocol, address, port)
  server = make_server(address, port, wsgi_application)  # type:ignore
  if use_https and context is not None:
    server.socket = context.wrap_socket(server.socket, server_side=True)
  logging.info("wsdl is at: %s://%s:%d/?wsdl", protocol, address, port)
  logging.info("Url to use in DOME: %s://%s:%d/?wsdl", protocol, address, port)
  server.serve_forever()
