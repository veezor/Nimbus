#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import types
from django.conf import settings


class CommandNameError(Exception):
    pass


def command(name):

    def inner(function):
        function.__command_name__ = name
        return function

    return inner


class Commands(object):



    def __init__(self):
        self.commands = {}
        self._load_commands()


    def _get_app_command_module(self, appname):
        module = __import__(appname + ".commands")
        return module


    def _get_commands_from_module(self, module):
        items_name = [ i for i in dir(module) if not i.startswith('_') ]
        commands = []

        for item_name in list(items_name):
            item_obj = getattr(module, item_name)
            if isinstance(item_obj, types.FunctionType)\
               and hasattr(item_obj, "__command_name__"):
                commands.append(item_obj)

        return commands


    def _get_commands_from_app(self, app):
        module = self._get_app_command_module(app)
        return self._get_commands_from_module(module)


    def _list_apps(self):
        return [ app for app in settings.INSTALLED_APPS if app.startswith('nimbus.') ]


    def _update_commands(self, commands):
        for command in commands:
            name = command.__command_name__
            if not name in self.commands:
                self.commands[name] = command
            else:
                raise CommandNameError('command name duplicated')


    def _load_commands(self):
        apps = self._list_apps()
        for app in apps:
            commands = self._get_commands_from_app(app)
            self._update_commands(commands)


    def list_commands(self):
        return self.commands.keys()


    def run_command(self, command_name, *args):
        command = self.commands[command_name]
        command(*args)


    def run(self):
        args = list(sys.argv)
        nimbus = args.pop(0)
        command = args.pop(0)
        self.run_command(command, *args)
