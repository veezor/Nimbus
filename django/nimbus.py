#!/usr/bin/env python

import os, sys


ver = sys.version_info
pyversion = "%d.%d" % (ver[0],ver[1])
sys.path.extend( [  "/var/nimbus/deps/",
                    "/var/lib/python-support/python%s/" % pyversion,
                    "/usr/lib/python%s/" % pyversion,
                    "/usr/lib/python%s/site-packages/" % pyversion,
                    "/usr/lib/python%s/dist-packages/" % pyversion,
                    "/usr/lib/python%s/lib-dynload/"  % pyversion])

os.environ['DJANGO_SETTINGS_MODULE'] = 'backup_corporativo.settings'

from django.core.management import call_command
from django.contrib.auth.models import User
from django.core.servers.fastcgi import runfastcgi
from backup_corporativo import settings
from backup_corporativo.bkp import offsite

class App(object):

    def create_database(self):
        call_command('syncdb',verbosity=0,interactive=False)
        if len(User.objects.all()) == 0:
            u = User(username = "teste", 
                     is_superuser=True,
                     email = "suporte@linconet.com.br")
            u.set_password("teste")
            u.save()

    def run_server(self):
        runfastcgi(method="threaded", daemonize="false")


    def create_upload_requests(self, args):
        volumes = offsite.get_volumes_abspath( args )
        manager = offsite.RemoteManager()
        for volume in volumes:
            manager.create_upload_request( volume )
        

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
            self.create_upload_requests(sys.argv[1:])
        elif command == "--upload-now":
            self.upload_volumes()
        else:
            self.run_server()


def main():
    App().run()

if __name__ == "__main__":
    main()
