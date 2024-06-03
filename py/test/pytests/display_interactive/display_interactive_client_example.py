# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Display interactive test client example.

Description
-----------
This script provides a client example to interact with the
DisplayInteractiveTest running on a target DUT (Device Under Test). It
uses XML-RPC for communication. This enables external test equipment or
scripts to control and evaluate display functionality.

Dependency
----------
- Uses an XML-RPC client for communication.
  - In this example, we use Python's `xmlrpc.client`.

Test Procedure
--------------
  1. Ensure the DisplayInteractiveTest is running on the DUT.
  2. Modify the IP address in this script to match the DUT's IP address.
  3. Run this script with the desired function and arguments.

Usage:
  python display_interactive_client_example.py -i <DUT's IP address>
  <function> <arguments>

Examples
--------
  1. Show a solid blue pattern:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1
     show_pattern css blue
     ```
  2. Get DUT serial number:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1 get_sn
     ```
  3. Set display brightness to 50%:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1
     set_display_brightness 0.5
     ```
  4. Mark the test as passed:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1
     report_test_result PASS
     ```
  5. Mark the test as failed with a reason:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1
     report_test_result FAIL 'Display has defects'
     ```
  6. Display a BMP image:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1
     show_pattern image my_image bmp
     ```
  7. Display a PNG image:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1
     show_pattern image my_image png
     ```
  8. Display a message string:
     ```bash
     python display_interactive_client_example.py -i 192.168.0.1
     show_pattern message 'Hello ChromeOS!'
     ```
"""

import argparse
import logging
import xmlrpc.client

# Setup logging level and format.
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


class Communication:
  """XML-RPC client for communicating with a device."""

  def __init__(self, ip_address: str, xmlrpc_port: int = 5566):
    """Initializes the XML-RPC client.

    Args:
        ip_address: The IP address of the device.
        xmlrpc_port: The XML-RPC listening port on the device.
    """
    self._proxy = xmlrpc.client.ServerProxy(
        f'http://{ip_address}:{xmlrpc_port}')

  def ShowPattern(self, pattern_type: str, pattern: str,
                  ext: str = 'png') -> None:
    """Shows the specified pattern on the device.

    Args:
        pattern_type: The type of pattern to show (e.g., 'css', 'image').
        pattern: The pattern itself (e.g., color name, image filename, message).
        ext: Extension of the image file (defaults to 'png').
    """
    self._proxy.ShowPattern(pattern_type, pattern, ext)

  def GetSerialNumber(self) -> None:
    """Print the serial number of the device."""
    serial_number = self._proxy.GetSerialNumber()
    print(serial_number)

  def ReportTestResult(self, result: str, reason: str = '') -> None:
    """Report the test result.

    Args:
        result: The test result ('PASS' or 'FAIL').
        reason: The reason for failure (optional).
    """
    self._proxy.JudgeTestResult(result, reason)

  def SetDisplayBrightness(self, arg_brightness: str) -> None:
    """Sets the display backlight brightness.

    Args:
        arg_brightness: The brightness level (0.0 - 1.0).

    Raises:
        ValueError: If brightness is not within the valid range.
    """
    try:
      brightness = float(arg_brightness)
    except ValueError:
      raise ValueError(
          f'Brightness must be a number; got {arg_brightness}') from None
    if not 0.0 <= brightness <= 1.0:
      raise ValueError('Brightness must be in the range [0.0, 1.0]')
    self._proxy.SetDisplayBrightness(brightness)


def main():
  parser = argparse.ArgumentParser(description='Device interaction client')
  parser.add_argument('-i', '--ip_address', required=True,
                      help='Device IP address')
  parser.add_argument('function', help='Function to call.')
  parser.add_argument('arguments', nargs='*', help='Function arguments')
  args = parser.parse_args()

  comm = Communication(args.ip_address)
  func = args.function
  arguments = args.arguments
  logging.info('Calling function: %s with arguments: %s', func, arguments)
  try:
    if func == 'show_pattern':
      comm.ShowPattern(*arguments)
    elif func == 'get_sn':
      comm.GetSerialNumber()
    elif func == 'set_display_brightness':
      comm.SetDisplayBrightness(*arguments)
    elif func == 'report_test_result':
      comm.ReportTestResult(*arguments)
    else:
      logging.error("Function '%s' not found.", func)
  except xmlrpc.client.Fault:
    pass


if __name__ == '__main__':
  main()
