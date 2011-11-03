#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import threading # FIX KeyError


sys.path.extend( ['/var/nimbus/deps/',
                  '/var/nimbus/deps/gunicorn-0.11.1-py2.6.egg/',
                  '/usr/lib/python2.6/dist-packages',
                  '/usr/lib/python2.6/lib-dynload',
                  '/usr/lib/python2.6/'] )

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'


from gunicorn.app.base import Application
from django.core.handlers.wsgi import WSGIHandler


from nimbus.libs import commands
from nimbus.shared.middlewares import LogSetup



class NimbusApplication(Application):

    def init(self, parser, opts, args):
        self.project_path = 'nimbus'
        self.settings_modname = "nimbus.settings"
        self.cfg.set("default_proc_name", self.settings_modname)
        self.cfg.set("timeout", 2592000)


    def load(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = self.settings_modname
        return WSGIHandler()



def run_server():
    NimbusApplication("%prog [OPTIONS] [SETTINGS_PATH]").run()


def main():
    LogSetup()
    try:
        commands.Commands().run()
    except commands.CommandMissing:
        run_server()
    except commands.CommandNotFound:
        print "Command not found"
        sys.exit(1)
    except commands.ParameterMissing, e:
        print e.args[0]
        sys.exit(1)


if __name__ == "__main__":
    main()
