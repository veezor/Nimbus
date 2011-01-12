#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
from os.path import join, dirname




sys.path.extend( ['/var/nimbus/deps/',
                  '/var/nimbus/deps/gunicorn-0.11.1-py2.6.egg/',
                  '/usr/lib/python2.6/dist-packages',
                  '/usr/lib/python2.6/lib-dynload',
                  '/usr/lib/python2.6/'] )

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'


from gunicorn.config import Config
from gunicorn.app.base import Application

from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from django.contrib.auth.models import User
from django.conf import settings

from nimbus.libs import offsite
from nimbus.shared import utils
from nimbus.config.models import Config
from nimbus.storages.models import Storage
from nimbus.computers.models import Computer
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


class App(object):

    def create_database(self):
        call_command('syncdb',verbosity=0,interactive=False)
        if len(User.objects.all()) == 0:
            u = User(username = "admin", 
                     is_superuser=True,
                     email = "suporte@veezor.com")
            u.set_password("admin")
            u.save()

            call_command('loaddata', settings.INITIALDATA_FILE)


            config = Config.get_instance()
            config.director_password = utils.random_password()
            config.save()

            storage = Storage.objects.get(id=1)
            storage.password =  utils.random_password()
            storage.save()

            computer = Computer.objects.get(id=1)
            computer.activate()


            call_command('loaddata', 
                          settings.ADMINISTRATIVE_MODELS_DATA_FILE)


    def shell(self):
        call_command('shell')

    def run_server(self):
        NimbusApplication("%prog [OPTIONS] [SETTINGS_PATH]").run()


    def create_upload_requests(self, args):
        volumes = args.split('|')
        volumes = offsite.get_volumes_abspath( volumes )
        manager = offsite.RemoteManager()
        for volume in volumes:
            manager.create_upload_request( volume )

        manager.generate_database_dump_upload_request()
        manager.process_pending_upload_requests()
        

    def upload_volumes(self):
        manager = offsite.RemoteManager()
        manager.process_pending_upload_requests()

    def run(self):
        if len(sys.argv) > 1:
            command = sys.argv[1]
        else:
            command = "--serve-forever"

        if command == "--create-database":
            self.create_database()
        elif command == "--upload-requests":
            try:
                self.create_upload_requests(sys.argv[2])
            except IndexError, error:
                pass
        elif command == "--upload-now":
            self.upload_volumes()
        elif command == "--shell":
            self.shell()
        else:
            self.run_server()


def main():
    LogSetup()
    App().run()

if __name__ == "__main__":
    main()
