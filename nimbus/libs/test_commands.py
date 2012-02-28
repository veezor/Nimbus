#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import mock
import types
import unittest

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'

from nimbus.libs import commands
from nimbus.shared.middlewares import LogSetup

LogSetup()

class SystemProcessTest(unittest.TestCase):


    def setUp(self):
        self.patch_settings = mock.patch("nimbus.libs.commands.settings")
        self.mock_settings = self.patch_settings.start()
        self.mock_settings.INSTALLED_APPS = ['nimbus.testapp']

        self.patch_import = mock.patch("__builtin__.__import__")
        self.mock_import = self.patch_import.start()
        self.test_module = types.ModuleType("test_commands")
        self.mock_import.return_value = self.test_module

        #patching order is relevant


    def test_decorator(self):
        @commands.command("--test-command")
        def command(*args):
            pass

        self.assertTrue( hasattr(command, "__command_name__") )
        self.assertEqual( command.__command_name__, "--test-command")


    def test_get_app_command_module(self):
        commands_ = commands.Commands()
        module = commands_._get_app_command_module("test_commands")
        self.assertEqual(module, self.test_module)
        self.mock_import.assert_called_with("test_commands.commands",
                                             fromlist="test_commands")


    def _make_commands(self):
        @commands.command("--test-command1")
        def command1(*args):
            """mydoc"""
            pass

        def notcommand(args):
            pass

        self.test_module.command1 = command1
        self.test_module.notcommand = notcommand
        self.func_commands = [command1]



    def test_get_commands_from_module(self):
        self._make_commands()
        commands_ = commands.Commands()
        lst_commands = commands_._get_commands_from_module(self.test_module)
        self.assertEqual(lst_commands, self.func_commands)



    def test_get_commands_from_app(self):
        self._make_commands()
        commands_ = commands.Commands()
        lst_commands = commands_._get_commands_from_app("new_test_commands")
        self.mock_import.assert_called_with("new_test_commands.commands",
                                            fromlist="new_test_commands")
        self.assertEqual(lst_commands, self.func_commands)


    def test_list_apps(self):
        commands_ = commands.Commands()
        self.assertEqual( commands_._list_apps(), ["nimbus.testapp"])


    def test_update_commands(self):
        commands_ = commands.Commands()
        self._make_commands()
        commands_._update_commands(self.func_commands)
        self.assertEqual( commands_.commands.values(), self.func_commands )
        self.assertEqual( commands_.commands.keys(), ["--test-command1"] )
        self.assertRaises( commands.CommandNameError, commands_._update_commands, self.func_commands )


    def test_load_commands(self):
        commands_ = commands.Commands()
        self.assertEqual( commands_.commands.values(), [] )
        self.assertEqual( commands_.commands.keys(), [] )
        self._make_commands()
        commands_._load_commands()
        self.assertEqual( commands_.commands.values(), self.func_commands )
        self.assertEqual( commands_.commands.keys(), ["--test-command1"] )



    def test_list_commands(self):

        commands_ = commands.Commands()
        self.assertEqual( commands_.list_commands(), [])
        self._make_commands()
        commands_._load_commands()
        self.assertEqual( commands_.list_commands(), ["--test-command1"])



    def test_get_usage(self):
        mock_ = mock.Mock()
        sys.stdout = mock_
        self._make_commands()
        commands_ = commands.Commands()
        commands_.get_usage()
        sys.stdout = sys.__stdout__
        mock_.assert_has_calls( [mock.call.write('\t'),
                             mock.call.write('--test-command1'),
                             mock.call.write('\n'),
                             mock.call.write('\t\t'),
                             mock.call.write('mydoc'),
                             mock.call.write('\n')])


    def test_run_command(self):
        self.test_module.command1 = mock.Mock(spec=types.FunctionType)
        self.test_module.command1.__command_name__ = "mock_command"
        commands_ = commands.Commands()
        commands_.run_command("mock_command", "test_param")
        self.test_module.command1.assert_called_with("test_param")


    def test_run_command_missing(self):
        argv = sys.argv
        sys.argv = ["python"]
        commands_ = commands.Commands()
        self.assertRaises( commands.CommandMissing, commands_.run)


    def test_run_command_not_found(self):
        sys.argv = ["python", "command_not_found"]
        commands_ = commands.Commands()
        self.assertRaises( commands.CommandNotFound, commands_.run)


    def test_run_parameter_missing(self):
        @commands.command("test")
        def cmd(arg):
            pass

        self.test_module.cmd = cmd

        commands_ = commands.Commands()
        sys.argv = ["python", "test"]
        self.assertRaises( commands.ParameterMissing, commands_.run)


    def test_run_ok(self):
        self.test_module.command1 = mock.Mock(spec=types.FunctionType)
        self.test_module.command1.__command_name__ = "mock_command"
        commands_ = commands.Commands()
        sys.argv = ["python", "mock_command", "test_param"]
        commands_.run()
        self.test_module.command1.assert_called_with("test_param")


    def tearDown(self):
        self.patch_import.stop()
        self.patch_settings.stop()




if __name__ == "__main__":
    unittest.main()

