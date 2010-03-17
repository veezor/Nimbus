#!/usr/bin/env python

import os, sys


sys.path.extend( [  "/var/nimbus/deps/",
                    "/var/lib/python-support/python2.5/", 
                    "/usr/lib/python2.5/",
                    "/usr/lib/python2.5/site-packages/",
                    "/usr/lib/python2.5/lib-dynload/"])

os.environ['DJANGO_SETTINGS_MODULE'] = 'backup_corporativo.settings'

from django.core.management import execute_manager
from django.contrib.auth.models import User
from django.core.servers.fastcgi import runfastcgi
from backup_corporativo import settings




if len(sys.argv) >= 2:
    execute_manager(settings)
    if sys.argv[1] == "syncdb":
        u = User(username = "teste", 
                 is_superuser=True,
                 email = "suporte@linconet.com.br")
        u.set_password("test")
        u.save()
else:
    runfastcgi(method="threaded", daemonize="false")

