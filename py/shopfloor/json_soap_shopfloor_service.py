# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Implementation of ChromeOS Factory Json Soap Shopfloor Service"""

import json
import logging

import spyne
from spyne.protocol import soap
from spyne.server import wsgi


KEY_SERIAL_NUMBER = 'serials.serial_number'
KEY_MLB_SERIAL_NUMBER = 'serials.mlb_serial_number'

SHOPFLOOR_TNS = 'spyne.shopfloor.soap'


class SoapShopfloorService(spyne.ServiceBase):

  @spyne.rpc(_returns=spyne.String)
  def GetVersion(self):
    """Returns the version of supported protocol."""
    logging.info('GetVersion is called.')
    return '1.0'

  @spyne.rpc(spyne.String, spyne.String, _returns=spyne.String)
  def NotifyStart(self, raw_data, station: str):
    """Notifies shopfloor backend that DUT is starting a manufacturing station.

    Args:
      raw_data: A json encoded FactoryDeviceData instance.
      station: A string to indicate manufacturing station.

    Returns:
      A mapping in DeviceData format.
    """
    data = json.loads(raw_data)
    logging.info('DUT %s Entering station %s', data.get(KEY_MLB_SERIAL_NUMBER),
                 station)
    return json.dumps({})

  @spyne.rpc(spyne.String, spyne.String, _returns=spyne.String)
  def NotifyEnd(self, raw_data, station: str):
    """Notifies shopfloor backend that DUT has finished a manufacturing station.

    Args:
      raw_data: A json encoded FactoryDeviceData instance.
      station: A string to indicate manufacturing station.

    Returns:
      A mapping in DeviceData format.
    """
    data = json.loads(raw_data)
    logging.info('DUT %s Leaving station %s', data.get(KEY_MLB_SERIAL_NUMBER),
                 station)
    return json.dumps({})

  @spyne.rpc(spyne.String, spyne.String, _returns=spyne.String)
  def NotifyEvent(self, raw_data, event):
    """Notifies shopfloor backend that the DUT has performed an event.

    Args:
      raw_data: A json encoded FactoryDeviceData instance.
      event: A string to indicate manufacturing event.

    Returns:
      A mapping in spyne.String format.
    """
    data = json.loads(raw_data)
    assert event in ['Finalize', 'Refinalize']
    logging.info('DUT %s sending event %s', data.get(KEY_MLB_SERIAL_NUMBER),
                 event)
    return json.dumps({})

  @spyne.rpc(spyne.String, _returns=spyne.String)
  def GetDeviceInfo(self, raw_data):
    """Returns information about the device's expected configuration.

    Args:
      raw_data: A json encoded FactoryDeviceData instance.

    Returns:
      A mapping in DeviceData format.
    """
    data = json.loads(raw_data)
    logging.info('DUT %s requesting device information',
                 data.get(KEY_MLB_SERIAL_NUMBER))
    # Empty string '' decays as None when the client receive the data so we use
    # some test string here.
    return json.dumps({
        'vpd.ro.region': 'us',
        'vpd.rw.ubind_attribute': 'test_ubind',
        'vpd.rw.gbind_attribute': 'test_gbind',
    })

  @spyne.rpc(spyne.String, spyne.String, spyne.String, _returns=spyne.String)
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
    return json.dumps({})

  @spyne.rpc(spyne.String, spyne.String, spyne.String, spyne.String,
             _returns=spyne.String)
  def UpdateTestResult(self, raw_data, test_id, status, details=None):
    """Sends the specified test result to shopfloor backend.

    Args:
      raw_data: A json encoded FactoryDeviceData instance.
      test_id: A string as identifier of the given test.
      status: A string from TestState; one of PASSED, FAILED, SKIPPED, or
          FAILED_AND_WAIVED.
      details: (optional) A mapping to provide more details, including at least
          'error_message'.

    Returns:
      A mapping in DeviceData format. If 'action' is included, DUT software
      should follow the value to decide how to proceed.
    """
    data = json.loads(raw_data)
    logging.info('DUT %s updating test results for <%s> with status <%s> %s',
                 data.get(KEY_MLB_SERIAL_NUMBER), test_id, status,
                 details.get('error_message') if details else '')
    return json.dumps({})


def RunAsSoapServer(address, port):
  from wsgiref.simple_server import make_server
  application = spyne.Application([SoapShopfloorService], SHOPFLOOR_TNS,
                                  in_protocol=soap.Soap11(validator='lxml'),
                                  out_protocol=soap.Soap11())
  wsgi_application = wsgi.WsgiApplication(application)

  logging.info('listening to http://%s:%d', address, port)
  server = make_server(address, port, wsgi_application)  # type:ignore
  logging.info("wsdl is at: http://%s:%d/?wsdl", address, port)
  logging.info("Url to use in DOME: json:http://%s:%d/?wsdl", address, port)
  server.serve_forever()
