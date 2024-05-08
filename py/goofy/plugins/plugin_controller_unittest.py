#!/usr/bin/env python3

# Copyright 2016 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


import os
import unittest
from unittest import mock

from jsonrpclib import ProtocolError

from cros.factory.goofy import goofy
from cros.factory.goofy import goofy_server
from cros.factory.goofy.plugins import plugin
from cros.factory.goofy.plugins import plugin_controller
from cros.factory.test.env import goofy_proxy
from cros.factory.test.env import paths
from cros.factory.utils import type_utils


# pylint: disable=protected-access
class PluginControllerTest(unittest.TestCase):

  BASE_PLUGIN_MODULE = 'mock_plugin.mock_plugin'

  def setUp(self):
    self._goofy = mock.Mock(goofy.Goofy)
    self._goofy.goofy_server = mock.Mock(goofy_server.GoofyServer)

    # Load the base plugin class for test.
    # yapf: disable
    self._config = {'plugins': {self.BASE_PLUGIN_MODULE: {}}}  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

  def CreateController(self):
    with mock.patch('cros.factory.utils.config_utils.LoadConfig') as LoadConfig:
      LoadConfig.return_value = self._config
      controller = plugin_controller.PluginController('config', self._goofy)
      LoadConfig.assert_called_with('config', 'plugins', allow_inherit=True)
      return controller

  def testInit(self):
    controller = self.CreateController()
    self.assertCountEqual(
        list(controller._plugins),
        [self.BASE_PLUGIN_MODULE])
    self.assertCountEqual(controller._frontend_configs, [{
        'url': '/plugin/mock_plugin_mock_plugin/mock_plugin.html',
        'location': 'testlist',
        'iframe_id': 'mock_plugin-mock_plugin-iframe'
    }])
    self._goofy.goofy_server.RegisterPath.assert_called_once_with(
        '/plugin/mock_plugin_mock_plugin',
        os.path.join(paths.FACTORY_PYTHON_DIR, 'goofy', 'plugins',
                     'mock_plugin', 'static'))

  def testInitError(self):
    self._config['plugins']['not_exist_plugin.NotExistPlugin'] = {}
    controller = self.CreateController()
    self.assertCountEqual(
        list(controller._plugins),
        [self.BASE_PLUGIN_MODULE])

  def testStartAllPlugins(self):
    mock_plugin = mock.Mock(plugin.Plugin)
    controller = self.CreateController()
    controller._plugins['mock_plugin.MockPlugin'] = mock_plugin
    controller.StartAllPlugins()
    mock_plugin.Start.assert_called_with()

  def testStopAndDestroyAllPlugins(self):
    mock_plugin = mock.Mock(plugin.Plugin)
    controller = self.CreateController()
    controller._plugins['mock_plugin.MockPlugin'] = mock_plugin
    controller.StopAndDestroyAllPlugins()
    mock_plugin.Stop.assert_called_with()
    mock_plugin.Destroy.assert_called_with()

  def testPauseAndResumePluginByResource(self):
    mock_plugin = mock.Mock(plugin.Plugin)
    mock_plugin.used_resources = ['TEST_RESOURCE']
    controller = self.CreateController()
    controller._plugins['mock_plugin.MockPlugin'] = mock_plugin
    controller.PauseAndResumePluginByResource(set(['TEST_RESOURCE']))
    mock_plugin.Stop.assert_called_once_with()
    controller.PauseAndResumePluginByResource(set(['OTHER_RESOURCE']))
    mock_plugin.Start.assert_called_once_with()

  def testGetPluginInstance(self):
    controller = self.CreateController()
    self.assertIsNotNone(controller.GetPluginInstance(self.BASE_PLUGIN_MODULE))
    self.assertIsNone(controller.GetPluginInstance('not_exist_plugin'))

  def testGetPluginRPCPath(self):
    # pylint: disable=protected-access
    self.assertEqual(
        plugin_controller._GetPluginRPCPath('plugin'), '/plugin/plugin')

  @mock.patch.object(goofy_proxy, 'GetRPCProxy', autospec=True)
  def testGetPluginProxy(self, mock_get_rpc_proxy):
    mock_proxy = mock_get_rpc_proxy.return_value
    self.assertEqual(plugin_controller.GetPluginRPCProxy('plugin'), mock_proxy)
    mock_get_rpc_proxy.assert_called_once_with(None, None, '/plugin/plugin')
    mock_proxy.system.listMethods.assert_called_once_with()

  @mock.patch.object(plugin, 'GetPluginClass', autospec=True)
  def testGetPluginProxy_NoPluginClass(self, mock_get_plugin_class):
    mock_get_plugin_class.return_value = None
    with self.assertRaisesRegex(
        plugin_controller.PluginError,
        r"Failed to get plugin class of 'fake_plugin_name'\."):
      plugin_controller.GetPluginRPCProxy('fake_plugin_name')

  @mock.patch.object(plugin, 'GetPluginClass', autospec=True)
  @mock.patch.object(plugin, 'GetPluginNameFromClass', autospec=True)
  @mock.patch.object(goofy_proxy, 'GetRPCProxy', autospec=True)
  @mock.patch.object(type_utils, 'FlattenTuple', autospec=True)
  def testGetPluginProxy_PluginNotRunning(
      self, mock_flatten_tuple, mock_get_rpc_proxy, mock_get_plugin_name,
      mock_get_plugin_class):
    mock_get_plugin_class.return_value = 'fake_plugin_class'
    mock_get_plugin_name.return_value = 'fake_plugin_name'
    mock_proxy = mock_get_rpc_proxy.return_value
    mock_proxy.system.listMethods.side_effect = ProtocolError()
    mock_flatten_tuple.return_value = (404, )

    with self.assertRaisesRegex(
        plugin_controller.PluginError,
        r"The requested plugin 'fake_plugin_name' is not running\."):
      plugin_controller.GetPluginRPCProxy('fake_plugin_name')

  def testOnMenuItemClicked(self):
    controller = self.CreateController()
    mock_callback = mock.Mock()
    item = plugin.MenuItem('test', mock_callback)
    controller._menu_items[item.id] = item
    controller.OnMenuItemClicked(item.id)
    mock_callback.assert_called_once_with()

  def testGetPluginMenuItems(self):
    controller = self.CreateController()
    item = plugin.MenuItem('test', None)
    controller._menu_items[item.id] = item
    self.assertEqual([item], controller.GetPluginMenuItems())

  def testGetFrontendConfigs(self):
    controller = self.CreateController()
    url = '/plugin/mock_plugin_mock_plugin/mock_plugin.html'
    config = {
        'url': url,
        'location': 'testlist',
        'iframe_id': 'mock_plugin-mock_plugin-iframe'
    }
    controller._frontend_configs = [config]
    self.assertEqual([config], controller.GetFrontendConfigs())

if __name__ == '__main__':
  unittest.main()
