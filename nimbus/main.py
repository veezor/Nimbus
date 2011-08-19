#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import getpass
import functools




sys.path.extend( ['/var/nimbus/deps/',
                  '/var/nimbus/deps/gunicorn-0.11.1-py2.6.egg/',
                  '/usr/lib/python2.6/dist-packages',
                  '/usr/lib/python2.6/lib-dynload',
                  '/usr/lib/python2.6/'] )

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'


from gunicorn.app.base import Application

from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from django.contrib.auth.models import User
from django.conf import settings

from nimbus.libs import offsite, graphsdata
from nimbus.shared import utils
from nimbus.libs.bacula import ( ReloadManager,
                                 ReloadManagerService,
                                 force_unlock_bacula_and_start)
from nimbus.config.models import Config
from nimbus.storages.models import Storage
from nimbus.computers.models import Computer
from nimbus.shared.middlewares import LogSetup
from nimbus.reports.models import send_email_report
from nimbus.security.models import register_administrative_nimbus_models




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

            register_administrative_nimbus_models()

            reload_manager = ReloadManager()
            reload_manager.force_reload()
        else:
            force_unlock_bacula_and_start()




    def update_graphs_data(self):
        graphs_data_manager = graphsdata.GraphDataManager()
        graphs_data_manager.update()


    def shell(self):
        call_command('shell')

    def run_server(self):
        NimbusApplication("%prog [OPTIONS] [SETTINGS_PATH]").run()


    def create_upload_requests(self):
        try:
            args = sys.argv[2]
            volumes = args.split('|')
            volumes = filter(None, volumes)
            volumes = offsite.get_volumes_abspath( volumes )
            manager = offsite.RemoteManager()

            for volume in volumes:
                manager.create_upload_request( volume )

            manager.generate_database_dump_upload_request()
            manager.process_pending_upload_requests()
        except IndexError, error:
            # not args.
            pass


    def upload_volumes(self):
        manager = offsite.RemoteManager()
        manager.process_pending_upload_requests()


    def delete_volumes(self):
        manager = offsite.RemoteManager()
        manager.process_pending_delete_requests()


    def change_password(self):

        while True:
            password = getpass.getpass("new password: ")
            confirm_password = getpass.getpass("confirm password: ")

            if password != confirm_password:
                print "password does not match"
                print
            else:
                user = User.objects.get(id=1)
                user.set_password(password)
                user.save()
                print "password changed"
                break


    def reload_manager_service(self):
        service = ReloadManagerService()
        service.run()

    def send_email_report(self):
        job_id =  int(sys.argv[2])
        send_email_report(job_id)

    def run(self):
        commands = {
            "--server-forever" : self.run_server,
            "--update-graphs-data" : self.update_graphs_data,
            "--upload-requests" : self.create_upload_requests,
            "--create-database" : self.create_database,
            "--upload-now" : self.upload_volumes,
            "--shell" : self.shell,
            "--delete-volumes" : self.delete_volumes,
            "--change-password" : self.change_password,
            "--start-reload-manager-service" : self.reload_manager_service,
            "--email-report": self.send_email_report
        }

        if len(sys.argv) > 1:
            try:
                commands[sys.argv[1]]()
            except KeyError, error:
                print "option not found"
                sys.exit(1)
        else:
            self.run_server()




def main():
    LogSetup()
    App().run()

if __name__ == "__main__":
    main()
