#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import types
from django.conf import settings


class CommandNameError(Exception):
    pass


class CommandNotFound(Exception):
    pass

class CommandMissing(Exception):
    pass


class ParameterMissing(Exception):
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
        app = appname.split('.')[-1]
        module = __import__(appname + ".commands", fromlist=app)
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
            try:
                commands = self._get_commands_from_app(app)
                self._update_commands(commands)
            except ImportError:
                pass


    def list_commands(self):
        return self.commands.keys()


    def get_usage(self):
        for name,command in self.commands.items():
            print "\t",name
            doc = command.__doc__
            if not doc is None:
                for line in doc.split('\n'):
                    print "\t"*2,line.strip()
            else:
                print "\t\tDocumentation not found"


    def run_command(self, command_name, *args):
        command = self.commands[command_name]
        command(*args)


    def run(self):
        args = list(sys.argv)
        nimbus = args.pop(0)
        try:
            command = args.pop(0)
        except IndexError:
            raise CommandMissing("type the command")
        try:
            self.run_command(command, *args)
        except KeyError:
            raise CommandNotFound("command '%s' not found" % command)
        except TypeError, e:
            raise ParameterMissing(e.args[0])
